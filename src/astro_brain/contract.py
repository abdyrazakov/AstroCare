"""Input contract (data team -> brain): typed sample model and strict validation.

``parse_sample`` turns a raw JSON-decoded dict into an immutable ``VitalsSample``.
Every violation raises ``ContractError`` whose message names the offending field
and the reason (missing / wrong type / out of range). The brain never guesses.

Validation rules (see AGENTS.md for the human-readable table):
- booleans are never accepted as numbers (``bool`` is an ``int`` subclass in Python);
- floats with an integer value (``72.0``) are accepted for int fields, ``72.5`` is not;
- unknown extra keys are ignored for forward compatibility.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

Consciousness = Literal["alert", "altered"]
MissionPhase = Literal["PHASE_1_ACUTE_ADAPTATION", "PHASE_2_LONG_DURATION"]

_CONSCIOUSNESS_VALUES: tuple[str, ...] = ("alert", "altered")


class ContractError(ValueError):
    """Raised when a raw sample violates the input contract."""


@dataclass(frozen=True)
class BloodPressure:
    """Arterial blood pressure in mmHg."""

    systolic: int
    diastolic: int


@dataclass(frozen=True)
class VitalsSample:
    """One validated vitals sample. Field names equal the JSON keys."""

    timestamp: str
    astronaut_id: str
    hr: int
    spo2: int
    bp: BloodPressure
    temp_c: float
    resp_rate: int
    radiation_dose_rate: float
    on_supplemental_o2: bool = False
    consciousness: Consciousness = "alert"
    noaa_s_scale: int | None = None
    bfo_dose_30day_mgy_eq: float | None = None
    radiation_dose_career_msv: float | None = None
    exercise_minutes_today: int | None = None
    required_exercise_minutes: int | None = None
    caloric_intake: int | None = None
    caloric_target: int | None = None
    sleep_hours: float | None = None
    mood_score: int | None = None
    mission_day: int | None = None
    mission_phase: MissionPhase | None = None
    cabin_ppco2_mmhg: float | None = None
    iop_mmhg: float | None = None
    hrv_rmssd_ms: float | None = None
    pvt_slowest10_rt_ms: float | None = None
    medical_kit: tuple[str, ...] | None = None


# (field, min, max) — inclusive integer ranges.
_REQUIRED_INT_FIELDS: tuple[tuple[str, int, int], ...] = (
    ("hr", 0, 300),
    ("spo2", 0, 100),
    ("resp_rate", 0, 80),
)
_OPTIONAL_INT_FIELDS: tuple[tuple[str, int, int], ...] = (
    ("exercise_minutes_today", 0, 1440), ("required_exercise_minutes", 1, 1440),
    ("caloric_intake", 0, 20000), ("caloric_target", 1, 20000), ("mood_score", 1, 10),
    ("mission_day", 1, 3650),
)

# (field, min, max) — inclusive real-number ranges; ``None`` max means unbounded.
_REQUIRED_NUMBER_FIELDS: tuple[tuple[str, float, float | None], ...] = (
    ("temp_c", 25.0, 45.0),
    ("radiation_dose_rate", 0.0, None),
)
_OPTIONAL_NUMBER_FIELDS: tuple[tuple[str, float, float | None], ...] = (
    ("sleep_hours", 0.0, 24.0), ("cabin_ppco2_mmhg", 0.0, 20.0),
    ("iop_mmhg", 0.0, 60.0), ("hrv_rmssd_ms", 0.0, 300.0),
    ("pvt_slowest10_rt_ms", 100.0, 1000.0),
)

_OPTIONAL_DOSE_FIELDS = ("bfo_dose_30day_mgy_eq", "radiation_dose_career_msv")

_BP_RANGE = (0, 300)
_NOAA_RANGE = (0, 5)
_MISSION_PHASES = ("PHASE_1_ACUTE_ADAPTATION", "PHASE_2_LONG_DURATION")


# --------------------------------------------------------------------------- primitives


def _type_name(value: object) -> str:
    return type(value).__name__


def _require(raw: Mapping[str, object], field: str) -> object:
    if field not in raw:
        raise ContractError(f"'{field}' is missing (required field)")
    return raw[field]


def _as_non_empty_str(field: str, value: object) -> str:
    if not isinstance(value, str):
        raise ContractError(f"'{field}' must be a string, got {_type_name(value)}")
    if not value:
        raise ContractError(f"'{field}' must be a non-empty string")
    return value


def _as_bool(field: str, value: object) -> bool:
    if not isinstance(value, bool):
        raise ContractError(f"'{field}' must be a boolean, got {_type_name(value)}")
    return value


def _check_range(field: str, value: float, lo: float, hi: float | None) -> None:
    upper = "inf" if hi is None else hi
    if value < lo or (hi is not None and value > hi):
        raise ContractError(f"'{field}' out of range: {value!r} not within [{lo}, {upper}]")


def _as_int(field: str, value: object, lo: int, hi: int) -> int:
    if isinstance(value, bool):
        raise ContractError(f"'{field}' must be an integer, got bool")
    if isinstance(value, float):
        if not value.is_integer():
            raise ContractError(f"'{field}' must be an integer, got non-integer float {value!r}")
        value = int(value)
    if not isinstance(value, int):
        raise ContractError(f"'{field}' must be an integer, got {_type_name(value)}")
    _check_range(field, value, lo, hi)
    return value


def _as_number(field: str, value: object, lo: float, hi: float | None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"'{field}' must be a number, got {_type_name(value)}")
    if not math.isfinite(value):
        raise ContractError(f"'{field}' must be a finite number, got {value!r}")
    _check_range(field, value, lo, hi)
    return float(value)


# --------------------------------------------------------------------------- composite fields


def _parse_bp(value: object) -> BloodPressure:
    if not isinstance(value, Mapping):
        raise ContractError(f"'bp' must be an object {{systolic, diastolic}}, got {_type_name(value)}")
    lo, hi = _BP_RANGE
    systolic = _as_int("bp.systolic", _require(value, "systolic"), lo, hi)
    diastolic = _as_int("bp.diastolic", _require(value, "diastolic"), lo, hi)
    if diastolic > systolic:
        raise ContractError(
            f"'bp.diastolic' ({diastolic}) must not exceed 'bp.systolic' ({systolic})"
        )
    return BloodPressure(systolic=systolic, diastolic=diastolic)


def _as_consciousness(value: object) -> Consciousness:
    if not isinstance(value, str) or value not in _CONSCIOUSNESS_VALUES:
        allowed = " | ".join(repr(option) for option in _CONSCIOUSNESS_VALUES)
        raise ContractError(f"'consciousness' must be one of {allowed}, got {value!r}")
    return value  # type: ignore[return-value]


def _as_optional_noaa(value: object) -> int | None:
    if value is None:
        return None
    lo, hi = _NOAA_RANGE
    return _as_int("noaa_s_scale", value, lo, hi)


def _optional_ints(raw: Mapping[str, object]) -> dict[str, int | None]:
    return {name: None if raw.get(name) is None else _as_int(name, raw[name], lo, hi)
            for name, lo, hi in _OPTIONAL_INT_FIELDS}


def _optional_numbers(raw: Mapping[str, object]) -> dict[str, float | None]:
    return {name: None if raw.get(name) is None else _as_number(name, raw[name], lo, hi)
            for name, lo, hi in _OPTIONAL_NUMBER_FIELDS}


def _optional_pair(raw: Mapping[str, object], first: str, second: str) -> None:
    present = raw.get(first) is not None, raw.get(second) is not None
    if present[0] != present[1]:
        raise ContractError(f"'{first}' and '{second}' must be provided together")


def _medical_kit(value: object) -> tuple[str, ...] | None:
    if value is None:
        return None
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ContractError("'medical_kit' must be a list of non-empty strings or null")
    return tuple(value)


# --------------------------------------------------------------------------- entry point


def parse_sample(raw: object) -> VitalsSample:
    """Validate a raw JSON-decoded sample and return an immutable ``VitalsSample``.

    Raises ``ContractError`` naming the offending field on any violation.
    """
    if not isinstance(raw, Mapping):
        raise ContractError(f"sample must be a JSON object, got {_type_name(raw)}")

    ints = {name: _as_int(name, _require(raw, name), lo, hi) for name, lo, hi in _REQUIRED_INT_FIELDS}
    ints.update(_optional_ints(raw))
    numbers = {
        name: _as_number(name, _require(raw, name), lo, hi) for name, lo, hi in _REQUIRED_NUMBER_FIELDS
    }
    numbers.update(_optional_numbers(raw))
    optional_doses = {name: None if raw.get(name) is None else _as_number(name, raw[name], 0.0, None)
                      for name in _OPTIONAL_DOSE_FIELDS}
    _optional_pair(raw, "exercise_minutes_today", "required_exercise_minutes")
    _optional_pair(raw, "caloric_intake", "caloric_target")
    phase = raw.get("mission_phase")
    if phase is not None and (not isinstance(phase, str) or phase not in _MISSION_PHASES):
        raise ContractError(f"'mission_phase' must be one of {_MISSION_PHASES}, got {phase!r}")

    return VitalsSample(
        timestamp=_as_non_empty_str("timestamp", _require(raw, "timestamp")),
        astronaut_id=_as_non_empty_str("astronaut_id", _require(raw, "astronaut_id")),
        bp=_parse_bp(_require(raw, "bp")),
        on_supplemental_o2=_as_bool("on_supplemental_o2", raw.get("on_supplemental_o2", False)),
        consciousness=_as_consciousness(raw.get("consciousness", "alert")),
        noaa_s_scale=_as_optional_noaa(raw.get("noaa_s_scale")),
        mission_phase=phase, medical_kit=_medical_kit(raw.get("medical_kit")),
        **ints,
        **numbers,
        **optional_doses,
    )
