"""Tests for astro_brain.doctor.layer: DoctorLayer cache / debounce / async-upgrade semantics."""

from __future__ import annotations

import threading

import pytest

from astro_brain.doctor.fallback import NOMINAL_TEXT, build_fallback
from astro_brain.doctor.layer import DoctorLayer
from astro_brain.doctor.ollama_client import OllamaError
from conftest import FakeFlag, make_assessment


class FakeClient:
    """Scripted stand-in for OllamaClient; records every call, never hits a network."""

    def __init__(self, script=None):
        self.calls: list[tuple[str, str, float | None]] = []
        self._script = list(script) if script is not None else []
        self._lock = threading.Lock()

    def generate(self, system, user, timeout_s=None):
        with self._lock:
            self.calls.append((system, user, timeout_s))
            behavior = self._script.pop(0) if self._script else OllamaError("no script left")
        if isinstance(behavior, Exception):
            raise behavior
        if callable(behavior):
            return behavior()
        return behavior

    def is_available(self) -> bool:
        return True

    @property
    def call_count(self) -> int:
        return len(self.calls)


@pytest.fixture
def upgrade_threads(monkeypatch):
    threads = []
    original = threading.Thread

    def track_thread(*args, **kwargs):
        thread = original(*args, **kwargs)
        threads.append(thread)
        return thread

    monkeypatch.setattr(threading, "Thread", track_thread)
    yield threads
    for thread in threads:
        thread.join(2)


def _join_upgrades(threads):
    assert len(threads) == 1
    threads[0].join(2)
    assert not threads[0].is_alive()


def _flagged(code: str = "LOW_MOOD") -> tuple[FakeFlag, ...]:
    return (FakeFlag(code=code, severity="yellow", message=f"{code} msg"),)




def test_stats_start_at_zero():
    layer = DoctorLayer(FakeClient())

    assert layer.stats == {
        "llm_calls": 0,
        "cache_hits": 0,
        "fallbacks": 0,
        "upgrade_successes": 0,
        "upgrade_failures": 0,
        "inflight_skips": 0,
    }


def test_cache_key_is_alert_level_flag_codes_and_condition_codes():
    assessment = make_assessment(
        alert_level="red",
        flags=(
            FakeFlag("NEWS2_HIGH", "red", "m"),
            FakeFlag("SLEEP_DEFICIT", "yellow", "m"),
        ),
    )

    assert DoctorLayer.cache_key(assessment) == ("red", assessment.flag_codes(), ())


def test_cache_key_separates_assessments_with_different_condition_codes():
    from conftest import FakeCondition

    first = make_assessment(
        alert_level="yellow",
        flags=_flagged(),
        likely_conditions=(FakeCondition("SEPSIS"),),
    )
    second = make_assessment(
        alert_level="yellow",
        flags=_flagged(),
        likely_conditions=(FakeCondition("HYPOXEMIA"),),
    )

    assert DoctorLayer.cache_key(first) != DoctorLayer.cache_key(second)




def test_disabled_layer_always_returns_fallback_and_never_touches_client():
    client = FakeClient()
    layer = DoctorLayer(client, enabled=False)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    rec = layer.recommend(assessment)

    assert rec.source == "fallback"
    assert rec.text == build_fallback(assessment)
    assert client.calls == []


def test_green_with_no_flags_returns_nominal_text_without_llm_call():
    client = FakeClient()
    layer = DoctorLayer(client)
    assessment = make_assessment(alert_level="green", flags=())

    rec = layer.recommend(assessment)

    assert rec.text == NOMINAL_TEXT
    assert rec.source == "fallback"
    assert client.calls == []




def test_cache_hit_returns_cached_text_and_does_not_call_llm_again():
    client = FakeClient(script=["Stay hydrated and rest."])
    layer = DoctorLayer(client)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    first = layer.recommend(assessment)
    second = layer.recommend(assessment)

    assert first.source == "llm"
    assert first.text == "Stay hydrated and rest."
    assert second.source == "cache"
    assert not layer._in_flight
    assert second.text == first.text
    assert client.call_count == 1
    assert layer.stats == {
        "llm_calls": 1,
        "cache_hits": 1,
        "fallbacks": 0,
        "upgrade_successes": 0,
        "upgrade_failures": 0,
        "inflight_skips": 0,
    }


def test_cache_miss_calls_llm_with_client_default_timeout():
    client = FakeClient(script=["Some advice."])
    layer = DoctorLayer(client)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    rec = layer.recommend(assessment)

    assert rec.source == "llm"
    assert not layer._in_flight
    assert client.calls == [(client.calls[0][0], client.calls[0][1], None)]


def test_sanitisation_collapses_whitespace():
    client = FakeClient(script=["  Line one.\n\n  Line   two.  "])
    layer = DoctorLayer(client)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    rec = layer.recommend(assessment)

    assert rec.text == "Line one. Line two."


def test_sanitisation_caps_text_length():
    client = FakeClient(script=["x" * 1000])
    layer = DoctorLayer(client, max_text_chars=50)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    rec = layer.recommend(assessment)

    assert rec.source == "llm"
    assert not layer._in_flight
    assert len(rec.text) <= 50


def test_sanitisation_empty_result_is_treated_as_failure():
    client = FakeClient(script=["   \n  "])
    layer = DoctorLayer(client, async_upgrade=False)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    rec = layer.recommend(assessment)

    assert rec.source == "fallback"
    assert rec.text == build_fallback(assessment)
    assert layer.stats["fallbacks"] == 1
    assert not layer._in_flight




def test_ollama_error_falls_back_without_async_upgrade():
    client = FakeClient(script=[OllamaError("boom")])
    layer = DoctorLayer(client, async_upgrade=False)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    rec = layer.recommend(assessment)

    assert rec.source == "fallback"
    assert rec.text == build_fallback(assessment)
    assert layer.stats["fallbacks"] == 1
    assert not layer._in_flight
    assert layer.stats["upgrade_successes"] == 0
    assert not layer._in_flight
    assert layer.stats["upgrade_failures"] == 0


def test_ollama_error_starts_async_upgrade_that_populates_cache_on_success(upgrade_threads):
    client = FakeClient(script=[OllamaError("boom"), "Upgraded advice text."])
    layer = DoctorLayer(client, upgrade_timeout_s=2.0)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    first = layer.recommend(assessment)
    assert first.source == "fallback"
    _join_upgrades(upgrade_threads)
    assert layer.stats["upgrade_successes"] == 1
    assert not layer._in_flight
    second = layer.recommend(assessment)

    assert second.source == "cache"
    assert not layer._in_flight
    assert second.text == "Upgraded advice text."
    assert client.call_count == 2
    assert client.calls[1][2] == 2.0
    assert layer.stats["upgrade_failures"] == 0


@pytest.mark.parametrize("error", [OllamaError("upgrade fails"), ValueError("unexpected")])
def test_async_upgrade_failure_increments_counter_and_never_raises(upgrade_threads, error):
    client = FakeClient(script=[OllamaError("sync miss"), error])
    layer = DoctorLayer(client, upgrade_timeout_s=1.0)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    layer.recommend(assessment)

    _join_upgrades(upgrade_threads)
    assert layer.stats["upgrade_failures"] == 1
    assert layer.stats["upgrade_successes"] == 0
    assert not layer._in_flight


def test_in_flight_guard_skips_sync_generate_and_starts_exactly_one_upgrade_thread(
    upgrade_threads,
):
    release = threading.Event()
    started = threading.Event()

    def blocking_upgrade() -> str:
        started.set()
        release.wait(timeout=2.0)
        return "Upgraded text."

    client = FakeClient(script=[OllamaError("first miss"), blocking_upgrade])
    layer = DoctorLayer(client, upgrade_timeout_s=2.0)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())

    first = layer.recommend(assessment)
    assert started.wait(timeout=2.0), "upgrade thread never started"
    calls_before_second = client.call_count
    second = layer.recommend(assessment)  # same key, upgrade still pending
    release.set()
    _join_upgrades(upgrade_threads)
    assert layer.stats["upgrade_successes"] == 1
    assert not layer._in_flight

    assert first.source == "fallback"
    assert second.source == "fallback"
    assert client.call_count == calls_before_second  # zero additional generate() calls
    upgrade_calls = [call for call in client.calls if call[2] == 2.0]
    assert len(upgrade_calls) == 1  # exactly one upgrade thread/call
    assert layer.stats["upgrade_failures"] == 0
    assert layer.stats["inflight_skips"] == 1




def test_cache_eviction_drops_oldest_entry_first():
    client = FakeClient(script=["r1", "r2", "r3", "r1-again"])
    layer = DoctorLayer(client, max_cache=2)
    a1 = make_assessment(alert_level="yellow", flags=_flagged("LOW_MOOD"))
    a2 = make_assessment(alert_level="yellow", flags=_flagged("SLEEP_DEFICIT"))
    a3 = make_assessment(alert_level="yellow", flags=_flagged("TEMP_HIGH"))

    layer.recommend(a1)
    layer.recommend(a2)
    layer.recommend(a3)  # evicts a1's entry (max_cache=2)
    replay = layer.recommend(a1)

    assert replay.source == "llm"
    assert replay.text == "r1-again"
    assert client.call_count == 4


def test_concurrent_new_key_has_only_one_sync_call():
    started, release = threading.Event(), threading.Event()
    results = []

    def blocking_generate():
        started.set()
        assert release.wait(2)
        return "Advice."

    client = FakeClient([blocking_generate, "Duplicate advice."])
    layer = DoctorLayer(client)
    assessment = make_assessment(alert_level="yellow", flags=_flagged())
    first = threading.Thread(target=lambda: results.append(layer.recommend(assessment)))
    second = threading.Thread(target=lambda: results.append(layer.recommend(assessment)))
    first.start()
    try:
        assert started.wait(2)
        assert layer.cache_key(assessment) in layer._in_flight
        second.start()
        second.join(2)
        assert not second.is_alive()
        assert results[0].source == "fallback"
        assert client.call_count == 1
        assert layer.stats["inflight_skips"] == 1
    finally:
        release.set()
        first.join(2)
        if second.ident is not None:
            second.join(2)
    assert not first.is_alive()
    assert results[1].source == "llm"
    assert not layer._in_flight


def test_unexpected_generate_error_releases_claim():
    assessment = make_assessment(alert_level="yellow", flags=_flagged())
    layer = DoctorLayer(FakeClient())

    def fail():
        assert layer.cache_key(assessment) in layer._in_flight
        raise ValueError("unexpected")

    layer._client = FakeClient([fail])
    with pytest.raises(ValueError, match="unexpected"):
        layer.recommend(assessment)
    assert not layer._in_flight


def test_upgrade_start_failure_releases_claim(monkeypatch):
    def fail_start(self):
        raise RuntimeError("cannot start thread")

    monkeypatch.setattr(threading.Thread, "start", fail_start)
    layer = DoctorLayer(FakeClient([OllamaError("sync failed")]))
    assessment = make_assessment(alert_level="yellow", flags=_flagged())
    assert layer.recommend(assessment).source == "fallback"
    assert layer.stats["upgrade_failures"] == 1
    assert not layer._in_flight
