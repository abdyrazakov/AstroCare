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
    exercise_minutes_today: int
    required_exercise_minutes: int
    caloric_intake: int
    caloric_target: int
    sleep_hours: float
    mood_score: int
    on_supplemental_o2: bool = False
    consciousness: Consciousness = "alert"
    noaa_s_scale: int | None = None


# (field, min, max) — inclusive integer ranges.
_INT_FIELDS: tuple[tuple[str, int, int], ...] = (
    ("hr", 0, 300),
    ("spo2", 0, 100),
    ("resp_rate", 0, 80),
    ("exercise_minutes_today", 0, 1440),
    ("required_exercise_minutes", 1, 1440),
    ("caloric_intake", 0, 20000),
    ("caloric_target", 1, 20000),
    ("mood_score", 1, 10),
)

# (field, min, max) — inclusive real-number ranges; ``None`` max means unbounded.
_NUMBER_FIELDS: tuple[tuple[str, float, float | None], ...] = (
    ("temp_c", 25.0, 45.0),
    ("radiation_dose_rate", 0.0, None),
    ("sleep_hours", 0.0, 24.0),
)

_BP_RANGE = (0, 300)
_NOAA_RANGE = (0, 5)


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


# --------------------------------------------------------------------------- entry point


def parse_sample(raw: object) -> VitalsSample:
    """Validate a raw JSON-decoded sample and return an immutable ``VitalsSample``.

    Raises ``ContractError`` naming the offending field on any violation.
    """
    if not isinstance(raw, Mapping):
        raise ContractError(f"sample must be a JSON object, got {_type_name(raw)}")

    ints = {name: _as_int(name, _require(raw, name), lo, hi) for name, lo, hi in _INT_FIELDS}
    numbers = {
        name: _as_number(name, _require(raw, name), lo, hi) for name, lo, hi in _NUMBER_FIELDS
    }

    return VitalsSample(
        timestamp=_as_non_empty_str("timestamp", _require(raw, "timestamp")),
        astronaut_id=_as_non_empty_str("astronaut_id", _require(raw, "astronaut_id")),
        bp=_parse_bp(_require(raw, "bp")),
        on_supplemental_o2=_as_bool("on_supplemental_o2", raw.get("on_supplemental_o2", False)),
        consciousness=_as_consciousness(raw.get("consciousness", "alert")),
        noaa_s_scale=_as_optional_noaa(raw.get("noaa_s_scale")),
        **ints,
        **numbers,
    )
