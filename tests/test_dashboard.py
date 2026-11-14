"""Tests for astro_brain.dashboard: the owner-only self-check HTTP server.

Skipped entirely if astro_brain.scoring is not present yet (owned by a parallel
agent) -- Brain.process needs it, same guard as test_pipeline.py.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

import pytest

pytest.importorskip("astro_brain.scoring")

from astro_brain.dashboard import NO_DATA, StateStore, build_brain, build_server  # noqa: E402
from astro_brain.doctor.layer import DoctorLayer  # noqa: E402
from astro_brain.doctor.ollama_client import OllamaClient  # noqa: E402
from astro_brain.pipeline import Brain  # noqa: E402

NOMINAL_SAMPLE = {
    "timestamp": "2026-11-14T10:00:00Z",
    "astronaut_id": "ASTRO-01",
    "hr": 72,
    "spo2": 98,
    "bp": {"systolic": 120, "diastolic": 80},
    "temp_c": 36.8,
    "resp_rate": 14,
    "radiation_dose_rate": 20.5,
    "exercise_minutes_today": 90,
    "required_exercise_minutes": 120,
    "caloric_intake": 2600,
    "caloric_target": 2800,
    "sleep_hours": 7.5,
    "mood_score": 8,
}


def _offline_brain() -> Brain:
    return Brain(doctor=DoctorLayer(OllamaClient(), enabled=False))


@pytest.fixture()
def running_server():
    brain = _offline_brain()
    store = StateStore()
    server = build_server(0, brain, store)
    # Small poll_interval: shutdown() otherwise waits up to the default 0.5s
    # per test to notice the stop flag, which would blow the <3s test budget.
    thread = threading.Thread(target=server.serve_forever, args=(0.02,), daemon=True)
    thread.start()
    try:
        yield server
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def _url(server, path: str) -> str:
    return f"http://localhost:{server.server_port}{path}"


def _get(server, path: str):
    with urllib.request.urlopen(_url(server, path), timeout=2) as response:
        return response.status, response.headers.get("Content-Type"), response.read()


def _get_allow_error(server, path: str):
    try:
        return _get(server, path)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Content-Type"), exc.read()


def _post(server, path: str, body: bytes):
    request = urllib.request.Request(
        _url(server, path), data=body, method="POST", headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def test_root_before_any_data_is_plain_text_and_says_no_data_yet(running_server):
    # Act
    status, content_type, body = _get(running_server, "/")

    # Assert
    assert status == 200
    assert content_type == "text/plain; charset=utf-8"
    assert "no data yet" in body.decode("utf-8")


def test_ingest_valid_sample_returns_200_with_alert_level(running_server):
    # Act
    status, body = _post(running_server, "/ingest", json.dumps(NOMINAL_SAMPLE).encode("utf-8"))

    # Assert
    assert status == 200
    payload = json.loads(body)
    assert payload["alertLevel"] == "green"
    assert payload["astronautId"] == "ASTRO-01"


def test_ingest_missing_field_returns_400_naming_the_field(running_server):
    # Arrange
    bad_sample = dict(NOMINAL_SAMPLE)
    del bad_sample["hr"]

    # Act
    status, body = _post(running_server, "/ingest", json.dumps(bad_sample).encode("utf-8"))

    # Assert
    assert status == 400
    error = json.loads(body)["error"]
    assert "hr" in error


def test_ingest_garbage_body_returns_400(running_server):
    # Act
    status, body = _post(running_server, "/ingest", b"not json at all {")

    # Assert
    assert status == 400
    assert "error" in json.loads(body)


def test_state_after_ingest_equals_last_output(running_server):
    # Arrange
    _post(running_server, "/ingest", json.dumps(NOMINAL_SAMPLE).encode("utf-8"))

    # Act
    status, content_type, body = _get(running_server, "/state")

    # Assert
    assert status == 200
    assert content_type == "application/json"
    state = json.loads(body)
    assert state["astronautId"] == "ASTRO-01"
    assert state["alertLevel"] == "green"


def test_history_grows_with_each_ingest(running_server):
    # Act
    _post(running_server, "/ingest", json.dumps(NOMINAL_SAMPLE).encode("utf-8"))
    _post(running_server, "/ingest", json.dumps(NOMINAL_SAMPLE).encode("utf-8"))
    status, _, body = _get(running_server, "/history")

    # Assert
    assert status == 200
    history = json.loads(body)
    assert len(history) == 2


def test_unknown_path_returns_404(running_server):
    # Act
    status, content_type, body = _get_allow_error(running_server, "/unknown")

    # Assert
    assert status == 404
    assert "error" in json.loads(body)


def test_no_data_sentinel_is_read_only():
    # Act / Assert: NO_DATA is shared across request threads, so mutation must fail.
    with pytest.raises(TypeError):
        NO_DATA["status"] = "mutated"


def test_build_brain_offline_returns_disabled_doctor():
    # Act
    brain = build_brain(offline=True)

    # Assert
    assert brain._doctor._enabled is False


def test_build_brain_live_defers_to_env_driven_brain_default(monkeypatch):
    # Arrange: no ASTRO_DOCTOR_OFFLINE -> Brain()'s own default applies (enabled doctor).
    # Never calls .process()/.recommend()/.is_available(), so no network traffic happens.
    monkeypatch.delenv("ASTRO_DOCTOR_OFFLINE", raising=False)

    # Act
    brain = build_brain(offline=False)

    # Assert
    assert isinstance(brain, Brain)
    assert brain._doctor._enabled is True
