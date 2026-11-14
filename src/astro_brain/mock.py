"""Mock vitals data strictly matching the INPUT contract (AGENTS.md section 2).

Everything here produces raw JSON-shaped dicts (snake_case keys, ``bp`` as a
nested ``{"systolic", "diastolic"}`` object) -- the shape the data team hands
to ``Brain.process``, never the typed ``VitalsSample``.

``_NOMINAL_RAW`` mirrors the numeric values of ``tests/conftest.py``'s
``NOMINAL_DEFAULTS`` (required fields, plus optional cumulative doses) so "nominal" means the same thing
on both sides of the contract; if one changes, update the other.
"""

from __future__ import annotations

import random
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal

_BASE_TIMESTAMP = datetime(2026, 11, 14, 10, 0, 0, tzinfo=timezone.utc)
_STEP_SECONDS = 60
_MIN_ANOMALIES = 3
_MAX_ANOMALIES = 5

# Synthetic scenario values, not safety thresholds: docs/EVIDENCE.md (ASSUMPTION).
# Requested ISS-like 0.5 mSv/day * 30 days; career history is illustrative.
_NOMINAL_30DAY_MGY_EQ = 12.0
_NOMINAL_CAREER_MSV = 120.0
# Test stimuli above the limits documented at:
# https://www.nasa.gov/reference/4-0-human-performance/
_WARNING_30DAY_MGY_EQ = 150.0
_EXCEEDED_30DAY_MGY_EQ = 260.0
_EXCEEDED_CAREER_MSV = 660.0
_CAREER_WARNING_MSV = 350.0

# Required values match tests/conftest.py; optional cumulative doses are synthetic.
_NOMINAL_RAW: dict[str, Any] = {
    "hr": 68,
    "spo2": 98,
    "bp": {"systolic": 118, "diastolic": 76},
    "temp_c": 36.7,
    "resp_rate": 15,
    "radiation_dose_rate": 20.0,
    "bfo_dose_30day_mgy_eq": _NOMINAL_30DAY_MGY_EQ,
    "radiation_dose_career_msv": _NOMINAL_CAREER_MSV,
    "exercise_minutes_today": 120,
    "required_exercise_minutes": 150,
    "caloric_intake": 2600,
    "caloric_target": 2800,
    "sleep_hours": 7.5,
    "mood_score": 8,
    "medical_kit": [
        "ORAL_REHYDRATION_SALTS", "IV_ACCESS_KIT", "THERMOMETER",
        "ANTIBIOTICS_BROAD_SPECTRUM", "PULSE_OXIMETER", "SUPPLEMENTAL_O2",
        "ANTIEMETICS", "STORM_SHELTER", "DOSIMETER", "ECG_MONITOR",
        "BETA_BLOCKER", "NUTRITION_SUPPLEMENTS",
    ],
}


def nominal_raw(timestamp: str, astronaut_id: str = "ASTRO-01") -> dict[str, Any]:
    """A fresh nominal (all-green) raw input-contract sample for ``timestamp``."""
    return {
        "timestamp": timestamp,
        "astronaut_id": astronaut_id,
        **{key: (dict(value) if isinstance(value, dict) else value) for key, value in _NOMINAL_RAW.items()},
    }


@dataclass(frozen=True)
class Anomaly:
    """One named deviation from nominal, with the clinical outcome it must produce."""

    name: str
    overrides: Mapping[str, Any]
    expected_level: Literal["yellow", "red"]
    expected_codes: frozenset[str]
    expected_conditions: frozenset[str] = frozenset()


def _anomaly(
    name: str,
    overrides: Mapping[str, Any],
    level: Literal["yellow", "red"],
    *codes: str,
    conditions: tuple[str, ...] = (),
) -> Anomaly:
    return Anomaly(
        name=name,
        overrides=overrides,
        expected_level=level,
        expected_codes=frozenset(codes),
        expected_conditions=frozenset(conditions),
    )


ANOMALIES: Mapping[str, Anomaly] = {
    anomaly.name: anomaly
    for anomaly in (
        _anomaly("dose_30day_warning", {"bfo_dose_30day_mgy_eq": _WARNING_30DAY_MGY_EQ},
                 "yellow", "RADIATION_30DAY_LIMIT",
                 conditions=("ACUTE_RADIATION_SYNDROME",)),
        _anomaly("dose_30day_exceeded", {"bfo_dose_30day_mgy_eq": _EXCEEDED_30DAY_MGY_EQ},
                 "red", "RADIATION_30DAY_LIMIT"),
        _anomaly("career_limit_warning", {"radiation_dose_career_msv": _CAREER_WARNING_MSV},
                 "yellow", "RADIATION_CAREER_LIMIT"),
        _anomaly("career_limit_exceeded", {"radiation_dose_career_msv": _EXCEEDED_CAREER_MSV},
                 "red", "RADIATION_CAREER_LIMIT"),
        _anomaly("tachycardia", {"hr": 125}, "yellow", "HR_HIGH",
                 conditions=("CARDIAC_ARRHYTHMIA",)),
        _anomaly("hypoxia", {"spo2": 89}, "yellow", "SPO2_LOW", "NEWS2_MEDIUM",
                 conditions=("ALTITUDE_SICKNESS",)),
        _anomaly(
            "hypotension",
            {"bp": {"systolic": 88, "diastolic": 55}},
            "yellow",
            "BP_LOW",
            "NEWS2_MEDIUM",
            conditions=(),
        ),
        _anomaly("hypovolemia_like", {"bp": {"systolic": 85, "diastolic": 55}, "hr": 125},
                 "yellow", "BP_LOW", "HR_HIGH", "NEWS2_MEDIUM",
                 conditions=("HYPOVOLEMIC_SHOCK",)),
        _anomaly("fever", {"temp_c": 39.4}, "yellow", "TEMP_HIGH"),
        _anomaly("radiation_storm", {"radiation_dose_rate": 1500.0}, "red", "RADIATION_CRITICAL",
                 conditions=("ACUTE_RADIATION_SYNDROME",)),
        _anomaly("radiation_elevated", {"radiation_dose_rate": 250.0}, "yellow", "RADIATION_ELEVATED"),
        _anomaly("sleep_deprivation", {"sleep_hours": 4.0}, "yellow", "SLEEP_DEFICIT",
                 conditions=("SLEEP_DISORDER",)),
        _anomaly("low_mood", {"mood_score": 3}, "yellow", "LOW_MOOD",
                 conditions=("DEPRESSION",)),
        _anomaly("phq2_positive", {"phq2_score": 4}, "yellow", "PHQ2_POSITIVE",
                 conditions=("DEPRESSION",)),
        _anomaly("caloric_deficit", {"caloric_intake": 1500}, "red", "CALORIC_DEFICIT",
                 conditions=("NUTRITIONAL_DEFICIT",)),
        _anomaly("caloric_low", {"caloric_intake": 2400}, "yellow", "CALORIC_LOW"),
        _anomaly("exercise_deficit", {"exercise_minutes_today": 30}, "yellow", "EXERCISE_DEFICIT"),
        _anomaly(
            "sepsis_like",
            {"hr": 135, "resp_rate": 26, "temp_c": 39.5, "spo2": 93},
            "red",
            "NEWS2_HIGH",
            conditions=("SEPSIS", "RESPIRATORY_INFECTION_LOWER"),
        ),
        _anomaly("hypercapnia", {"cabin_ppco2_mmhg": 8.0}, "red", "CABIN_CO2_HIGH",
                 conditions=("HYPERCAPNIA",)),
        _anomaly("sans_like", {"iop_mmhg": 24.0}, "yellow", "IOP_HIGH",
                 conditions=("SANS",)),
    )
}


def apply_anomaly(raw: Mapping[str, Any], name: str) -> dict[str, Any]:
    """Return a NEW dict: ``raw`` with anomaly ``name``'s overrides applied.

    ``raw`` is never mutated. A nested ``bp`` override is merged into the
    existing ``bp`` object rather than replacing it wholesale. Raises
    ``KeyError`` naming the unknown anomaly (and the valid names) otherwise.
    """
    anomaly = ANOMALIES.get(name)
    if anomaly is None:
        available = ", ".join(sorted(ANOMALIES))
        raise KeyError(f"unknown anomaly {name!r}; available: {available}")

    updated = dict(raw)
    for key, value in anomaly.overrides.items():
        if key == "bp" and isinstance(value, Mapping) and isinstance(updated.get("bp"), Mapping):
            updated["bp"] = {**updated["bp"], **value}
        else:
            updated[key] = value
    return updated


@dataclass(frozen=True)
class Step:
    """One tick of a scenario: its position, raw sample, and the anomaly applied (if any)."""

    index: int
    raw: Mapping[str, Any]
    anomaly_name: str | None


def _timestamp_for_index(index: int) -> str:
    moment = _BASE_TIMESTAMP + timedelta(seconds=_STEP_SECONDS * index)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def _clamped_anomaly_count(requested: int, length: int) -> int:
    bounded = max(_MIN_ANOMALIES, min(_MAX_ANOMALIES, requested))
    return min(bounded, length)


def scenario(seed: int = 42, length: int = 24, anomalies: int = 4) -> tuple[Step, ...]:
    """A deterministic sequence of ``length`` steps, mostly nominal.

    Between 3 and 5 anomalies (``anomalies``, clamped to that range) are placed
    at indices chosen by ``random.Random(seed)``; every other step is nominal.
    Timestamps start at 2026-11-14T10:00:00Z, spaced 60 s apart.
    """
    rng = random.Random(seed)
    count = _clamped_anomaly_count(anomalies, length)
    anomaly_indices = set(rng.sample(range(length), k=count))
    names = sorted(ANOMALIES)

    steps = []
    for index in range(length):
        timestamp = _timestamp_for_index(index)
        if index in anomaly_indices:
            name = rng.choice(names)
            raw = apply_anomaly(nominal_raw(timestamp), name)
            steps.append(Step(index=index, raw=raw, anomaly_name=name))
        else:
            steps.append(Step(index=index, raw=nominal_raw(timestamp), anomaly_name=None))
    return tuple(steps)


def stream(
    seed: int = 42, period_s: float = 1.0,
    astronaut_ids: tuple[str, ...] = ("ASTRO-01",),
):
    """Cycle per-astronaut scenarios, yielding one crew round per period.

    Each member uses seed + their index; the default preserves the single-member
    stream. Use period_s=0 in tests. IDs must be nonempty and unique.
    """
    if not astronaut_ids or not all(astronaut_ids) or len(set(astronaut_ids)) != len(astronaut_ids):
        raise ValueError("astronaut_ids must be nonempty, unique IDs")
    scenarios = [scenario(seed=seed + index) for index in range(len(astronaut_ids))]
    while True:
        for crew_steps in zip(*scenarios):
            for astronaut_id, step in zip(astronaut_ids, crew_steps):
                yield {**step.raw, "astronaut_id": astronaut_id}
            if period_s > 0:
                time.sleep(period_s)
