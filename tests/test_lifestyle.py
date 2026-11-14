"""Tests for astro_brain.lifestyle: exercise/caloric/sleep/mood flags."""

from __future__ import annotations

from astro_brain.lifestyle import (
    CALORIC_DEFICIT_RATIO,
    EXERCISE_DEFICIT_RATIO,
    LOW_MOOD_MAX,
    SLEEP_DEFICIT_HOURS,
    lifestyle_flags,
)


def test_nominal_sample_has_no_lifestyle_flags(nominal_sample):
    assert lifestyle_flags(nominal_sample()) == ()


# --------------------------------------------------------------------------- exercise


def test_exercise_exactly_at_half_required_is_not_deficit(nominal_sample):
    required = 150
    sample = nominal_sample(required_exercise_minutes=required, exercise_minutes_today=int(required * EXERCISE_DEFICIT_RATIO))
    codes = [flag.code for flag in lifestyle_flags(sample)]
    assert "EXERCISE_DEFICIT" not in codes


def test_exercise_just_below_half_required_is_deficit(nominal_sample):
    required = 150
    threshold = required * EXERCISE_DEFICIT_RATIO
    sample = nominal_sample(required_exercise_minutes=required, exercise_minutes_today=int(threshold) - 1)
    flags = lifestyle_flags(sample)
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == "EXERCISE_DEFICIT"
    assert flag.severity == "yellow"
    assert flag.value == int(threshold) - 1
    assert flag.threshold == threshold


# --------------------------------------------------------------------------- caloric


def test_caloric_exactly_at_seventy_percent_is_not_deficit(nominal_sample):
    target = 2800
    # round(), not int(): 2800 * 0.7 is 1959.9999999999998 in binary float, and the
    # implementation compares against that exact float, not the mathematical 1960.
    threshold = round(target * CALORIC_DEFICIT_RATIO)
    sample = nominal_sample(caloric_target=target, caloric_intake=threshold)
    codes = [flag.code for flag in lifestyle_flags(sample)]
    assert "CALORIC_DEFICIT" not in codes


def test_caloric_just_below_seventy_percent_is_deficit(nominal_sample):
    target = 2800
    threshold = target * CALORIC_DEFICIT_RATIO
    sample = nominal_sample(caloric_target=target, caloric_intake=int(threshold) - 1)
    flags = lifestyle_flags(sample)
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == "CALORIC_DEFICIT"
    assert flag.threshold == threshold


# --------------------------------------------------------------------------- sleep


def test_sleep_exactly_at_six_hours_is_not_deficit(nominal_sample):
    sample = nominal_sample(sleep_hours=SLEEP_DEFICIT_HOURS)
    codes = [flag.code for flag in lifestyle_flags(sample)]
    assert "SLEEP_DEFICIT" not in codes


def test_sleep_just_below_six_hours_is_deficit(nominal_sample):
    sample = nominal_sample(sleep_hours=SLEEP_DEFICIT_HOURS - 0.1)
    flags = lifestyle_flags(sample)
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == "SLEEP_DEFICIT"
    assert flag.severity == "yellow"
    assert flag.value == SLEEP_DEFICIT_HOURS - 0.1
    assert flag.threshold == SLEEP_DEFICIT_HOURS


# --------------------------------------------------------------------------- mood


def test_mood_just_above_low_threshold_is_not_low_mood(nominal_sample):
    sample = nominal_sample(mood_score=LOW_MOOD_MAX + 1)
    codes = [flag.code for flag in lifestyle_flags(sample)]
    assert "LOW_MOOD" not in codes


def test_mood_exactly_at_low_threshold_is_low_mood(nominal_sample):
    sample = nominal_sample(mood_score=LOW_MOOD_MAX)
    flags = lifestyle_flags(sample)
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == "LOW_MOOD"
    assert flag.severity == "yellow"
    assert flag.value == LOW_MOOD_MAX
    assert flag.threshold == LOW_MOOD_MAX


# --------------------------------------------------------------------------- combination


def test_multiple_lifestyle_deficits_all_reported(nominal_sample):
    sample = nominal_sample(
        exercise_minutes_today=1,
        caloric_intake=1,
        sleep_hours=1.0,
        mood_score=1,
    )
    codes = {flag.code for flag in lifestyle_flags(sample)}
    assert codes == {"EXERCISE_DEFICIT", "CALORIC_DEFICIT", "SLEEP_DEFICIT", "LOW_MOOD"}
    assert {flag.code: flag.severity for flag in lifestyle_flags(sample)}["CALORIC_DEFICIT"] == "red"
