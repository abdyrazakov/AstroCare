"""Doctor Layer: turns an Assessment into a short recommendation with caching.

Mutable-state note: ``DoctorLayer._cache`` (an ``OrderedDict`` used as a bounded
LRU/FIFO cache), ``DoctorLayer._in_flight`` (the set of cache keys with a synchronous call or background
upgrade already running) and ``DoctorLayer.stats`` (a plain counters dict) are the
ONLY mutable state in this project. Everything else -- ``Recommendation``, every
``Flag``/``Assessment``, every prompt and fallback string -- is an immutable value.
All three mutable structures are guarded by a single ``threading.Lock``.

Semantics implemented by ``recommend()`` (the "debounce + cache + timeout->fallback"
requirement):

1. ``enabled=False`` -> always the rule-based fallback, source ``"fallback"``, the
   client is never called.
2. Green with no active flags and no likely conditions -> the nominal fallback text,
   source ``"fallback"``, no LLM call (a known-nominal state needs no model opinion).
3. Identical ``(alert_level, flag_codes, condition_codes)`` seen before -> the cached
   text, source ``"cache"``. This is the debounce: the same picture never re-queries
   the LLM while it is cached.
4. On a cache miss, the cache key is atomically claimed in ``_in_flight`` (under
   ``_lock``) *before* the synchronous client call, and released once that call
   finishes -- unless it fails and hands the key off to a background upgrade
   thread (see 6). This closes the race where two concurrent callers with the
   same brand-new key would otherwise both call the LLM: whichever caller loses
   the claim takes the in-flight path in (5) instead.
5. If the key is already claimed -- either by another caller's in-progress sync
   call, or by a background upgrade thread (see 6) -- a miss returns the
   fallback text immediately, source ``"fallback"``, WITHOUT a synchronous
   client call and without starting a second thread (the 7B model can take well
   over the client's own timeout on CPU, so retrying it synchronously on every
   tick with unchanged flags would block for nothing). ``stats["inflight_skips"]``
   counts these.
6. Otherwise, the claiming caller makes one synchronous call to the client with
   its own default timeout. On success the (sanitised) text is cached, the claim
   is released, and the result is returned with source ``"llm"``. If that call
   raises ``OllamaError`` (including a timeout) -> the fallback text, source
   ``"fallback"``; if ``async_upgrade`` is on, the already-held claim is handed
   off to exactly one background daemon thread per cache key, which retries with
   a longer timeout and, on success, populates the cache (so the next identical
   assessment gets source ``"cache"``) and releases the claim; otherwise the
   claim is released immediately. Upgrade failures only increment a counter,
   never raise. Failure to start the thread also releases the claim. Unexpected
   synchronous exceptions propagate after releasing the claim.
7. The cache is bounded by ``max_cache`` entries, oldest evicted first.
"""

from __future__ import annotations

import re
import threading
from collections import OrderedDict
from dataclasses import dataclass
from typing import Literal, Protocol

from .fallback import build_fallback
from .ollama_client import OllamaError
from .prompts import SYSTEM_PROMPT, build_user_prompt

_WHITESPACE_RE = re.compile(r"\s+")

RecommendationSource = Literal["llm", "cache", "fallback"]

CacheKey = tuple[str, ...]


@dataclass(frozen=True)
class Recommendation:
    """Immutable result of ``DoctorLayer.recommend``."""

    text: str
    source: RecommendationSource


class _FlagLike(Protocol):
    code: str


class _AssessmentLike(Protocol):
    alert_level: str
    flags: tuple[_FlagLike, ...]

    def flag_codes(self) -> tuple[str, ...]: ...
class _ClientLike(Protocol):
    def generate(self, system: str, user: str, timeout_s: float | None = None) -> str: ...


def _condition_codes(assessment: _AssessmentLike) -> tuple[str, ...]:
    """Ranked condition codes when the assessment carries IMM-lite candidates."""
    getter = getattr(assessment, "condition_codes", None)
    if callable(getter):
        return tuple(getter())
    conditions = getattr(assessment, "likely_conditions", ())
    return tuple(condition.code for condition in conditions)


def _capability_statuses(assessment: _AssessmentLike) -> tuple[str, ...]:
    return tuple(
        str(getattr(condition, "onboard_capability", {}).get("status", "unknown"))
        for condition in getattr(assessment, "likely_conditions", ())
    )


class DoctorLayer:
    """Caches/debounces LLM recommendations and falls back to rule-based text."""

    def __init__(
        self,
        client: _ClientLike,
        *,
        enabled: bool = True,
        async_upgrade: bool = True,
        upgrade_timeout_s: float = 90.0,
        max_cache: int = 256,
        max_text_chars: int = 600,
    ) -> None:
        self._client = client
        self._enabled = enabled
        self._async_upgrade = async_upgrade
        self._upgrade_timeout_s = upgrade_timeout_s
        self._max_cache = max_cache
        self._max_text_chars = max_text_chars

        self._lock = threading.Lock()
        self._cache: OrderedDict[CacheKey, str] = OrderedDict()
        self._in_flight: set[CacheKey] = set()
        self.stats: dict[str, int] = {
            "llm_calls": 0,
            "cache_hits": 0,
            "fallbacks": 0,
            "upgrade_successes": 0,
            "upgrade_failures": 0,
            "inflight_skips": 0,
        }

    @staticmethod
    def cache_key(assessment: _AssessmentLike) -> CacheKey:
        """``(alert_level, flag_codes, condition_codes)`` -- identical pictures share a key."""
        conditions = _condition_codes(assessment)
        statuses = _capability_statuses(assessment)
        if statuses:
            return (assessment.alert_level, assessment.flag_codes(), conditions, statuses)
        return (assessment.alert_level, assessment.flag_codes(), conditions)

    def recommend(self, assessment: _AssessmentLike) -> Recommendation:
        """Return a recommendation for ``assessment``; see module docstring for rules."""
        if not self._enabled:
            return self._fallback_result(assessment)

        if assessment.alert_level == "green" and not assessment.flags:
            return self._fallback_result(assessment)

        key = self.cache_key(assessment)
        with self._lock:
            cached = self._read_cache_locked(key)
            if cached is not None:
                return Recommendation(text=cached, source="cache")
            claimed = key not in self._in_flight
            if claimed:
                self._in_flight.add(key)
        if not claimed:
            return self._inflight_skip_result(assessment)

        return self._query_llm_or_fallback(key, assessment)

    def ask(self, context: dict[str, object], question: str, timeout_s: float = 30.0) -> dict[str, str]:
        """Answer an interactive crew question without using the recommendation cache."""
        system = (
            "You are a flight-surgeon assistant. Answer in 3 to 6 plain-language sentences, "
            "without diagnosis or markdown. Ask one clarifying question when more than one "
            "condition is present. If the alert level is red, direct the crew to ground medical."
        )
        user = "Context: " + str(context) + "\nQuestion: " + question
        disclaimer = "Prototype decision support; follow mission procedures and ground medical direction."
        try:
            if not self._enabled:
                raise OllamaError("doctor disabled")
            text = self._sanitize(self._client.generate(system, user, timeout_s=timeout_s))
            if not text:
                raise OllamaError("empty response")
            return {"answer": text, "source": "llm", "disclaimer": disclaimer}
        except Exception:
            flags = ", ".join(str(item.get("code")) for item in context.get("flagDetails", []) if isinstance(item, dict))
            actions = " ".join(str(item) for item in context.get("doctorRecommendation", "").split("."))
            answer = f"Model unavailable. Current status: {context.get('alertLevel', 'unknown')}. Active flags: {flags or 'none'}. Suggested actions: {actions}".replace("  ", " ")
            return {"answer": answer, "source": "fallback", "disclaimer": disclaimer}

    # ----------------------------------------------------------------- internals

    def _fallback_result(self, assessment: _AssessmentLike) -> Recommendation:
        with self._lock:
            self.stats["fallbacks"] += 1
        return Recommendation(text=build_fallback(assessment), source="fallback")

    def _read_cache_locked(self, key: CacheKey) -> str | None:
        # Caller must hold self._lock, including the subsequent claim on a miss.
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)
        self.stats["cache_hits"] += 1
        return self._cache[key]

    def _inflight_skip_result(self, assessment: _AssessmentLike) -> Recommendation:
        with self._lock:
            self.stats["inflight_skips"] += 1
            self.stats["fallbacks"] += 1
        return Recommendation(text=build_fallback(assessment), source="fallback")

    def _query_llm_or_fallback(
        self, key: CacheKey, assessment: _AssessmentLike
    ) -> Recommendation:
        owned = True
        try:
            try:
                text = self._generate_and_sanitize(assessment, timeout_s=None)
            except OllamaError:
                result = self._fallback_result(assessment)
                if self._async_upgrade:
                    owned = not self._maybe_start_upgrade(key, assessment)
                return result
            with self._lock:
                self.stats["llm_calls"] += 1
                self._store_locked(key, text)
                self._in_flight.discard(key)
                owned = False
            return Recommendation(text=text, source="llm")
        finally:
            if owned:
                with self._lock:
                    self._in_flight.discard(key)

    def _generate_and_sanitize(
        self, assessment: _AssessmentLike, *, timeout_s: float | None
    ) -> str:
        raw = self._client.generate(
            SYSTEM_PROMPT, build_user_prompt(assessment), timeout_s=timeout_s
        )
        text = self._sanitize(raw)
        if not text:
            raise OllamaError("Ollama response was empty after sanitisation")
        return text

    def _sanitize(self, raw: str) -> str:
        collapsed = _WHITESPACE_RE.sub(" ", raw.strip()).strip()
        if len(collapsed) > self._max_text_chars:
            collapsed = collapsed[: self._max_text_chars].rstrip()
        return collapsed

    def _store_locked(self, key: CacheKey, text: str) -> None:
        # Caller must hold ``self._lock``.
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = text
        while len(self._cache) > self._max_cache:
            self._cache.popitem(last=False)

    def _maybe_start_upgrade(self, key: CacheKey, assessment: _AssessmentLike) -> bool:
        """Transfer the caller's existing claim to an upgrade thread if started."""
        try:
            thread = threading.Thread(
                target=self._run_upgrade, args=(key, assessment), daemon=True
            )
            thread.start()
        except Exception:
            with self._lock:
                self.stats["upgrade_failures"] += 1
            return False
        return True

    def _run_upgrade(self, key: CacheKey, assessment: _AssessmentLike) -> None:
        try:
            text = self._generate_and_sanitize(assessment, timeout_s=self._upgrade_timeout_s)
            with self._lock:
                self._store_locked(key, text)
                self.stats["upgrade_successes"] += 1
        except Exception:
            with self._lock:
                self.stats["upgrade_failures"] += 1
        finally:
            with self._lock:
                self._in_flight.discard(key)
