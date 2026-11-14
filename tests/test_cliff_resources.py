"""Tests for astro_brain.cliff_resources: CliFF Essential resource tables.

Counts below are the number of Essential-resource items transcribed from
docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md sections 5.2-5.10 for
each condition; see that document for the source RT/CRT prose per condition.
This module is data-only and is not wired into resources.py / conditions.py.
"""

from __future__ import annotations

import re

import pytest

from astro_brain import resources as legacy_resources
from astro_brain.cliff_resources import (
    CliffResource,
    LEGACY_CODE_MAP,
    NON_RT_CANONICAL_CODES,
    canonical_code,
    essential_for,
)

UPPER_SNAKE = re.compile(r"^[A-Z][A-Z0-9_]*$")

# (condition code, expected item count transcribed from the report)
EXPECTED_COUNTS = {
    "HYPOVOLEMIC_SHOCK": 35,  # report 5.2: 19 airway + 10 circulation + 6 meds/consumables
    "SEPSIS": 41,  # report 5.3: 20 airway + 11 circulation/diagnostic + 10 meds/consumables
    "ACUTE_RADIATION_SYNDROME": 20,  # report 5.4
    "CARDIAC_ARRHYTHMIA": 8,  # report 5.5
    "SLEEP_DISORDER": 1,  # report 5.6: Zolpidem only
    "DEPRESSION": 3,  # report 5.7
    "CO2_HEADACHE": 3,  # report 5.8 (CO2_HEADACHE)
    "SANS": 4,  # report 5.9: CRT prose, no RT, no published counts
    "RESPIRATORY_INFECTION_LOWER": 5,  # report 5.10
    "ALTITUDE_SICKNESS": 0,  # report 5.11: NOT FOUND
    "NUTRITIONAL_DEFICIT": 0,  # report 5.11: NOT FOUND
}

NO_RT_CODES = ("ALTITUDE_SICKNESS", "NUTRITIONAL_DEFICIT")


@pytest.mark.parametrize("code, expected_count", EXPECTED_COUNTS.items())
def test_essential_item_count_matches_report(code: str, expected_count: int) -> None:
    assert len(essential_for(code)) == expected_count


def test_no_rt_conditions_are_empty() -> None:
    for code in NO_RT_CODES:
        assert essential_for(code) == ()


def test_sans_items_have_no_units() -> None:
    for item in essential_for("SANS"):
        assert item.best_case_units is None
        assert item.worst_case_units is None


def test_fractional_units_stay_float() -> None:
    ketamine_items = [item for item in essential_for("HYPOVOLEMIC_SHOCK") if item.code == "KETAMINE_50MG"]
    assert len(ketamine_items) == 1
    assert ketamine_items[0].worst_case_units == pytest.approx(0.3)


def test_zero_slash_one_units_are_ints() -> None:
    ambu_items = [item for item in essential_for("HYPOVOLEMIC_SHOCK") if item.code == "AMBU_BAG_MASK"]
    assert len(ambu_items) == 1
    assert ambu_items[0].best_case_units == 0
    assert ambu_items[0].worst_case_units == 1


def test_every_item_is_a_cliff_resource() -> None:
    for code in EXPECTED_COUNTS:
        for item in essential_for(code):
            assert isinstance(item, CliffResource)


def test_canonical_codes_are_upper_snake() -> None:
    for code in EXPECTED_COUNTS:
        for item in essential_for(code):
            assert UPPER_SNAKE.match(item.code), item.code


def test_canonical_codes_are_internally_consistent() -> None:
    """The same canonical code must always name the same real-world item."""
    names_by_code: dict[str, set[str]] = {}
    for code in EXPECTED_COUNTS:
        for item in essential_for(code):
            names_by_code.setdefault(item.code, set()).add(item.name)
    for code, names in names_by_code.items():
        assert len(names) == 1, f"{code} used for conflicting names: {names}"


def test_categories_are_from_the_allowed_set() -> None:
    allowed = {"airway", "circulation", "medication", "diagnostic", "procedure", "environmental"}
    for code in EXPECTED_COUNTS:
        for item in essential_for(code):
            assert item.category in allowed


def test_unknown_condition_returns_empty_tuple() -> None:
    assert essential_for("NOT_A_REAL_CONDITION") == ()


def test_legacy_map_resolves_every_code_used_in_resources_py() -> None:
    used_codes: set[str] = set()
    for codes in legacy_resources.RESOURCES_BY_CONDITION.values():
        used_codes.update(codes)
    missing = used_codes - set(LEGACY_CODE_MAP)
    assert not missing, f"LEGACY_CODE_MAP is missing: {missing}"


def test_legacy_map_honest_mappings_point_at_real_canonical_codes() -> None:
    all_canonical_codes = {
        item.code
        for code in EXPECTED_COUNTS
        for item in essential_for(code)
    } | NON_RT_CANONICAL_CODES
    for legacy_code, target in LEGACY_CODE_MAP.items():
        if target is not None:
            assert target in all_canonical_codes, f"{legacy_code} -> {target} is not a transcribed code"


def test_canonical_code_helper_matches_the_map() -> None:
    assert canonical_code("IV_FLUIDS") == "IV_FLUID_1L"
    assert canonical_code("SLEEP_AID") == "ZOLPIDEM_5MG"
    assert canonical_code("ORAL_REHYDRATION_SALTS") is None


def test_canonical_code_helper_unknown_legacy_code_returns_none() -> None:
    assert canonical_code("NOT_A_REAL_LEGACY_CODE") is None


def test_cliff_resource_is_frozen() -> None:
    item = essential_for("SLEEP_DISORDER")[0]
    with pytest.raises(Exception):
        item.name = "mutated"  # type: ignore[misc]


def test_legacy_code_map_is_immutable() -> None:
    with pytest.raises(TypeError):
        LEGACY_CODE_MAP["NEW_CODE"] = "X"  # type: ignore[index]
