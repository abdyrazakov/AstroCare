"""Lifestyle/operational flags: exercise, calories, sleep, mood.

All four flags are yellow and independent of each other and of NEWS2.
"""

from __future__ import annotations

from astro_brain.contract import VitalsSample
from astro_brain.flags import Flag

EXERCISE_DEFICIT_RATIO = 0.5
CALORIC_DEFICIT_RATIO = 0.7
SLEEP_DEFICIT_HOURS = 6.0
LOW_MOOD_MAX = 4


def _exercise_deficit_flag(sample: VitalsSample) -> Flag | None:
    threshold = EXERCISE_DEFICIT_RATIO * sample.required_exercise_minutes
    if sample.exercise_minutes_today >= threshold:
        return None
    message = (
        f"Only {sample.exercise_minutes_today} min of exercise today; minimum is "
        f"{threshold:.0f} min ({EXERCISE_DEFICIT_RATIO:.0%} of the "
        f"{sample.required_exercise_minutes} min target)."
    )
    return Flag(
        code="EXERCISE_DEFICIT",
        severity="yellow",
        message=message,
        value=sample.exercise_minutes_today,
        threshold=threshold,
    )


def _caloric_deficit_flag(sample: VitalsSample) -> Flag | None:
    threshold = CALORIC_DEFICIT_RATIO * sample.caloric_target
    if sample.caloric_intake >= threshold:
        return None
    message = (
        f"Only {sample.caloric_intake} kcal consumed today; minimum is "
        f"{threshold:.0f} kcal ({CALORIC_DEFICIT_RATIO:.0%} of the "
        f"{sample.caloric_target} kcal target)."
    )
    return Flag(
        code="CALORIC_DEFICIT",
        severity="yellow",
        message=message,
        value=sample.caloric_intake,
        threshold=threshold,
    )


def _sleep_deficit_flag(sample: VitalsSample) -> Flag | None:
    if sample.sleep_hours >= SLEEP_DEFICIT_HOURS:
        return None
    message = f"Only {sample.sleep_hours:g} h of sleep; minimum is {SLEEP_DEFICIT_HOURS:g} h."
    return Flag(
        code="SLEEP_DEFICIT",
        severity="yellow",
        message=message,
        value=sample.sleep_hours,
        threshold=SLEEP_DEFICIT_HOURS,
    )


def _low_mood_flag(sample: VitalsSample) -> Flag | None:
    if sample.mood_score > LOW_MOOD_MAX:
        return None
    message = f"Mood score {sample.mood_score} is at or below the low-mood threshold of {LOW_MOOD_MAX}."
    return Flag(
        code="LOW_MOOD",
        severity="yellow",
        message=message,
        value=sample.mood_score,
        threshold=LOW_MOOD_MAX,
    )


def lifestyle_flags(sample: VitalsSample) -> tuple[Flag, ...]:
    """All active lifestyle flags for ``sample``, in a fixed order."""
    candidates = (
        _exercise_deficit_flag(sample),
        _caloric_deficit_flag(sample),
        _sleep_deficit_flag(sample),
        _low_mood_flag(sample),
    )
    return tuple(flag for flag in candidates if flag is not None)
