"""Tests for astro_brain.news2: per-component NEWS2 scoring and risk classification."""

from __future__ import annotations

import pytest

from astro_brain.news2 import (
    News2Result,
    bp_systolic_score,
    compute_news2,
    consciousness_score,
    hr_score,
    resp_rate_score,
    spo2_score,
    supplemental_o2_score,
    temp_c_score,
)


# --------------------------------------------------------------------------- resp_rate


@pytest.mark.parametrize(
    "resp_rate,expected",
    [(8, 3), (9, 1), (11, 1), (12, 0), (20, 0), (21, 2), (24, 2), (25, 3)],
)
def test_resp_rate_score_boundaries(resp_rate, expected):
    assert resp_rate_score(resp_rate) == expected


# --------------------------------------------------------------------------- spo2


@pytest.mark.parametrize(
    "spo2,expected",
    [(91, 3), (92, 2), (93, 2), (94, 1), (95, 1), (96, 0)],
)
def test_spo2_score_boundaries(spo2, expected):
    assert spo2_score(spo2) == expected


# --------------------------------------------------------------------------- supplemental_o2


@pytest.mark.parametrize("on,expected", [(True, 2), (False, 0)])
def test_supplemental_o2_score(on, expected):
    assert supplemental_o2_score(on) == expected


# --------------------------------------------------------------------------- bp_systolic


@pytest.mark.parametrize(
    "systolic,expected",
    [(90, 3), (91, 2), (100, 2), (101, 1), (110, 1), (111, 0), (219, 0), (220, 3)],
)
def test_bp_systolic_score_boundaries(systolic, expected):
    assert bp_systolic_score(systolic) == expected


# --------------------------------------------------------------------------- hr


@pytest.mark.parametrize(
    "hr,expected",
    [(40, 3), (41, 1), (50, 1), (51, 0), (90, 0), (91, 1), (110, 1), (111, 2), (130, 2), (131, 3)],
)
def test_hr_score_boundaries(hr, expected):
    assert hr_score(hr) == expected


# --------------------------------------------------------------------------- consciousness


@pytest.mark.parametrize("consciousness,expected", [("alert", 0), ("altered", 3)])
def test_consciousness_score(consciousness, expected):
    assert consciousness_score(consciousness) == expected


# --------------------------------------------------------------------------- temp_c


@pytest.mark.parametrize(
    "temp_c,expected",
    [
        (35.0, 3),
        (35.1, 1),
        (36.0, 1),
        (36.05, 0),  # mid-band float must land in the lower (36.1-38.0) band, not round up
        (36.1, 0),
        (38.0, 0),
        (38.1, 1),
        (39.0, 1),
        (39.1, 2),
    ],
)
def test_temp_c_score_boundaries(temp_c, expected):
    assert temp_c_score(temp_c) == expected


# --------------------------------------------------------------------------- compute_news2 + risk


def test_compute_news2_all_nominal_totals_zero(nominal_sample):
    result = compute_news2(nominal_sample())
    assert isinstance(result, News2Result)
    assert result.total == 0
    assert result.any_component_three is False
    assert result.risk == "low"
    assert result.components == {
        "resp_rate": 0,
        "spo2": 0,
        "supplemental_o2": 0,
        "bp_systolic": 0,
        "hr": 0,
        "consciousness": 0,
        "temp_c": 0,
    }


def test_compute_news2_single_component_three_is_low_medium(nominal_sample):
    # hr=131 scores 3 alone; total=3, no 5-6 or >=7 band, but any_component_three fires.
    result = compute_news2(nominal_sample(hr=131))
    assert result.total == 3
    assert result.any_component_three is True
    assert result.risk == "low-medium"


def test_compute_news2_total_five_no_three_is_medium(nominal_sample):
    # resp=21(2) + bp=91(2) + hr=41(1) = 5, no single component scores 3.
    from astro_brain.contract import BloodPressure

    import dataclasses

    sample = dataclasses.replace(
        nominal_sample(resp_rate=21, hr=41), bp=BloodPressure(systolic=91, diastolic=60)
    )
    result = compute_news2(sample)
    assert result.total == 5
    assert result.any_component_three is False
    assert result.risk == "medium"


def test_compute_news2_total_six_no_three_is_medium(nominal_sample):
    import dataclasses

    from astro_brain.contract import BloodPressure

    sample = dataclasses.replace(
        nominal_sample(resp_rate=21, hr=111), bp=BloodPressure(systolic=91, diastolic=60)
    )
    result = compute_news2(sample)
    assert result.total == 6
    assert result.any_component_three is False
    assert result.risk == "medium"


def test_compute_news2_total_seven_or_more_is_high_even_with_a_three(nominal_sample):
    import dataclasses

    from astro_brain.contract import BloodPressure

    # resp=8(3) + bp=91(2) + hr=111(2) = 7; any_component_three True but total>=7 wins.
    sample = dataclasses.replace(
        nominal_sample(resp_rate=8, hr=111), bp=BloodPressure(systolic=91, diastolic=60)
    )
    result = compute_news2(sample)
    assert result.total == 7
    assert result.any_component_three is True
    assert result.risk == "high"


def test_news2_result_is_immutable(nominal_sample):
    result = compute_news2(nominal_sample())
    with pytest.raises(Exception):
        result.total = 99  # type: ignore[misc]
    with pytest.raises(TypeError):
        result.components["hr"] = 99  # type: ignore[index]
