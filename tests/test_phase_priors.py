"""Tests for the IMM-derived phase priors in astro_brain.phase_priors.

Numbers are transcribed from docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md
section 3 and section 7; see that document for basis and status of each value.
"""

from __future__ import annotations

import pytest

from astro_brain.conditions import CONDITION_RULES
from astro_brain.phase_priors import (
    IMM_PRIORS,
    PHASE_1_ACUTE_ADAPTATION,
    PHASE_2_LONG_DURATION,
    PhasePrior,
    phase_multiplier,
    prior_record,
)

SA_CODES = ("SANS", "SLEEP_DISORDER")
GENERAL_CODES = (
    "HYPOVOLEMIC_SHOCK",
    "SEPSIS",
    "CARDIAC_ARRHYTHMIA",
    "DEPRESSION",
    "HYPERCAPNIA",
    "RESPIRATORY_INFECTION_LOWER",
)
NOT_FOUND_CODES = ("ALTITUDE_SICKNESS", "NUTRITIONAL_DEFICIT")
LOW_TIER_CODES = ("SEPSIS", "HYPOVOLEMIC_SHOCK", "CARDIAC_ARRHYTHMIA", "DEPRESSION")
HIGH_TIER_CODES = ("RESPIRATORY_INFECTION_LOWER", "HYPERCAPNIA")


def test_every_conditions_rule_code_has_a_record() -> None:
    for rule in CONDITION_RULES:
        assert rule.code in IMM_PRIORS, f"missing IMM prior for {rule.code}"


def test_not_found_codes_have_explicit_status() -> None:
    for code in NOT_FOUND_CODES:
        record = prior_record(code)
        assert record is not None
        assert record.status == "NOT_FOUND"
        assert record.phase_1 is None
        assert record.phase_2 is None


def test_sans_proportion_matches_report() -> None:
    record = prior_record("SANS")
    assert record is not None
    assert record.phase_1 == pytest.approx(0.2789)
    assert record.phase_2 == pytest.approx(0.0)
    assert record.measure == "proportion"
    assert record.mechanism == "SA"
    assert record.status == "VERIFIED"


def test_sleep_disorder_sas_insomnia_proportion_matches_report() -> None:
    record = prior_record("SLEEP_DISORDER")
    assert record is not None
    assert record.phase_1 == pytest.approx(0.4721)
    assert record.phase_2 == pytest.approx(0.0)
    assert record.mechanism == "SA"


def test_sleep_disorder_note_mentions_late_insomnia() -> None:
    record = prior_record("SLEEP_DISORDER")
    assert record is not None
    assert record.note is not None
    assert "late" in record.note.lower()


def test_sepsis_phase_values_match_report() -> None:
    record = prior_record("SEPSIS")
    assert record is not None
    assert record.phase_1 == pytest.approx(3.288e-5, rel=1e-3)
    assert record.phase_2 == pytest.approx(1.151e-3, rel=1e-3)


def test_hypovolemic_shock_phase_values_match_report() -> None:
    record = prior_record("HYPOVOLEMIC_SHOCK")
    assert record is not None
    assert record.phase_1 == pytest.approx(8.78e-6, rel=1e-3)
    assert record.phase_2 == pytest.approx(3.073e-4, rel=1e-3)
    assert record.emcl_name == "ICL116 Traumatic Hypovolemic Shock"


def test_cardiac_arrhythmia_phase_values_match_report() -> None:
    record = prior_record("CARDIAC_ARRHYTHMIA")
    assert record is not None
    assert record.phase_1 == pytest.approx(6.478e-6, rel=1e-3)
    assert record.phase_2 == pytest.approx(2.267e-4, rel=1e-3)


def test_hypercapnia_maps_to_co2_headache_in_report() -> None:
    record = prior_record("HYPERCAPNIA")
    assert record is not None
    assert record.emcl_name == "Headache - CO2 (ICL64)"
    assert record.phase_1 == pytest.approx(0.02078, rel=1e-3)
    assert record.phase_2 == pytest.approx(0.7272, rel=1e-3)
    assert record.note is not None
    assert "rename" in record.note.lower()


def test_respiratory_infection_lower_phase_values_match_report() -> None:
    record = prior_record("RESPIRATORY_INFECTION_LOWER")
    assert record is not None
    assert record.phase_1 == pytest.approx(0.01054, rel=1e-3)
    assert record.phase_2 == pytest.approx(0.3689, rel=1e-3)


def test_depression_uses_mean_of_sexes() -> None:
    record = prior_record("DEPRESSION")
    assert record is not None
    assert record.rate_per_year == pytest.approx(0.00325)
    assert record.phase_1 == pytest.approx(4.452e-5, rel=1e-2)
    assert record.phase_2 == pytest.approx(1.558e-3, rel=1e-2)


def test_acute_radiation_syndrome_is_spe_conditional() -> None:
    record = prior_record("ACUTE_RADIATION_SYNDROME")
    assert record is not None
    assert record.mechanism == "spe_conditional"
    assert record.phase_1 == pytest.approx(0.05)
    assert record.phase_2 == pytest.approx(0.05)


def test_sa_mechanism_gets_phase_1_boost() -> None:
    for code in SA_CODES:
        assert phase_multiplier(code, PHASE_1_ACUTE_ADAPTATION) == pytest.approx(1.25)


def test_sa_mechanism_gets_phase_2_dampen() -> None:
    for code in SA_CODES:
        assert phase_multiplier(code, PHASE_2_LONG_DURATION) == pytest.approx(0.85)


def test_general_mechanism_is_phase_independent() -> None:
    for code in GENERAL_CODES:
        phase_1_value = phase_multiplier(code, PHASE_1_ACUTE_ADAPTATION)
        phase_2_value = phase_multiplier(code, PHASE_2_LONG_DURATION)
        assert phase_1_value == pytest.approx(phase_2_value)


def test_low_rate_tier_conditions_get_point_eight() -> None:
    for code in LOW_TIER_CODES:
        assert phase_multiplier(code, PHASE_1_ACUTE_ADAPTATION) == pytest.approx(0.8)


def test_high_rate_tier_conditions_get_one() -> None:
    for code in HIGH_TIER_CODES:
        assert phase_multiplier(code, PHASE_1_ACUTE_ADAPTATION) == pytest.approx(1.0)


def test_acute_radiation_syndrome_has_no_phase_effect() -> None:
    phase_1_value = phase_multiplier("ACUTE_RADIATION_SYNDROME", PHASE_1_ACUTE_ADAPTATION)
    phase_2_value = phase_multiplier("ACUTE_RADIATION_SYNDROME", PHASE_2_LONG_DURATION)
    assert phase_1_value == pytest.approx(1.0)
    assert phase_2_value == pytest.approx(1.0)


def test_not_found_codes_always_return_default_multiplier() -> None:
    for code in NOT_FOUND_CODES:
        assert phase_multiplier(code, PHASE_1_ACUTE_ADAPTATION) == pytest.approx(1.0)
        assert phase_multiplier(code, PHASE_2_LONG_DURATION) == pytest.approx(1.0)


def test_no_mission_phase_returns_default_multiplier() -> None:
    for rule in CONDITION_RULES:
        assert phase_multiplier(rule.code, None) == pytest.approx(1.0)


def test_unknown_code_returns_default_multiplier() -> None:
    assert phase_multiplier("NOT_A_REAL_CONDITION", PHASE_1_ACUTE_ADAPTATION) == pytest.approx(1.0)


def test_imm_priors_mapping_is_immutable() -> None:
    with pytest.raises(TypeError):
        IMM_PRIORS["SEPSIS"] = None  # type: ignore[index]


def test_prior_record_is_a_frozen_dataclass() -> None:
    record = prior_record("SEPSIS")
    assert record is not None
    with pytest.raises(Exception):
        record.phase_1 = 1.0  # type: ignore[misc]


def test_prior_record_returns_none_for_unknown_code() -> None:
    assert prior_record("NOT_A_REAL_CONDITION") is None


def test_phase_prior_is_dataclass_type() -> None:
    record = prior_record("SANS")
    assert isinstance(record, PhasePrior)
