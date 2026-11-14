"""Tests for astro_brain.vitals_flags: directional component flags + aggregate flag."""

from __future__ import annotations

import dataclasses

import pytest

from astro_brain.contract import BloodPressure
from astro_brain.news2 import compute_news2
from astro_brain.vitals_flags import vitals_flags


def _flags_for(sample):
    return vitals_flags(compute_news2(sample), sample)


def _codes_for(sample):
    return {flag.code for flag in _flags_for(sample)}


def test_nominal_sample_has_no_vitals_flags(nominal_sample):
    assert _flags_for(nominal_sample()) == ()


# --------------------------------------------------------------------------- hr


def test_hr_low_flag(nominal_sample):
    sample = nominal_sample(hr=40)
    flags = [f for f in _flags_for(sample) if f.code.startswith("HR")]
    assert len(flags) == 1
    assert flags[0].code == "HR_LOW"
    assert flags[0].severity == "yellow"
    assert flags[0].value == 40


def test_hr_high_flag(nominal_sample):
    sample = nominal_sample(hr=131)
    flags = [f for f in _flags_for(sample) if f.code.startswith("HR")]
    assert len(flags) == 1
    assert flags[0].code == "HR_HIGH"
    assert flags[0].value == 131


def test_hr_mild_abnormal_score_one_has_no_flag(nominal_sample):
    sample = nominal_sample(hr=45)  # score 1, below the >=2 flag threshold
    assert "HR_HIGH" not in _codes_for(sample)
    assert "HR_LOW" not in _codes_for(sample)


# --------------------------------------------------------------------------- spo2


def test_spo2_low_flag(nominal_sample):
    sample = nominal_sample(spo2=90)
    flags = [f for f in _flags_for(sample) if f.code.startswith("SPO2")]
    assert len(flags) == 1
    assert flags[0].code == "SPO2_LOW"
    assert flags[0].severity == "yellow"
    assert flags[0].value == 90


# --------------------------------------------------------------------------- bp_systolic


def test_bp_low_flag(nominal_sample):
    sample = dataclasses.replace(nominal_sample(), bp=BloodPressure(systolic=90, diastolic=50))
    flags = [f for f in _flags_for(sample) if f.code.startswith("BP")]
    assert len(flags) == 1
    assert flags[0].code == "BP_LOW"
    assert flags[0].value == 90


def test_bp_high_flag(nominal_sample):
    sample = dataclasses.replace(nominal_sample(), bp=BloodPressure(systolic=220, diastolic=100))
    flags = [f for f in _flags_for(sample) if f.code.startswith("BP")]
    assert len(flags) == 1
    assert flags[0].code == "BP_HIGH"
    assert flags[0].value == 220


# --------------------------------------------------------------------------- temp_c


def test_temp_low_flag(nominal_sample):
    sample = nominal_sample(temp_c=35.0)
    flags = [f for f in _flags_for(sample) if f.code.startswith("TEMP")]
    assert len(flags) == 1
    assert flags[0].code == "TEMP_LOW"
    assert flags[0].value == 35.0


def test_temp_high_flag(nominal_sample):
    sample = nominal_sample(temp_c=39.1)
    flags = [f for f in _flags_for(sample) if f.code.startswith("TEMP")]
    assert len(flags) == 1
    assert flags[0].code == "TEMP_HIGH"
    assert flags[0].value == 39.1


# --------------------------------------------------------------------------- resp_rate


def test_resp_low_flag(nominal_sample):
    sample = nominal_sample(resp_rate=8)
    flags = [f for f in _flags_for(sample) if f.code.startswith("RESP")]
    assert len(flags) == 1
    assert flags[0].code == "RESP_LOW"
    assert flags[0].value == 8


def test_resp_high_flag(nominal_sample):
    sample = nominal_sample(resp_rate=25)
    flags = [f for f in _flags_for(sample) if f.code.startswith("RESP")]
    assert len(flags) == 1
    assert flags[0].code == "RESP_HIGH"
    assert flags[0].value == 25


# --------------------------------------------------------------------------- consciousness


def test_consciousness_altered_flag(nominal_sample):
    sample = nominal_sample(consciousness="altered")
    flags = [f for f in _flags_for(sample) if f.code == "CONSCIOUSNESS_ALTERED"]
    assert len(flags) == 1
    assert flags[0].severity == "yellow"
    assert flags[0].value is None
    assert flags[0].threshold is None


# --------------------------------------------------------------------------- supplemental_o2 (no flag of its own)


def test_supplemental_o2_on_contributes_no_direct_flag(nominal_sample):
    sample = nominal_sample(on_supplemental_o2=True)
    result = compute_news2(sample)
    assert result.components["supplemental_o2"] == 2
    assert result.total == 2  # scores but no flag of its own, and too low to hit the aggregate
    assert _flags_for(sample) == ()


# --------------------------------------------------------------------------- aggregate exclusivity


def test_aggregate_medium_when_total_five_to_six_is_total_variant(nominal_sample):
    sample = dataclasses.replace(
        nominal_sample(resp_rate=21, hr=41), bp=BloodPressure(systolic=91, diastolic=60)
    )
    result = compute_news2(sample)
    assert result.total == 5
    codes = _codes_for(sample)
    assert "NEWS2_MEDIUM" in codes
    assert "NEWS2_HIGH" not in codes
    medium = [f for f in _flags_for(sample) if f.code == "NEWS2_MEDIUM"][0]
    assert medium.value == 5
    assert medium.threshold == 5
    assert medium.message == "NEWS2 total 5 is medium risk."


def test_aggregate_high_when_total_at_least_seven(nominal_sample):
    sample = dataclasses.replace(
        nominal_sample(resp_rate=8, hr=111), bp=BloodPressure(systolic=91, diastolic=60)
    )
    codes = _codes_for(sample)
    assert "NEWS2_HIGH" in codes
    assert "NEWS2_MEDIUM" not in codes
    high_flags = [f for f in _flags_for(sample) if f.code == "NEWS2_HIGH"]
    assert high_flags[0].severity == "red"


def test_aggregate_medium_via_single_component_three_is_single_parameter_variant(nominal_sample):
    sample = nominal_sample(hr=131)  # total 3, only hr scores 3
    result = compute_news2(sample)
    assert result.total == 3
    codes = _codes_for(sample)
    assert "NEWS2_MEDIUM" in codes
    assert "NEWS2_HIGH" not in codes
    medium = [f for f in _flags_for(sample) if f.code == "NEWS2_MEDIUM"][0]
    assert medium.value == 3
    assert medium.threshold == 3
    assert medium.message == (
        "NEWS2 single parameter at maximum score (3) — hr — urgent re-check required."
    )


def test_hypoxia_spo2_alone_is_single_parameter_variant(nominal_sample):
    sample = nominal_sample(spo2=89)  # total 3, only spo2 scores 3
    result = compute_news2(sample)
    assert result.total == 3
    medium = [f for f in _flags_for(sample) if f.code == "NEWS2_MEDIUM"][0]
    assert medium.value == 3
    assert medium.threshold == 3
    assert medium.message == (
        "NEWS2 single parameter at maximum score (3) — spo2 — urgent re-check required."
    )
    assert "NEWS2_HIGH" not in _codes_for(sample)


def test_hypotension_systolic_alone_is_single_parameter_variant(nominal_sample):
    sample = dataclasses.replace(nominal_sample(), bp=BloodPressure(systolic=88, diastolic=50))
    result = compute_news2(sample)
    assert result.total == 3
    medium = [f for f in _flags_for(sample) if f.code == "NEWS2_MEDIUM"][0]
    assert medium.value == 3
    assert medium.threshold == 3
    assert medium.message == (
        "NEWS2 single parameter at maximum score (3) — bp_systolic — urgent re-check required."
    )
    assert "NEWS2_HIGH" not in _codes_for(sample)


def test_no_aggregate_flag_when_all_nominal(nominal_sample):
    codes = _codes_for(nominal_sample())
    assert "NEWS2_MEDIUM" not in codes
    assert "NEWS2_HIGH" not in codes
