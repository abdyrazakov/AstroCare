"""Tests for astro_brain.pipeline: Brain.process end-to-end and to_output shape.

Skipped entirely if astro_brain.scoring is not present yet (owned by a parallel agent).
"""

from __future__ import annotations

import pytest

pytest.importorskip("astro_brain.scoring")

from astro_brain.contract import ContractError  # noqa: E402
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

RED_SAMPLE = {
    "timestamp": "2026-11-14T10:05:00Z",
    "astronaut_id": "ASTRO-02",
    "hr": 180,
    "spo2": 85,
    "bp": {"systolic": 70, "diastolic": 40},
    "temp_c": 35.0,
    "resp_rate": 30,
    "radiation_dose_rate": 1450.0,
    "exercise_minutes_today": 0,
    "required_exercise_minutes": 120,
    "caloric_intake": 500,
    "caloric_target": 2800,
    "sleep_hours": 2.0,
    "mood_score": 1,
    "consciousness": "altered",
}

CONTRACT_OUTPUT_KEYS = {
    "timestamp",
    "astronautId",
    "alertLevel",
    "news2Score",
    "activeFlags",
    "flagDetails",
    "doctorRecommendation",
    "doctorSource",
}


def _offline_brain() -> Brain:
    from astro_brain.doctor.layer import DoctorLayer
    from astro_brain.doctor.ollama_client import OllamaClient

    return Brain(doctor=DoctorLayer(OllamaClient(), enabled=False))


def test_nominal_sample_is_green_with_no_flags_and_fallback_source():
    # Arrange
    brain = _offline_brain()

    # Act
    output = brain.process(NOMINAL_SAMPLE)

    # Assert
    assert output["alertLevel"] == "green"
    assert output["activeFlags"] == []
    assert output["doctorSource"] == "fallback"
    assert set(output.keys()) == CONTRACT_OUTPUT_KEYS


def test_red_sample_has_red_alert_level_and_contract_shaped_output():
    # Arrange
    brain = _offline_brain()

    # Act
    output = brain.process(RED_SAMPLE)

    # Assert
    assert output["alertLevel"] == "red"
    assert len(output["activeFlags"]) > 0
    assert set(output.keys()) == CONTRACT_OUTPUT_KEYS
    assert output["astronautId"] == "ASTRO-02"
    assert output["timestamp"] == "2026-11-14T10:05:00Z"
    for detail in output["flagDetails"]:
        assert set(detail.keys()) == {"code", "severity", "message", "value", "threshold"}


def test_invalid_sample_raises_contract_error():
    # Arrange
    brain = _offline_brain()
    bad_sample = dict(NOMINAL_SAMPLE)
    del bad_sample["hr"]

    # Act / Assert
    with pytest.raises(ContractError):
        brain.process(bad_sample)


def test_env_offline_flag_builds_disabled_doctor_layer(monkeypatch):
    # Arrange
    monkeypatch.setenv("ASTRO_DOCTOR_OFFLINE", "1")

    # Act
    brain = Brain()
    output = brain.process(NOMINAL_SAMPLE)

    # Assert
    assert output["doctorSource"] == "fallback"
    assert brain._doctor._enabled is False
