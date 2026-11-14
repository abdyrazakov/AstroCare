from __future__ import annotations

import pytest

from astro_brain.conditions import likely_conditions
from astro_brain.contract import parse_sample
from astro_brain.doctor.layer import DoctorLayer
from astro_brain.mock import apply_anomaly, nominal_raw
from astro_brain.pipeline import Brain
from astro_brain.scoring import assess


def _raw(name: str) -> dict[str, object]:
    return apply_anomaly(nominal_raw("2026-11-14T10:00:00Z"), name)


@pytest.mark.parametrize("name,condition", [("hypercapnia", "CO2_HEADACHE"), ("sans_like", "SANS")])
def test_new_conditions_are_reachable(name: str, condition: str) -> None:
    result = assess(parse_sample(_raw(name)))
    assert condition in result.condition_codes()


@pytest.mark.parametrize("phase", [None, "PHASE_1_ACUTE_ADAPTATION", "PHASE_2_LONG_DURATION"])
def test_phase_scoring_is_bounded(phase: str | None) -> None:
    result = likely_conditions(assess(parse_sample(_raw("sans_like"))).flags, phase)
    assert all(0 <= item.confidence <= 1 for item in result)


@pytest.mark.parametrize("name", ["hypercapnia", "sans_like", "sepsis_like", "hypovolemia_like"])
def test_condition_resource_shape(name: str) -> None:
    conditions = assess(parse_sample(_raw(name))).likely_conditions
    for condition in conditions:
        payload = condition.to_dict()
        assert "resources" in payload
        assert payload["onboardCapability"]["status"] in {"full", "partial", "none", "unknown", "no_rt"}


def test_hysteresis_sequence() -> None:
    brain = Brain(doctor=DoctorLayer(object(), enabled=False))
    outputs = []
    for rate in (103, 99, 100, 90):
        raw = nominal_raw("2026-11-14T10:00:00Z")
        raw["radiation_dose_rate"] = rate
        outputs.append(brain.process(raw))
    assert all("RADIATION_ELEVATED" in outputs[index]["activeFlags"] for index in range(3))
    assert outputs[3]["activeFlags"] == []


def test_reset_clears_hysteresis_memory() -> None:
    brain = Brain(doctor=DoctorLayer(object(), enabled=False))
    raw = nominal_raw("x")
    raw["radiation_dose_rate"] = 103
    brain.process(raw)
    brain.reset("ASTRO-01")
    raw["radiation_dose_rate"] = 99
    assert "RADIATION_ELEVATED" not in brain.process(raw)["activeFlags"]


def test_reset_all_clears_memory() -> None:
    brain = Brain(doctor=DoctorLayer(object(), enabled=False))
    raw = nominal_raw("x")
    raw["radiation_dose_rate"] = 103
    brain.process(raw)
    brain.reset()
    raw["radiation_dose_rate"] = 99
    assert "RADIATION_ELEVATED" not in brain.process(raw)["activeFlags"]


def test_phase_adjustment_is_reported() -> None:
    flags = assess(parse_sample(_raw("sans_like"))).flags
    conditions = likely_conditions(flags, "PHASE_2_LONG_DURATION")
    sans = next(item for item in conditions if item.code == "SANS")
    assert sans.phase_adjusted is True


@pytest.mark.parametrize("question", ["", "   "])
def test_empty_question_is_rejected_by_contract(question: str) -> None:
    assert not question.strip()


@pytest.mark.parametrize("name", ["hypercapnia", "sans_like", "sepsis_like", "hypovolemia_like", "tachycardia", "hypoxia", "fever", "sleep_deprivation", "low_mood", "caloric_deficit", "exercise_deficit", "radiation_storm", "radiation_elevated", "dose_30day_exceeded", "career_limit_exceeded"])
def test_mock_anomaly_is_parseable(name: str) -> None:
    sample = parse_sample(_raw(name))
    assert sample.astronaut_id == "ASTRO-01"


@pytest.mark.parametrize("name", ["hypercapnia", "sans_like"])
def test_new_flag_has_evidence(name: str) -> None:
    result = assess(parse_sample(_raw(name)))
    assert all(flag.evidence for flag in result.flags)
