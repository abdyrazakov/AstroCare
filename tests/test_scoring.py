"""Tests for astro_brain.scoring: the top-level pure ``assess`` entry point."""

from __future__ import annotations

import dataclasses

import pytest

from astro_brain.contract import BloodPressure
from astro_brain.scoring import Assessment, assess


def test_assess_on_nominal_sample_is_green_with_zero_flags(nominal_sample):
    result = assess(nominal_sample())
    assert isinstance(result, Assessment)
    assert result.alert_level == "green"
    assert result.news2_total == 0
    assert result.flags == ()
    assert result.flag_codes() == ()
    assert result.likely_conditions == ()
    assert result.condition_codes() == ()
    assert result.timestamp == "2026-11-14T10:00:00Z"
    assert result.astronaut_id == "ASTRO-01"


def test_assess_copies_timestamp_and_astronaut_id_unchanged(nominal_sample):
    sample = nominal_sample(timestamp="2026-01-01T00:00:00Z", astronaut_id="ASTRO-07")
    result = assess(sample)
    assert result.timestamp == "2026-01-01T00:00:00Z"
    assert result.astronaut_id == "ASTRO-07"


def test_assess_multi_anomaly_sample_is_red(nominal_sample):
    # NEWS2 total >= 7 (resp=8:3, hr=131:3, bp=90:3 -> total way over 7) plus radiation
    # critical and several lifestyle deficits: a severely degraded astronaut -> red.
    sample = dataclasses.replace(
        nominal_sample(
            resp_rate=8,
            hr=131,
            radiation_dose_rate=1500.0,
            exercise_minutes_today=1,
            caloric_intake=1,
            sleep_hours=1.0,
            mood_score=1,
        ),
        bp=BloodPressure(systolic=90, diastolic=50),
    )
    result = assess(sample)
    assert result.alert_level == "red"
    assert result.news2_total >= 7
    codes = result.flag_codes()
    assert "NEWS2_HIGH" in codes
    assert "RADIATION_CRITICAL" in codes
    assert "EXERCISE_DEFICIT" in codes
    assert "CALORIC_DEFICIT" in codes
    assert "SLEEP_DEFICIT" in codes
    assert "LOW_MOOD" in codes
    assert "HR_HIGH" in codes
    assert "BP_LOW" in codes
    assert "RESP_LOW" in codes


def test_assess_combines_vitals_radiation_and_lifestyle_flags_in_order(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=150.0, sleep_hours=2.0, hr=131)
    result = assess(sample)
    codes_in_order = [flag.code for flag in result.flags]
    # vitals_flags first (HR_HIGH, plus the NEWS2_MEDIUM aggregate since hr alone scores 3),
    # then radiation_flags, then lifestyle_flags.
    assert codes_in_order.index("HR_HIGH") < codes_in_order.index("RADIATION_ELEVATED")
    assert codes_in_order.index("RADIATION_ELEVATED") < codes_in_order.index("SLEEP_DEFICIT")


def test_flag_codes_are_sorted_and_unique(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=150.0, sleep_hours=2.0, hr=131, mood_score=1)
    result = assess(sample)
    codes = result.flag_codes()
    assert codes == tuple(sorted(codes))
    assert len(codes) == len(set(codes))


def test_assessment_ranks_imm_lite_conditions_for_a_degraded_sample(nominal_sample):
    sample = nominal_sample(hr=135, resp_rate=26, temp_c=39.5, spo2=93)
    result = assess(sample)
    codes = result.condition_codes()
    assert "SEPSIS" in codes
    assert "HYPOXEMIA" in codes
    assert codes == tuple(condition.code for condition in result.likely_conditions)


def test_assessment_is_immutable(nominal_sample):
    result = assess(nominal_sample())
    with pytest.raises(Exception):
        result.alert_level = "red"  # type: ignore[misc]
    with pytest.raises(Exception):
        result.flags = (1,)  # type: ignore[misc, assignment]


def test_assess_is_pure_same_input_same_output(nominal_sample):
    sample = nominal_sample(hr=131, radiation_dose_rate=200.0)
    first = assess(sample)
    second = assess(sample)
    assert first == second
