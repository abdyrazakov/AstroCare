"""Tests for astro_brain.conditions: the IMM-lite condition ranking."""

from __future__ import annotations

from pathlib import Path

import pytest

from astro_brain.conditions import (
    CONDITION_RULES,
    MAX_CONDITIONS,
    MIN_CONFIDENCE,
    likely_conditions,
)
from astro_brain.contract import parse_sample
from astro_brain.evidence import CONDITION_EVIDENCE_BY_CODE
from astro_brain.flags import Flag
from astro_brain.mock import nominal_raw
from astro_brain.scoring import assess

TIMESTAMP = "2026-11-14T10:00:00Z"


def _assess(**overrides):
    return assess(parse_sample({**nominal_raw(TIMESTAMP), **overrides}))


def test_nominal_sample_has_no_likely_conditions():
    assert _assess().condition_codes() == ()


@pytest.mark.parametrize(
    ("overrides", "condition"),
    [
        ({"bp": {"systolic": 88, "diastolic": 55}}, "HYPOVOLEMIA"),
        ({"hr": 135, "resp_rate": 26, "temp_c": 39.5, "spo2": 93}, "SEPSIS"),
        ({"spo2": 89}, "HYPOXEMIA"),
        ({"radiation_dose_rate": 1500.0}, "ACUTE_RADIATION_SYNDROME"),
        ({"hr": 125}, "CARDIAC_ARRHYTHMIA"),
        ({"sleep_hours": 4.0}, "SLEEP_DISORDER"),
        ({"mood_score": 3}, "DEPRESSION"),
        ({"caloric_intake": 1500}, "NUTRITIONAL_DEFICIT"),
    ],
)
def test_each_condition_is_reachable_from_its_own_signal(overrides, condition):
    result = _assess(**overrides)
    assert condition in result.condition_codes()


def test_low_heart_rate_supports_cardiac_arrhythmia():
    assert "CARDIAC_ARRHYTHMIA" in _assess(hr=35).condition_codes()


def test_sepsis_needs_more_than_a_single_fever_signal():
    result = _assess(temp_c=39.4)
    assert "TEMP_HIGH" in result.flag_codes()
    assert "SEPSIS" not in result.condition_codes()


def test_lone_mild_signal_below_confidence_floor_is_suppressed():
    # RESP_HIGH alone is too weak to support any condition.
    result = _assess(resp_rate=22)
    assert "RESP_HIGH" in result.flag_codes()
    assert result.likely_conditions == ()


def test_isolated_elevated_dose_rate_does_not_claim_radiation_syndrome():
    result = _assess(radiation_dose_rate=150.0)
    assert "RADIATION_ELEVATED" in result.flag_codes()
    assert "ACUTE_RADIATION_SYNDROME" not in result.condition_codes()


def test_conditions_are_capped_at_max_conditions():
    result = _assess(
        hr=135, resp_rate=26, temp_c=39.5, spo2=93, sleep_hours=3.0, mood_score=3,
        caloric_intake=500, radiation_dose_rate=1500.0,
    )
    assert 0 < len(result.likely_conditions) <= MAX_CONDITIONS


def test_conditions_are_sorted_by_confidence_descending():
    result = _assess(hr=135, resp_rate=26, temp_c=39.5, spo2=93)
    confidences = [condition.confidence for condition in result.likely_conditions]
    assert confidences == sorted(confidences, reverse=True)


def test_drivers_are_active_flags_and_declared_by_the_rule():
    result = _assess(hr=135, resp_rate=26, temp_c=39.5, spo2=93)
    active = set(result.flag_codes())
    weights = {rule.code: {code for code, _weight in rule.weights} for rule in CONDITION_RULES}
    for condition in result.likely_conditions:
        assert set(condition.drivers) <= active
        assert set(condition.drivers) <= weights[condition.code]


def test_confidence_is_bounded_and_rounded_in_the_output_shape():
    condition = _assess(hr=135, resp_rate=26, temp_c=39.5, spo2=93).likely_conditions[0]
    payload = condition.to_dict()
    assert 0.0 < condition.confidence <= 1.0
    assert payload["confidence"] == round(condition.confidence, 2)
    assert payload["confidence"] >= MIN_CONFIDENCE
    assert set(payload) == {"code", "label", "confidence", "drivers", "evidenceRef"}


def test_ranking_is_deterministic_for_the_same_flags():
    flags = (
        Flag("SPO2_LOW", "yellow", "m"),
        Flag("RESP_HIGH", "yellow", "m"),
        Flag("SLEEP_DEFICIT", "yellow", "m"),
    )
    first = likely_conditions(flags)
    second = likely_conditions(flags)
    assert [c.to_dict() for c in first] == [c.to_dict() for c in second]


def test_empty_flags_return_no_conditions():
    assert likely_conditions(()) == ()


def test_every_rule_has_an_evidence_reference():
    assert {rule.code for rule in CONDITION_RULES} == set(CONDITION_EVIDENCE_BY_CODE)
    assert all(reference.strip() for reference in CONDITION_EVIDENCE_BY_CODE.values())


def test_evidence_document_lists_every_condition_code():
    document = Path(__file__).resolve().parents[1] / "docs" / "EVIDENCE.md"
    rows = {
        line.split("|")[1].strip().strip("`")
        for line in document.read_text().splitlines()
        if line.startswith("|")
    }
    assert set(CONDITION_EVIDENCE_BY_CODE) <= rows
