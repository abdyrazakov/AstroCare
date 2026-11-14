"""Lifestyle/operational flags: exercise, calories, sleep, mood."""

from __future__ import annotations

from astro_brain.contract import VitalsSample
from astro_brain.evidence import EVIDENCE_BY_CODE
from astro_brain.flags import Flag

# Operational cutoffs; source limitations are recorded in docs/EVIDENCE.md.
EXERCISE_DEFICIT_RATIO = 0.5
# JSC-63555 Energy intake operating bands; VERIFIED (docs/EVIDENCE.md).
CALORIC_RED_BAND_RATIO = 0.80
CALORIC_YELLOW_BAND_RATIO = 0.90
# Compatibility aliases retained for v0.2 imports.
CALORIC_LOW_RATIO = CALORIC_RED_BAND_RATIO
CALORIC_DEFICIT_RATIO = CALORIC_RED_BAND_RATIO
CALORIC_GREEN_RATIO = CALORIC_YELLOW_BAND_RATIO
SLEEP_DEFICIT_HOURS = 6.0
LOW_MOOD_MAX = 4


def _exercise_deficit_flag(sample: VitalsSample) -> Flag | None:
    if sample.exercise_minutes_today is None or sample.required_exercise_minutes is None:
        return None
    threshold = EXERCISE_DEFICIT_RATIO * sample.required_exercise_minutes
    if sample.exercise_minutes_today >= threshold:
        return None
    message = (
        f"Only {sample.exercise_minutes_today} min of exercise today; minimum is "
        f"{threshold:.0f} min ({EXERCISE_DEFICIT_RATIO:.0%} of the "
        f"{sample.required_exercise_minutes} min target)."
    )
    return Flag(
        code="EXERCISE_DEFICIT", evidence=EVIDENCE_BY_CODE["EXERCISE_DEFICIT"],
        severity="yellow",
        message=message,
        value=sample.exercise_minutes_today,
        threshold=threshold,
    )


def _caloric_flags(sample: VitalsSample) -> tuple[Flag, ...]:
    if sample.caloric_intake is None or sample.caloric_target is None:
        return ()
    ratio = sample.caloric_intake / sample.caloric_target
    if ratio < CALORIC_RED_BAND_RATIO:
        code, severity, band, threshold = "CALORIC_DEFICIT", "red", "red", CALORIC_RED_BAND_RATIO
    elif ratio < CALORIC_YELLOW_BAND_RATIO:
        code, severity, band, threshold = "CALORIC_LOW", "yellow", "yellow", CALORIC_YELLOW_BAND_RATIO
    else:
        return ()
    message = (
        f"Caloric intake is {ratio:.0%} of target ({band} NASA operating band); "
        f"threshold is {threshold:.0%} of {sample.caloric_target} kcal."
    )
    return (Flag(code=code, evidence=EVIDENCE_BY_CODE[code], severity=severity,
                 message=message, value=sample.caloric_intake,
                 threshold=threshold * sample.caloric_target),)


def _sleep_deficit_flag(sample: VitalsSample) -> Flag | None:
    if sample.sleep_hours is None:
        return None
    if sample.sleep_hours >= SLEEP_DEFICIT_HOURS:
        return None
    message = f"Only {sample.sleep_hours:g} h of sleep; minimum is {SLEEP_DEFICIT_HOURS:g} h."
    return Flag(
        code="SLEEP_DEFICIT", evidence=EVIDENCE_BY_CODE["SLEEP_DEFICIT"],
        severity="yellow",
        message=message,
        value=sample.sleep_hours,
        threshold=SLEEP_DEFICIT_HOURS,
    )


def _low_mood_flag(sample: VitalsSample) -> Flag | None:
    if sample.mood_score is None:
        return None
    if sample.mood_score > LOW_MOOD_MAX:
        return None
    message = f"Mood score {sample.mood_score} is at or below the low-mood threshold of {LOW_MOOD_MAX}."
    return Flag(
        code="LOW_MOOD", evidence=EVIDENCE_BY_CODE["LOW_MOOD"],
        severity="yellow",
        message=message,
        value=sample.mood_score,
        threshold=LOW_MOOD_MAX,
    )


def lifestyle_flags(sample: VitalsSample) -> tuple[Flag, ...]:
    """All active lifestyle flags for ``sample``, in a fixed order."""
    candidates = (
        _exercise_deficit_flag(sample),
        *_caloric_flags(sample),
        _sleep_deficit_flag(sample),
        _low_mood_flag(sample),
    )
    return tuple(flag for flag in candidates if flag is not None)
