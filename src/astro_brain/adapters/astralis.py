"""Pure mapping from ASTRALIS telemetry dictionaries to AstroBrain input."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from astro_brain.contract import ContractError


def _required(tick: Mapping[str, Any], key: str) -> Any:
    if key not in tick: raise ContractError(f"'{key}' is missing (simulator field)")
    return tick[key]


def stream_tick_to_input(tick: Mapping[str, Any], daily: Mapping[str, Any] | None = None,
                        *, required_exercise_minutes: int = 150) -> dict[str, Any]:
    """Map units and names; simulator radiation mSv/h becomes brain µSv/h (×1000)."""
    raw = {
        "timestamp": _required(tick, "timestamp"), "astronaut_id": _required(tick, "astronaut_id"),
        "hr": round(_required(tick, "hr")), "spo2": round(_required(tick, "spo2")),
        "bp": {"systolic": _required(tick, "systolic_bp"), "diastolic": _required(tick, "diastolic_bp")},
        "temp_c": _required(tick, "temp_c"), "resp_rate": round(_required(tick, "resp_rate")),
        "radiation_dose_rate": _required(tick, "radiation_dose_rate") * 1000,
        "mission_day": _required(tick, "mission_day"), "mission_phase": _required(tick, "mission_phase"),
        "cabin_ppco2_mmhg": _required(tick, "cabin_ppco2"), "iop_mmhg": _required(tick, "iop_mmhg"),
        "hrv_rmssd_ms": _required(tick, "hrv_rmssd"),
        "pvt_slowest10_rt_ms": _required(tick, "pvt_slowest10_rt"),
    }
    if daily is None:
        return raw
    raw["sleep_hours"] = daily.get("sleep_duration_h")
    raw["exercise_minutes_today"] = required_exercise_minutes if daily.get("ared_exercise_completed") else 0
    raw["required_exercise_minutes"] = required_exercise_minutes
    raw["radiation_dose_career_msv"] = daily.get("cumulative_radiation_msv")
    return raw
