"""Cumulative-dose boundaries, optional input validation and end-to-end flags."""

import pytest

from astro_brain.contract import ContractError, parse_sample
from astro_brain.mock import ANOMALIES, Step, apply_anomaly, nominal_raw
from astro_brain.dashboard import build_brain
from astro_brain.qa import evaluate
from astro_brain.radiation import radiation_flags
from astro_brain.scoring import assess

# Requested NASA limits; source and unit assumption tracked in docs/EVIDENCE.md.
LIMITS = (
    ("radiation_dose_30day_msv", "RADIATION_30DAY_LIMIT", 250.0),
    ("radiation_dose_career_msv", "RADIATION_CAREER_LIMIT", 600.0),
)


@pytest.mark.parametrize("field,code,limit", LIMITS)
@pytest.mark.parametrize("fraction,severity", [
    (0, None), (0.499, None), (0.5, "yellow"), (0.999, "yellow"),
    (1.0, "red"), (1.1, "red"),
])
def test_cumulative_limit_boundaries(nominal_sample, field, code, limit, fraction, severity):
    sample = nominal_sample(**{field: limit * fraction})
    flags = radiation_flags(sample)
    if severity is None:
        assert flags == ()
        return
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == code
    assert flag.severity == severity
    assert flag.value == limit * fraction
    assert flag.threshold == limit * (0.5 if severity == "yellow" else 1.0)
    assert f"{fraction:.0%}" in flag.message
    assert assess(sample).alert_level == severity


@pytest.mark.parametrize("field,code,limit", LIMITS)
@pytest.mark.parametrize("value", [-1, True, False, float("nan"), float("inf"), "10"])
def test_invalid_cumulative_doses_rejected(field, code, limit, value):
    raw = {**nominal_raw("test"), field: value}
    with pytest.raises(ContractError, match=field):
        parse_sample(raw)


@pytest.mark.parametrize("field,code,limit", LIMITS)
@pytest.mark.parametrize("value", [None, 0, 12.5])
def test_optional_doses_accept_null_zero_and_float(field, code, limit, value):
    sample = parse_sample({**nominal_raw("test"), field: value})
    assert getattr(sample, field) == value


def test_absent_doses_default_to_none_without_cumulative_flags():
    raw = nominal_raw("test")
    for field, _, _ in LIMITS:
        raw.pop(field, None)
    sample = parse_sample(raw)
    assert all(getattr(sample, field) is None for field, _, _ in LIMITS)
    assert radiation_flags(sample) == ()


def test_limits_emit_once_each_after_existing_radiation_flags(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=1500, radiation_dose_30day_msv=250,
                            radiation_dose_career_msv=600, sleep_hours=4)
    result = assess(sample)
    assert [flag.code for flag in result.flags] == [
        "RADIATION_CRITICAL", "RADIATION_30DAY_LIMIT", "RADIATION_CAREER_LIMIT", "SLEEP_DEFICIT",
    ]
    assert result.alert_level == "red"


@pytest.mark.parametrize("name,code,level", [
    ("dose_30day_warning", "RADIATION_30DAY_LIMIT", "yellow"),
    ("career_limit_exceeded", "RADIATION_CAREER_LIMIT", "red"),
])
def test_new_anomalies_pass_scoring_pipeline_and_qa(name, code, level):
    anomaly = ANOMALIES[name]
    assert anomaly.expected_level == level
    assert anomaly.expected_codes == frozenset({code})
    raw = apply_anomaly(nominal_raw("test"), name)
    result = assess(parse_sample(raw))
    assert result.alert_level == level
    assert result.flag_codes() == (code,)
    output = build_brain(offline=True).process(raw)
    assert evaluate(Step(0, raw, name), output).passed
    assert code not in output["doctorRecommendation"]  # Specific plain-language advice.


def test_nominal_mock_supplies_background_doses():
    raw = nominal_raw("test")
    assert raw["radiation_dose_30day_msv"] == 15.0
    assert raw["radiation_dose_career_msv"] == 120.0
    assert assess(parse_sample(raw)).flags == ()
