"""Small per-astronaut hold band for noisy threshold crossings."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from .flags import Flag, alert_level_from_flags

HYSTERESIS_FRACTION = 0.05


def _is_low(code: str) -> bool:
    return code.endswith("_LOW") or code.endswith("_DEFICIT") or code in {"LOW_MOOD", "CALORIC_LOW"}


def _value(sample: Any, code: str) -> float | None:
    if code.startswith("HR_"):
        return float(sample.hr)
    if code.startswith("SPO2_"):
        return float(sample.spo2)
    if code.startswith("BP_"):
        return float(sample.bp.systolic)
    if code.startswith("TEMP_"):
        return float(sample.temp_c)
    if code.startswith("RESP_"):
        return float(sample.resp_rate)
    if code.startswith("RADIATION_"):
        if "30DAY" in code:
            return sample.bfo_dose_30day_mgy_eq
        if "CAREER" in code:
            return sample.radiation_dose_career_msv
        return sample.radiation_dose_rate
    if code.startswith("CABIN_CO2"):
        return sample.cabin_ppco2_mmhg
    if code == "IOP_HIGH":
        return sample.iop_mmhg
    if code == "PVT_SLOW":
        return sample.pvt_slowest10_rt_ms
    if code == "SLEEP_DEFICIT":
        return sample.sleep_hours
    if code in {"CALORIC_LOW", "CALORIC_DEFICIT"}:
        return sample.caloric_intake
    if code == "EXERCISE_DEFICIT":
        return sample.exercise_minutes_today
    if code == "LOW_MOOD":
        return sample.mood_score
    return None


def apply_hysteresis(
    previous: Mapping[str, Flag],
    current: tuple[Flag, ...],
    sample: Any,
) -> tuple[Flag, ...]:
    """Hold a previous numeric flag while the current value remains within 5%."""
    result = list(current)
    current_codes = {flag.code for flag in current}
    for code, old in previous.items():
        if code in current_codes or not isinstance(old.threshold, (int, float)):
            continue
        value = _value(sample, code)
        if not isinstance(value, (int, float)):
            continue
        threshold = float(old.threshold)
        if _is_low(code):
            held = value <= threshold * (1 + HYSTERESIS_FRACTION)
        else:
            held = value >= threshold * (1 - HYSTERESIS_FRACTION)
        if held:
            result.append(replace(old, value=value, message=f"{old.message} (held: within 5% of threshold)"))
    return tuple(result)


def update_memory(memory: dict[str, Flag], flags: tuple[Flag, ...]) -> dict[str, Flag]:
    return {flag.code: flag for flag in flags}


def recompute(assessment: Any, flags: tuple[Flag, ...], conditions: tuple[Any, ...]) -> Any:
    return replace(assessment, flags=flags, alert_level=alert_level_from_flags(flags), likely_conditions=conditions)
