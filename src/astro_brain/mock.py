"""Mock vitals data strictly matching the INPUT contract (AGENTS.md section 2).

Everything here produces raw JSON-shaped dicts (snake_case keys, ``bp`` as a
nested ``{"systolic", "diastolic"}`` object) -- the shape the data team hands
to ``Brain.process``, never the typed ``VitalsSample``.

``_NOMINAL_RAW`` mirrors the numeric values of ``tests/conftest.py``'s
``NOMINAL_DEFAULTS`` (required fields only) so "nominal" means the same thing
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

# Required-field values, matching tests/conftest.py NOMINAL_DEFAULTS exactly.
_NOMINAL_RAW: dict[str, Any] = {
    "hr": 68,
    "spo2": 98,
    "bp": {"systolic": 118, "diastolic": 76},
    "temp_c": 36.7,
    "resp_rate": 15,
    "radiation_dose_rate": 20.0,
    "exercise_minutes_today": 120,
    "required_exercise_minutes": 150,
    "caloric_intake": 2600,
    "caloric_target": 2800,
    "sleep_hours": 7.5,
    "mood_score": 8,
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


def _anomaly(
    name: str, overrides: Mapping[str, Any], level: Literal["yellow", "red"], *codes: str
) -> Anomaly:
    return Anomaly(name=name, overrides=overrides, expected_level=level, expected_codes=frozenset(codes))


ANOMALIES: Mapping[str, Anomaly] = {
    anomaly.name: anomaly
    for anomaly in (
        _anomaly("tachycardia", {"hr": 125}, "yellow", "HR_HIGH"),
        _anomaly("hypoxia", {"spo2": 89}, "yellow", "SPO2_LOW", "NEWS2_MEDIUM"),
        _anomaly(
            "hypotension",
            {"bp": {"systolic": 88, "diastolic": 55}},
            "yellow",
            "BP_LOW",
            "NEWS2_MEDIUM",
        ),
        _anomaly("fever", {"temp_c": 39.4}, "yellow", "TEMP_HIGH"),
        _anomaly("radiation_storm", {"radiation_dose_rate": 1500.0}, "red", "RADIATION_CRITICAL"),
        _anomaly("radiation_elevated", {"radiation_dose_rate": 250.0}, "yellow", "RADIATION_ELEVATED"),
        _anomaly("sleep_deprivation", {"sleep_hours": 4.0}, "yellow", "SLEEP_DEFICIT"),
        _anomaly("low_mood", {"mood_score": 3}, "yellow", "LOW_MOOD"),
        _anomaly("caloric_deficit", {"caloric_intake": 1500}, "yellow", "CALORIC_DEFICIT"),
        _anomaly("exercise_deficit", {"exercise_minutes_today": 30}, "yellow", "EXERCISE_DEFICIT"),
        _anomaly(
            "sepsis_like",
            {"hr": 135, "resp_rate": 26, "temp_c": 39.5, "spo2": 93},
            "red",
            "NEWS2_HIGH",
        ),
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


def stream(seed: int = 42, period_s: float = 1.0):
    """Yield raw input-contract dicts forever, cycling ``scenario(seed)``.

    Used by the dashboard's ``--simulate`` mode to drive a live feed; a test
    should pass ``period_s=0`` (or wrap with ``itertools.islice``) rather than
    consume this generator in real time.
    """
    steps = scenario(seed=seed)
    while True:
        for step in steps:
            yield step.raw
            if period_s > 0:
                time.sleep(period_s)
