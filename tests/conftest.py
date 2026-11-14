"""Shared test fixtures for astro_brain scoring and doctor-layer tests.

The scoring-agent fixtures (``nominal_sample``) and the doctor-agent fixtures
(``FakeFlag``, ``FakeAssessment``, ``make_assessment``) live together in this one
file because pytest only loads a single ``tests/conftest.py``. Doctor Layer code
is duck-typed against the real ``astro_brain.scoring.Assessment``/``Flag`` shape, so
its tests use the fakes below instead of importing ``astro_brain.scoring`` directly.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import pytest

from astro_brain.contract import BloodPressure, VitalsSample

NOMINAL_DEFAULTS: dict[str, object] = {
    "timestamp": "2026-11-14T10:00:00Z",
    "astronaut_id": "ASTRO-01",
    "hr": 68,
    "spo2": 98,
    "bp": BloodPressure(systolic=118, diastolic=76),
    "temp_c": 36.7,
    "resp_rate": 15,
    "radiation_dose_rate": 20.0,
    "exercise_minutes_today": 120,
    "required_exercise_minutes": 150,
    "caloric_intake": 2600,
    "caloric_target": 2800,
    "sleep_hours": 7.5,
    "mood_score": 8,
    "on_supplemental_o2": False,
    "consciousness": "alert",
    "noaa_s_scale": None,
}


def nominal_sample(**overrides: object) -> VitalsSample:
    """A fresh, nominal (all-green) VitalsSample; pass kwargs to override fields."""
    fields = {**NOMINAL_DEFAULTS, **overrides}
    return VitalsSample(**fields)  # type: ignore[arg-type]


@pytest.fixture(name="nominal_sample")
def nominal_sample_fixture():
    """Fixture form: returns the ``nominal_sample`` factory function itself."""
    return nominal_sample


# --------------------------------------------------------------------------- doctor-agent fakes


@dataclass(frozen=True)
class FakeFlag:
    """Duck-type stand-in for ``astro_brain.flags.Flag``."""

    code: str
    severity: str
    message: str
    value: float | int | str | None = None
    threshold: float | int | str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "severity": self.severity,
            "message": self.message,
            "value": self.value,
            "threshold": self.threshold,
        }


@dataclass(frozen=True)
class FakeAssessment:
    """Duck-type stand-in for ``astro_brain.scoring.Assessment``."""

    timestamp: str = "2026-11-14T10:00:00Z"
    astronaut_id: str = "ASTRO-01"
    alert_level: str = "green"
    news2_total: int = 0
    news2_components: Mapping[str, int] = field(default_factory=dict)
    flags: tuple[FakeFlag, ...] = ()

    def flag_codes(self) -> tuple[str, ...]:
        return tuple(sorted({flag.code for flag in self.flags}))


def make_assessment(
    *,
    alert_level: str = "green",
    news2_total: int = 0,
    flags: tuple[FakeFlag, ...] = (),
    astronaut_id: str = "ASTRO-01",
    timestamp: str = "2026-11-14T10:00:00Z",
) -> FakeAssessment:
    """Convenience builder for a ``FakeAssessment`` with sensible defaults."""
    return FakeAssessment(
        timestamp=timestamp,
        astronaut_id=astronaut_id,
        alert_level=alert_level,
        news2_total=news2_total,
        news2_components={},
        flags=flags,
    )
