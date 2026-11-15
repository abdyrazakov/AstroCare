"""Tests for astro_brain.trajectory — the population body-trajectory model.

Numbers asserted here are transcribed from docs/BODY_TRAJECTORY_RESEARCH.md
section 1; see that document for the basis and status of each value, and
docs/EVIDENCE_TRAJECTORY.md for the curve-shape DESIGN DECISIONs.
"""

from __future__ import annotations

import json

import pytest

from astro_brain.trajectory import (
    MISSION_LENGTH_TYPICAL_DAYS,
    TRAJECTORY_PARAMETERS,
    TrajectoryParameter,
    expected_change,
    to_dict,
    trajectory_report,
)

PERCENT_CHANGE_CODES = (
    "bone_bmd_hip_pct",
    "bone_bmd_spine_pct",
    "muscle_strength_pct",
    "vo2peak_pct",
    "body_mass_pct",
)
NO_COUNTERMEASURE_CODES = (
    "muscle_strength_pct",
    "vo2peak_pct",
    "body_mass_pct",
    "orthostatic_intolerance_risk",
    "sans_risk",
)


def test_every_parameter_has_evidence_and_status() -> None:
    for code, param in TRAJECTORY_PARAMETERS.items():
        assert param.evidence, f"{code} missing evidence"
        assert param.status in ("VERIFIED", "VERIFY"), f"{code} has bad status"


def test_registry_key_matches_parameter_code() -> None:
    for code, param in TRAJECTORY_PARAMETERS.items():
        assert code == param.code


@pytest.mark.parametrize("code", PERCENT_CHANGE_CODES + ("sans_risk",))
def test_day_one_is_approximately_baseline(code: str) -> None:
    point = expected_change(code, mission_day=1)
    assert point.expected == pytest.approx(0.0, abs=0.06)


def test_hip_bmd_day_30_matches_doc_at_zero_adherence() -> None:
    point = expected_change("bone_bmd_hip_pct", mission_day=30, exercise_adherence=0.0)
    assert point.expected == pytest.approx(-1.56)


def test_hip_bmd_day_30_matches_doc_at_full_adherence() -> None:
    point = expected_change("bone_bmd_hip_pct", mission_day=30, exercise_adherence=1.0)
    assert point.expected == pytest.approx(-0.50)


def test_spine_bmd_day_30_matches_doc_at_zero_and_full_adherence() -> None:
    no_ex = expected_change("bone_bmd_spine_pct", mission_day=30, exercise_adherence=0.0)
    with_ex = expected_change("bone_bmd_spine_pct", mission_day=30, exercise_adherence=1.0)
    assert no_ex.expected == pytest.approx(-1.06)
    assert with_ex.expected == pytest.approx(-0.32)


def test_hip_bmd_adherence_interpolates_linearly() -> None:
    point = expected_change("bone_bmd_hip_pct", mission_day=30, exercise_adherence=0.5)
    # halfway between -1.56 and -0.50
    assert point.expected == pytest.approx(-1.03)


@pytest.mark.parametrize(
    ("code", "breakpoint_day", "plateau_value"),
    [
        ("muscle_strength_pct", MISSION_LENGTH_TYPICAL_DAYS, -24.0),
        ("vo2peak_pct", MISSION_LENGTH_TYPICAL_DAYS, -10.0),
        ("body_mass_pct", 30, -5.0),
        ("orthostatic_intolerance_risk", 120, 0.66),
        ("sans_risk", 30, 0.15),
    ],
)
def test_plateau_respects_breakpoint(code: str, breakpoint_day: int, plateau_value: float) -> None:
    at_breakpoint = expected_change(code, mission_day=breakpoint_day)
    well_beyond = expected_change(code, mission_day=breakpoint_day + 100)
    assert at_breakpoint.expected == pytest.approx(plateau_value)
    assert well_beyond.expected == pytest.approx(plateau_value)


def test_vo2peak_reaches_documented_trough_at_day_14() -> None:
    point = expected_change("vo2peak_pct", mission_day=14)
    assert point.expected == pytest.approx(-17.0)


def test_orthostatic_risk_starts_near_short_duration_figure() -> None:
    point = expected_change("orthostatic_intolerance_risk", mission_day=1)
    assert point.expected == pytest.approx(0.20)


@pytest.mark.parametrize("code", NO_COUNTERMEASURE_CODES)
def test_adherence_has_no_effect_without_a_countermeasure_variant(code: str) -> None:
    no_ex = expected_change(code, mission_day=45, exercise_adherence=0.0)
    full_ex = expected_change(code, mission_day=45, exercise_adherence=1.0)
    assert no_ex.expected == pytest.approx(full_ex.expected)
    # adherence_used still echoes the input even though it had no effect.
    assert no_ex.adherence_used == pytest.approx(0.0)
    assert full_ex.adherence_used == pytest.approx(1.0)


@pytest.mark.parametrize(
    "mission_day",
    [MISSION_LENGTH_TYPICAL_DAYS, 1],
)
def test_not_extrapolated_at_or_before_typical_mission_length(mission_day: int) -> None:
    point = expected_change("bone_bmd_hip_pct", mission_day=mission_day)
    assert point.extrapolated is False


def test_extrapolated_past_typical_mission_length() -> None:
    point = expected_change("bone_bmd_hip_pct", mission_day=MISSION_LENGTH_TYPICAL_DAYS + 1)
    assert point.extrapolated is True


def test_lower_and_upper_are_a_twenty_five_percent_band() -> None:
    point = expected_change("bone_bmd_hip_pct", mission_day=30, exercise_adherence=0.0)
    spread = abs(point.expected) * 0.25
    assert point.lower == pytest.approx(point.expected - spread)
    assert point.upper == pytest.approx(point.expected + spread)
    assert point.lower < point.expected < point.upper


def test_mission_day_must_be_at_least_one() -> None:
    with pytest.raises(ValueError):
        expected_change("bone_bmd_hip_pct", mission_day=0)


def test_adherence_must_be_within_unit_interval() -> None:
    with pytest.raises(ValueError):
        expected_change("bone_bmd_hip_pct", mission_day=10, exercise_adherence=1.5)
    with pytest.raises(ValueError):
        expected_change("bone_bmd_hip_pct", mission_day=10, exercise_adherence=-0.1)


def test_unknown_code_raises_value_error() -> None:
    with pytest.raises(ValueError):
        expected_change("not_a_real_code", mission_day=10)


def test_trajectory_report_covers_every_registered_parameter() -> None:
    points = trajectory_report(mission_day=30, exercise_adherence=1.0)
    assert {point.code for point in points} == set(TRAJECTORY_PARAMETERS)
    assert len(points) == len(TRAJECTORY_PARAMETERS)


def test_to_dict_is_json_serialisable_with_disclaimer() -> None:
    payload = to_dict(mission_day=30, exercise_adherence=0.75)
    serialised = json.dumps(payload)
    reloaded = json.loads(serialised)

    assert reloaded["missionDay"] == 30
    assert reloaded["exerciseAdherence"] == 0.75
    assert reloaded["populationModel"] is True
    assert reloaded["disclaimer"] == (
        "Population expectation from published spaceflight data; "
        "not this astronaut's measurement; never a diagnosis."
    )
    assert len(reloaded["parameters"]) == len(TRAJECTORY_PARAMETERS)
    for entry in reloaded["parameters"]:
        assert entry["status"] in ("VERIFIED", "VERIFY")
        assert entry["evidenceRef"]


def test_linear_per_month_parameter_requires_a_rate() -> None:
    with pytest.raises(ValueError):
        TrajectoryParameter(
            code="bad",
            label="bad",
            unit="%",
            curve="linear_per_month",
            evidence="row x",
            status="VERIFIED",
        )


def test_early_drop_then_plateau_requires_breakpoints_starting_at_day_one() -> None:
    with pytest.raises(ValueError):
        TrajectoryParameter(
            code="bad",
            label="bad",
            unit="%",
            curve="early_drop_then_plateau",
            evidence="row x",
            status="VERIFIED",
            breakpoints=((5, 0.0), (10, -1.0)),
        )


def test_unknown_curve_is_rejected() -> None:
    with pytest.raises(ValueError):
        TrajectoryParameter(
            code="bad",
            label="bad",
            unit="%",
            curve="exponential",
            evidence="row x",
            status="VERIFIED",
            rate_no_countermeasure_pct_per_month=-1.0,
        )
