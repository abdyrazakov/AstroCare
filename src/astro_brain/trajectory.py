"""Population-level "expected body change by mission day" trajectory model.

This module is explicitly **not a measurement** of any real astronaut. It
answers "what does the published NASA/ISS/Mir literature say a population of
astronauts experiences by mission day N", so a presentation layer can draw a
dashed "expected" line next to the astronaut's own solid "measured" line.

Data source: ``docs/BODY_TRAJECTORY_RESEARCH.md`` — the only numeric source
for this module. Every magnitude in :data:`TRAJECTORY_PARAMETERS` traces to a
row in that document's section 1 table and keeps that row's VERIFIED/VERIFY
status unchanged. Curve shapes, breakpoint days, the adherence-interpolation
model, and the uncertainty band are prototype **DESIGN DECISION**s with no
cited numeric source; see ``docs/EVIDENCE_TRAJECTORY.md`` for each one.

Two curve shapes are supported, matching the research doc's own sketch in its
section 3 (collapsed from four named shapes there into two mechanical ones
here, since the underlying math is the same):

- ``"linear_per_month"``: a constant %/month rate, applied for
  ``mission_day / DAYS_PER_MONTH`` months. Used only where the doc states a
  numeric monthly rate (the two bone parameters).
- ``"early_drop_then_plateau"``: a piecewise-linear curve through
  ``breakpoints`` — ``(mission_day, value)`` anchors, the first always at day
  1 — held flat at the last anchor's value for any later mission day.

Adherence (``exercise_minutes_today / required_exercise_minutes`` in the
input contract, passed here as ``exercise_adherence``) only affects a
parameter when the research doc gives both a no-countermeasure and a
with-ARED/SPRINT-countermeasure rate. The research doc gives that numeric
pair for exactly the two bone parameters (row 1b); everywhere else the doc
only describes countermeasures qualitatively, so adherence is accepted but
has no effect on ``expected`` — see the module docstring in
``docs/EVIDENCE_TRAJECTORY.md`` for the DESIGN DECISION rationale.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

CURVE_LINEAR_PER_MONTH = "linear_per_month"
CURVE_EARLY_DROP_THEN_PLATEAU = "early_drop_then_plateau"
_VALID_CURVES = frozenset({CURVE_LINEAR_PER_MONTH, CURVE_EARLY_DROP_THEN_PLATEAU})

STATUS_VERIFIED = "VERIFIED"
STATUS_VERIFY = "VERIFY"
_VALID_STATUSES = frozenset({STATUS_VERIFIED, STATUS_VERIFY})

UNIT_PERCENT = "%"
UNIT_PROBABILITY = "probability"

# DESIGN DECISION: a 30-day calendar-month approximation, matching the
# %/month unit the research doc itself uses (row 1b). Not a cited number.
DAYS_PER_MONTH = 30

# DESIGN DECISION: the research doc repeatedly frames long-duration missions
# as "4 to 6 months" (rows 1a, 5); 180 days is used here as the boundary past
# which this model's curves are extrapolated beyond their documented range.
MISSION_LENGTH_TYPICAL_DAYS = 180

# DESIGN DECISION: the research doc states no confidence interval for any
# row in this pass (two rows give an SD, which is not a CI); every point
# therefore gets the same prototype +/-25% band.
UNCERTAINTY_BAND_FRACTION = 0.25

DISCLAIMER = (
    "Population expectation from published spaceflight data; "
    "not this astronaut's measurement; never a diagnosis."
)


@dataclass(frozen=True)
class TrajectoryParameter:
    """One body-system parameter's documented trajectory coefficients.

    ``evidence`` is a short id matching a row of
    ``docs/BODY_TRAJECTORY_RESEARCH.md`` (e.g. ``"row 1b"``); ``status`` is
    that row's VERIFIED/VERIFY status, copied unchanged.

    For ``curve == "linear_per_month"``, ``rate_no_countermeasure_pct_per_month``
    is required and ``breakpoints`` must be empty. ``rate_with_countermeasure_pct_per_month``
    is optional; when set, :func:`expected_change` interpolates between the
    two rates by ``exercise_adherence`` (DESIGN DECISION — see module docstring).

    For ``curve == "early_drop_then_plateau"``, ``breakpoints`` is a
    non-empty, strictly-day-ascending tuple of ``(mission_day, value)``
    anchors starting at day 1; both rate fields must be unset, and
    ``exercise_adherence`` has no effect on ``expected``.
    """

    code: str
    label: str
    unit: str
    curve: str
    evidence: str
    status: str
    rate_no_countermeasure_pct_per_month: float | None = None
    rate_with_countermeasure_pct_per_month: float | None = None
    breakpoints: tuple[tuple[int, float], ...] = ()

    def __post_init__(self) -> None:
        if self.curve not in _VALID_CURVES:
            raise ValueError(f"{self.code}: unknown curve {self.curve!r}")
        if self.status not in _VALID_STATUSES:
            raise ValueError(f"{self.code}: unknown status {self.status!r}")
        if self.curve == CURVE_LINEAR_PER_MONTH:
            self._validate_linear_per_month()
        else:
            self._validate_early_drop_then_plateau()

    def _validate_linear_per_month(self) -> None:
        if self.rate_no_countermeasure_pct_per_month is None:
            raise ValueError(f"{self.code}: linear_per_month needs a no-countermeasure rate")
        if self.breakpoints:
            raise ValueError(f"{self.code}: linear_per_month must not set breakpoints")

    def _validate_early_drop_then_plateau(self) -> None:
        if self.rate_no_countermeasure_pct_per_month is not None:
            raise ValueError(f"{self.code}: early_drop_then_plateau must not set a rate")
        if not self.breakpoints:
            raise ValueError(f"{self.code}: early_drop_then_plateau needs breakpoints")
        if self.breakpoints[0][0] != 1:
            raise ValueError(f"{self.code}: first breakpoint must be mission day 1")
        days = [day for day, _ in self.breakpoints]
        if days != sorted(set(days)) or len(days) != len(self.breakpoints):
            raise ValueError(f"{self.code}: breakpoints must be strictly day-ascending")

    @property
    def has_countermeasure_variant(self) -> bool:
        """Whether adherence can change ``expected`` for this parameter."""
        return self.rate_with_countermeasure_pct_per_month is not None


@dataclass(frozen=True)
class TrajectoryPoint:
    """One evaluated trajectory value for a parameter at a mission day."""

    code: str
    mission_day: int
    expected: float
    lower: float
    upper: float
    adherence_used: float
    extrapolated: bool
    evidence: str
    status: str
    label: str
    unit: str

    def to_dict(self) -> dict[str, object]:
        """Return this point in the camelCase shape used by ``to_dict()``."""
        return {
            "code": self.code,
            "label": self.label,
            "unit": self.unit,
            "missionDay": self.mission_day,
            "expected": self.expected,
            "lower": self.lower,
            "upper": self.upper,
            "adherenceUsed": self.adherence_used,
            "extrapolated": self.extrapolated,
            "evidenceRef": self.evidence,
            "status": self.status,
        }


# Row numbers below are docs/BODY_TRAJECTORY_RESEARCH.md section 1 table rows.
# Breakpoint days beyond the first (always day 1, value 0.0 or the doc's own
# early-mission figure) are DESIGN DECISIONs where the doc gives no explicit
# timing; see docs/EVIDENCE_TRAJECTORY.md for each one.
TRAJECTORY_PARAMETERS: MappingProxyType[str, TrajectoryParameter] = MappingProxyType({
    "bone_bmd_hip_pct": TrajectoryParameter(
        code="bone_bmd_hip_pct",
        label="Hip (trochanter) areal BMD change",
        unit=UNIT_PERCENT,
        curve=CURVE_LINEAR_PER_MONTH,
        evidence="row 1b",
        status=STATUS_VERIFIED,
        rate_no_countermeasure_pct_per_month=-1.56,
        rate_with_countermeasure_pct_per_month=-0.50,
    ),
    "bone_bmd_spine_pct": TrajectoryParameter(
        code="bone_bmd_spine_pct",
        label="Lumbar spine areal BMD change",
        unit=UNIT_PERCENT,
        curve=CURVE_LINEAR_PER_MONTH,
        evidence="row 1b",
        status=STATUS_VERIFIED,
        rate_no_countermeasure_pct_per_month=-1.06,
        rate_with_countermeasure_pct_per_month=-0.32,
    ),
    "muscle_strength_pct": TrajectoryParameter(
        code="muscle_strength_pct",
        label="Calf muscle strength change",
        unit=UNIT_PERCENT,
        curve=CURVE_EARLY_DROP_THEN_PLATEAU,
        evidence="row 2",
        status=STATUS_VERIFIED,
        breakpoints=((1, 0.0), (MISSION_LENGTH_TYPICAL_DAYS, -24.0)),
    ),
    "vo2peak_pct": TrajectoryParameter(
        code="vo2peak_pct",
        label="VO2peak (aerobic capacity) change",
        unit=UNIT_PERCENT,
        curve=CURVE_EARLY_DROP_THEN_PLATEAU,
        evidence="row 3",
        status=STATUS_VERIFIED,
        breakpoints=((1, 0.0), (14, -17.0), (MISSION_LENGTH_TYPICAL_DAYS, -10.0)),
    ),
    "body_mass_pct": TrajectoryParameter(
        code="body_mass_pct",
        label="Body mass change",
        unit=UNIT_PERCENT,
        curve=CURVE_EARLY_DROP_THEN_PLATEAU,
        evidence="row 4",
        status=STATUS_VERIFIED,
        breakpoints=((1, 0.0), (30, -5.0)),
    ),
    "orthostatic_intolerance_risk": TrajectoryParameter(
        code="orthostatic_intolerance_risk",
        label="Post-landing orthostatic intolerance risk",
        unit=UNIT_PROBABILITY,
        curve=CURVE_EARLY_DROP_THEN_PLATEAU,
        evidence="row 5",
        status=STATUS_VERIFIED,
        breakpoints=((1, 0.20), (120, 0.66)),
    ),
    "sans_risk": TrajectoryParameter(
        code="sans_risk",
        label="SANS (optic disc edema) onset risk",
        unit=UNIT_PROBABILITY,
        curve=CURVE_EARLY_DROP_THEN_PLATEAU,
        evidence="row 6",
        status=STATUS_VERIFIED,
        breakpoints=((1, 0.0), (30, 0.15)),
    ),
})


def _interpolated_rate(param: TrajectoryParameter, exercise_adherence: float) -> float:
    """%/month rate for a linear_per_month parameter at ``exercise_adherence``.

    DESIGN DECISION: linear interpolation between the no-countermeasure and
    with-countermeasure rates; the doc verifies only the two endpoints.
    """
    no_rate = param.rate_no_countermeasure_pct_per_month
    assert no_rate is not None  # guaranteed by __post_init__ for this curve
    with_rate = param.rate_with_countermeasure_pct_per_month
    if with_rate is None:
        return no_rate
    return no_rate + (with_rate - no_rate) * exercise_adherence


def _piecewise_value(breakpoints: tuple[tuple[int, float], ...], mission_day: int) -> float:
    """Linear interpolation through ``breakpoints``, flat beyond the last one."""
    first_day, first_value = breakpoints[0]
    if mission_day <= first_day:
        return first_value
    for (day_a, value_a), (day_b, value_b) in zip(breakpoints, breakpoints[1:]):
        if mission_day <= day_b:
            fraction = (mission_day - day_a) / (day_b - day_a)
            return value_a + (value_b - value_a) * fraction
    return breakpoints[-1][1]


def _raw_expected_value(param: TrajectoryParameter, mission_day: int, exercise_adherence: float) -> float:
    if param.curve == CURVE_LINEAR_PER_MONTH:
        rate = _interpolated_rate(param, exercise_adherence)
        return rate * (mission_day / DAYS_PER_MONTH)
    return _piecewise_value(param.breakpoints, mission_day)


def _clamp_to_physiologic_range(unit: str, value: float) -> float:
    """DESIGN DECISION: generic sanity bounds; the doc gives no floor/ceiling.

    A percent-change parameter cannot lose or gain more than 100%; a
    probability-style parameter stays within [0, 1].
    """
    if unit == UNIT_PERCENT:
        return max(-100.0, min(100.0, value))
    if unit == UNIT_PROBABILITY:
        return max(0.0, min(1.0, value))
    return value


def _uncertainty_band(unit: str, expected: float) -> tuple[float, float]:
    spread = abs(expected) * UNCERTAINTY_BAND_FRACTION
    lower = _clamp_to_physiologic_range(unit, expected - spread)
    upper = _clamp_to_physiologic_range(unit, expected + spread)
    return lower, upper


def expected_change(code: str, mission_day: int, exercise_adherence: float = 1.0) -> TrajectoryPoint:
    """Population-level expected change for ``code`` at ``mission_day``.

    Not a measurement of any real astronaut — see the module docstring.

    Raises ``ValueError`` for an unknown ``code``, ``mission_day < 1``, or
    ``exercise_adherence`` outside ``[0, 1]``.
    """
    if mission_day < 1:
        raise ValueError(f"mission_day must be >= 1, got {mission_day}")
    if not 0.0 <= exercise_adherence <= 1.0:
        raise ValueError(f"exercise_adherence must be within [0, 1], got {exercise_adherence}")
    param = TRAJECTORY_PARAMETERS.get(code)
    if param is None:
        raise ValueError(f"unknown trajectory parameter code: {code!r}")

    raw_expected = _raw_expected_value(param, mission_day, exercise_adherence)
    expected = _clamp_to_physiologic_range(param.unit, raw_expected)
    lower, upper = _uncertainty_band(param.unit, expected)
    extrapolated = mission_day > MISSION_LENGTH_TYPICAL_DAYS

    return TrajectoryPoint(
        code=param.code,
        mission_day=mission_day,
        expected=expected,
        lower=lower,
        upper=upper,
        adherence_used=exercise_adherence,
        extrapolated=extrapolated,
        evidence=param.evidence,
        status=param.status,
        label=param.label,
        unit=param.unit,
    )


def trajectory_report(mission_day: int, exercise_adherence: float = 1.0) -> tuple[TrajectoryPoint, ...]:
    """One :class:`TrajectoryPoint` per registered parameter, in registry order."""
    return tuple(
        expected_change(code, mission_day, exercise_adherence)
        for code in TRAJECTORY_PARAMETERS
    )


def to_dict(mission_day: int, exercise_adherence: float = 1.0) -> dict[str, object]:
    """JSON-serialisable report envelope; see the module docstring for shape."""
    points = trajectory_report(mission_day, exercise_adherence)
    return {
        "missionDay": mission_day,
        "exerciseAdherence": exercise_adherence,
        "populationModel": True,
        "disclaimer": DISCLAIMER,
        "parameters": [point.to_dict() for point in points],
    }
