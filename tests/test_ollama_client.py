"""Tests for astro_brain.doctor.ollama_client: OllamaClient over urllib, monkeypatched."""

from __future__ import annotations

import json
import socket
import urllib.error

import pytest

from astro_brain.doctor.ollama_client import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT_S,
    OllamaClient,
    OllamaError,
)


class _FakeResponse:
    """Minimal stand-in for the context-manager urlopen returns."""

    def __init__(self, body: bytes, status: int = 200) -> None:
        self._body = body
        self.status = status

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "_FakeResponse":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None


def _chat_body(content: str) -> bytes:
    return json.dumps({"message": {"content": content}}).encode("utf-8")


def test_defaults_are_the_documented_constants():
    # Arrange / Act
    client = OllamaClient()

    # Assert
    assert client.base_url == DEFAULT_BASE_URL == "http://localhost:11434"
    assert client.model == DEFAULT_MODEL == "qwen2.5:7b-instruct"
    assert DEFAULT_TIMEOUT_S == 3.0


def test_generate_returns_stripped_content_on_success(monkeypatch):
    # Arrange
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(req.data.decode("utf-8"))
        return _FakeResponse(_chat_body("  Move to the shielded area.  \n"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act
    result = client.generate("system prompt", "user prompt")

    # Assert
    assert result == "Move to the shielded area."
    assert captured["url"] == "http://localhost:11434/api/chat"
    assert captured["timeout"] == DEFAULT_TIMEOUT_S
    body = captured["body"]
    assert body["model"] == DEFAULT_MODEL
    assert body["stream"] is False
    assert body["options"] == {"temperature": 0.2, "num_predict": 220}
    assert body["messages"] == [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "user prompt"},
    ]


def test_generate_uses_explicit_timeout_override(monkeypatch):
    # Arrange
    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout=None):
        captured["timeout"] = timeout
        return _FakeResponse(_chat_body("ok"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act
    client.generate("s", "u", timeout_s=90.0)

    # Assert
    assert captured["timeout"] == 90.0


def test_generate_raises_ollama_error_on_http_error(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 500, "Internal Server Error", {}, None)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    with pytest.raises(OllamaError):
        client.generate("s", "u")


def test_generate_closes_http_error_response_before_raising(monkeypatch):
    # Arrange: a fake HTTPError that records whether close() was invoked, since the
    # error-response body (and its socket) otherwise stays open for as long as
    # OllamaError's __cause__ keeps the original exception reachable.
    class _RecordingHTTPError(urllib.error.HTTPError):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.closed = False

        def close(self):
            self.closed = True
            super().close()

    captured: dict[str, object] = {}

    def fake_urlopen(req, timeout=None):
        error = _RecordingHTTPError(req.full_url, 503, "Service Unavailable", {}, None)
        captured["error"] = error
        raise error

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act
    with pytest.raises(OllamaError):
        client.generate("s", "u")

    # Assert
    assert captured["error"].closed is True


def test_generate_raises_ollama_error_on_url_error(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    with pytest.raises(OllamaError):
        client.generate("s", "u")


def test_generate_raises_ollama_error_on_timeout(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        raise socket.timeout("timed out")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    with pytest.raises(OllamaError):
        client.generate("s", "u")


def test_generate_raises_ollama_error_on_malformed_json(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        return _FakeResponse(b"not json at all")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    with pytest.raises(OllamaError):
        client.generate("s", "u")


def test_generate_raises_ollama_error_on_missing_message_content(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        return _FakeResponse(json.dumps({"message": {}}).encode("utf-8"))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    with pytest.raises(OllamaError):
        client.generate("s", "u")


def test_generate_raises_ollama_error_on_empty_content(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        return _FakeResponse(_chat_body("   "))

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    with pytest.raises(OllamaError):
        client.generate("s", "u")


def test_is_available_true_on_success(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        assert timeout == 1.5
        return _FakeResponse(b"{}")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    assert client.is_available() is True


def test_is_available_false_on_any_error(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        raise urllib.error.URLError("nope")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    assert client.is_available() is False


def test_is_available_never_raises_on_unexpected_error(monkeypatch):
    # Arrange
    def fake_urlopen(req, timeout=None):
        raise ValueError("unexpected")

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    client = OllamaClient()

    # Act / Assert
    assert client.is_available() is False
