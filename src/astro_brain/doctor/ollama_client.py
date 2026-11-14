"""Thin stdlib HTTP client for a local Ollama server.

Talks to the Ollama chat API (``POST /api/chat``) to turn an assessment into a short
recommendation, and offers a cheap liveness probe (``GET /api/tags``). Every failure
mode (connection refused, HTTP error, timeout, malformed JSON, empty content) is
normalised into a single ``OllamaError`` so callers never need to know about urllib.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Final

DEFAULT_BASE_URL: Final[str] = "http://localhost:11434"
DEFAULT_MODEL: Final[str] = "qwen2.5:7b-instruct"
DEFAULT_TIMEOUT_S: Final[float] = 3.0

_IS_AVAILABLE_TIMEOUT_S: Final[float] = 1.5
_TEMPERATURE: Final[float] = 0.2
_NUM_PREDICT: Final[int] = 220


class OllamaError(RuntimeError):
    """Raised whenever a chat request to Ollama cannot produce usable text."""


class OllamaClient:
    """Minimal client for the local Ollama chat API, stdlib only."""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        timeout_s: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_s = timeout_s

    def generate(self, system: str, user: str, timeout_s: float | None = None) -> str:
        """Ask the model for a reply to ``user`` given ``system``; return stripped text.

        Raises ``OllamaError`` on any network failure, non-2xx response, timeout,
        malformed JSON, or empty resulting content.
        """
        effective_timeout = self.timeout_s if timeout_s is None else timeout_s
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {"temperature": _TEMPERATURE, "num_predict": _NUM_PREDICT},
        }
        request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=effective_timeout) as response:
                raw_body = response.read()
        except (urllib.error.URLError, OSError) as exc:
            if isinstance(exc, urllib.error.HTTPError):
                # HTTPError keeps its error-response body (and the underlying
                # socket) open until closed; otherwise it leaks for as long as
                # OllamaError's __cause__ keeps this exception reachable, which
                # under background-upgrade retries can be a long time.
                exc.close()
            raise OllamaError(f"Ollama request to {self.base_url} failed: {exc}") from exc

        try:
            parsed = json.loads(raw_body)
        except json.JSONDecodeError as exc:
            raise OllamaError(f"Ollama returned malformed JSON: {exc}") from exc

        try:
            content = parsed["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise OllamaError("Ollama response is missing 'message.content'") from exc

        if not isinstance(content, str):
            raise OllamaError(f"Ollama 'message.content' must be a string, got {type(content)}")

        content = content.strip()
        if not content:
            raise OllamaError("Ollama returned empty content")
        return content

    def is_available(self) -> bool:
        """Cheap liveness probe against ``/api/tags``; never raises."""
        request = urllib.request.Request(f"{self.base_url}/api/tags", method="GET")
        try:
            with urllib.request.urlopen(request, timeout=_IS_AVAILABLE_TIMEOUT_S):
                return True
        except Exception:
            return False
