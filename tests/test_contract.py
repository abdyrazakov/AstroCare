"""Tests for astro_brain.contract: input-contract validation (parse_sample)."""

import dataclasses

import pytest

from astro_brain.contract import BloodPressure, ContractError, VitalsSample, parse_sample

REQUIRED_FIELDS = (
    "timestamp", "astronaut_id", "hr", "spo2", "bp", "temp_c", "resp_rate",
    "radiation_dose_rate",
)


def nominal_sample() -> dict:
    """A fresh, contract-valid sample (new dict every call so tests can mutate copies)."""
    return {
        "timestamp": "2026-11-14T10:00:00Z",
        "astronaut_id": "ASTRO-01",
        "hr": 72,
        "spo2": 98,
        "bp": {"systolic": 120, "diastolic": 80},
        "temp_c": 36.8,
        "resp_rate": 14,
        "radiation_dose_rate": 20.5,
        "exercise_minutes_today": 90,
        "required_exercise_minutes": 120,
        "caloric_intake": 2600,
        "caloric_target": 2800,
        "sleep_hours": 7.5,
        "mood_score": 8,
    }


def with_field(name: str, value: object) -> dict:
    return {**nominal_sample(), name: value}


# --------------------------------------------------------------------------- happy path


def test_parse_nominal_sample_returns_typed_vitals_sample():
    # Arrange
    raw = nominal_sample()

    # Act
    sample = parse_sample(raw)

    # Assert
    assert isinstance(sample, VitalsSample)
    assert sample.timestamp == "2026-11-14T10:00:00Z"
    assert sample.astronaut_id == "ASTRO-01"
    assert sample.hr == 72
    assert sample.spo2 == 98
    assert sample.bp == BloodPressure(systolic=120, diastolic=80)
    assert sample.temp_c == 36.8
    assert sample.resp_rate == 14
    assert sample.radiation_dose_rate == 20.5
    assert sample.exercise_minutes_today == 90
    assert sample.required_exercise_minutes == 120
    assert sample.caloric_intake == 2600
    assert sample.caloric_target == 2800
    assert sample.sleep_hours == 7.5
    assert sample.mood_score == 8


def test_optional_fields_use_contract_defaults_when_absent():
    # Arrange
    raw = nominal_sample()

    # Act
    sample = parse_sample(raw)

    # Assert
    assert sample.on_supplemental_o2 is False
    assert sample.consciousness == "alert"
    assert sample.noaa_s_scale is None


def test_optional_fields_are_parsed_when_present():
    # Arrange
    raw = {
        **nominal_sample(),
        "on_supplemental_o2": True,
        "consciousness": "altered",
        "noaa_s_scale": 2,
    }

    # Act
    sample = parse_sample(raw)

    # Assert
    assert sample.on_supplemental_o2 is True
    assert sample.consciousness == "altered"
    assert sample.noaa_s_scale == 2


def test_unknown_extra_keys_are_ignored():
    # Arrange
    raw = {**nominal_sample(), "future_field": "whatever", "hrv_ms": 42}

    # Act
    sample = parse_sample(raw)

    # Assert
    assert sample.hr == 72
    assert not hasattr(sample, "future_field")


def test_parsed_sample_is_immutable():
    # Arrange
    sample = parse_sample(nominal_sample())

    # Act / Assert
    with pytest.raises(dataclasses.FrozenInstanceError):
        sample.hr = 10  # type: ignore[misc]


def test_integer_valued_float_is_accepted_for_int_field():
    # Arrange
    raw = with_field("hr", 72.0)

    # Act
    sample = parse_sample(raw)

    # Assert
    assert sample.hr == 72
    assert isinstance(sample.hr, int)


def test_contract_error_is_a_value_error():
    assert issubclass(ContractError, ValueError)


# --------------------------------------------------------------------------- top-level shape


@pytest.mark.parametrize("raw", [None, 42, "text", [1, 2], True])
def test_non_object_sample_is_rejected(raw):
    # Act / Assert
    with pytest.raises(ContractError, match="object"):
        parse_sample(raw)


# --------------------------------------------------------------------------- missing fields


@pytest.mark.parametrize("field", REQUIRED_FIELDS)
def test_missing_required_field_is_rejected_naming_the_field(field):
    # Arrange
    raw = nominal_sample()
    del raw[field]

    # Act / Assert
    with pytest.raises(ContractError, match=field) as exc_info:
        parse_sample(raw)
    assert "missing" in str(exc_info.value).lower()


# --------------------------------------------------------------------------- wrong types


@pytest.mark.parametrize(
    "field",
    [
        "hr",
        "spo2",
        "temp_c",
        "resp_rate",
        "radiation_dose_rate",
        "exercise_minutes_today",
        "required_exercise_minutes",
        "caloric_intake",
        "caloric_target",
        "sleep_hours",
        "mood_score",
    ],
)
def test_bool_is_rejected_as_number(field):
    # Arrange
    raw = with_field(field, True)

    # Act / Assert
    with pytest.raises(ContractError, match=field):
        parse_sample(raw)


def test_bool_is_rejected_inside_blood_pressure():
    # Arrange
    raw = with_field("bp", {"systolic": True, "diastolic": 80})

    # Act / Assert
    with pytest.raises(ContractError, match="systolic"):
        parse_sample(raw)


def test_non_integer_float_is_rejected_for_int_field():
    # Arrange
    raw = with_field("hr", 72.5)

    # Act / Assert
    with pytest.raises(ContractError, match="hr"):
        parse_sample(raw)


@pytest.mark.parametrize("value", ["72", None, [72], {"v": 72}])
def test_non_numeric_value_is_rejected_for_int_field(value):
    # Arrange
    raw = with_field("hr", value)

    # Act / Assert
    with pytest.raises(ContractError, match="hr"):
        parse_sample(raw)


@pytest.mark.parametrize("value", ["36.6", None, [36.6]])
def test_non_numeric_value_is_rejected_for_number_field(value):
    # Arrange
    raw = with_field("temp_c", value)

    # Act / Assert
    with pytest.raises(ContractError, match="temp_c"):
        parse_sample(raw)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_number_is_rejected(value):
    # Arrange
    raw = with_field("radiation_dose_rate", value)

    # Act / Assert
    with pytest.raises(ContractError, match="radiation_dose_rate"):
        parse_sample(raw)


@pytest.mark.parametrize("field", ["timestamp", "astronaut_id"])
@pytest.mark.parametrize("value", ["", 123, None, True])
def test_string_fields_require_non_empty_string(field, value):
    # Arrange
    raw = with_field(field, value)

    # Act / Assert
    with pytest.raises(ContractError, match=field):
        parse_sample(raw)


@pytest.mark.parametrize("value", ["yes", 1, 0, None])
def test_on_supplemental_o2_must_be_bool(value):
    # Arrange
    raw = with_field("on_supplemental_o2", value)

    # Act / Assert
    with pytest.raises(ContractError, match="on_supplemental_o2"):
        parse_sample(raw)


# --------------------------------------------------------------------------- range boundaries


@pytest.mark.parametrize(
    ("field", "lo", "hi"),
    [
        ("hr", 0, 300),
        ("spo2", 0, 100),
        ("resp_rate", 0, 80),
        ("mood_score", 1, 10),
        ("exercise_minutes_today", 0, 1440),
        ("required_exercise_minutes", 1, 1440),
        ("caloric_intake", 0, 20000),
        ("caloric_target", 1, 20000),
    ],
)
class TestIntegerRangeBoundaries:
    def test_min_minus_one_fails(self, field, lo, hi):
        with pytest.raises(ContractError, match=field):
            parse_sample(with_field(field, lo - 1))

    def test_min_passes(self, field, lo, hi):
        assert getattr(parse_sample(with_field(field, lo)), field) == lo

    def test_max_passes(self, field, lo, hi):
        assert getattr(parse_sample(with_field(field, hi)), field) == hi

    def test_max_plus_one_fails(self, field, lo, hi):
        with pytest.raises(ContractError, match=field):
            parse_sample(with_field(field, hi + 1))


@pytest.mark.parametrize(
    ("field", "lo", "hi"),
    [
        ("sleep_hours", 0, 24),
        ("temp_c", 25, 45),
    ],
)
class TestNumberRangeBoundaries:
    def test_below_min_fails(self, field, lo, hi):
        with pytest.raises(ContractError, match=field):
            parse_sample(with_field(field, lo - 0.001))

    def test_min_passes(self, field, lo, hi):
        assert getattr(parse_sample(with_field(field, lo)), field) == lo

    def test_max_passes(self, field, lo, hi):
        assert getattr(parse_sample(with_field(field, hi)), field) == hi

    def test_above_max_fails(self, field, lo, hi):
        with pytest.raises(ContractError, match=field):
            parse_sample(with_field(field, hi + 0.001))


def test_radiation_dose_rate_zero_is_accepted():
    assert parse_sample(with_field("radiation_dose_rate", 0)).radiation_dose_rate == 0.0


def test_radiation_dose_rate_negative_is_rejected():
    with pytest.raises(ContractError, match="radiation_dose_rate"):
        parse_sample(with_field("radiation_dose_rate", -0.1))


def test_radiation_dose_rate_has_no_upper_bound():
    assert parse_sample(with_field("radiation_dose_rate", 50_000)).radiation_dose_rate == 50_000.0


# --------------------------------------------------------------------------- blood pressure


def test_bp_diastolic_greater_than_systolic_is_rejected():
    # Arrange
    raw = with_field("bp", {"systolic": 80, "diastolic": 120})

    # Act / Assert
    with pytest.raises(ContractError, match="diastolic"):
        parse_sample(raw)


def test_bp_diastolic_equal_to_systolic_is_accepted():
    sample = parse_sample(with_field("bp", {"systolic": 100, "diastolic": 100}))
    assert sample.bp == BloodPressure(100, 100)


@pytest.mark.parametrize("value", [120, "120/80", None, [120, 80]])
def test_bp_must_be_an_object(value):
    with pytest.raises(ContractError, match="bp"):
        parse_sample(with_field("bp", value))


@pytest.mark.parametrize("component", ["systolic", "diastolic"])
def test_bp_missing_component_is_rejected_naming_it(component):
    # Arrange
    bp = {"systolic": 120, "diastolic": 80}
    del bp[component]

    # Act / Assert
    with pytest.raises(ContractError, match=component):
        parse_sample(with_field("bp", bp))


@pytest.mark.parametrize("value", [-1, 301])
def test_bp_systolic_out_of_range_is_rejected(value):
    with pytest.raises(ContractError, match="systolic"):
        parse_sample(with_field("bp", {"systolic": value, "diastolic": 0}))


def test_bp_boundaries_are_inclusive():
    assert parse_sample(with_field("bp", {"systolic": 300, "diastolic": 0})).bp == BloodPressure(300, 0)


# --------------------------------------------------------------------------- consciousness / noaa


@pytest.mark.parametrize("value", ["awake", "ALERT", "", None, 1])
def test_bad_consciousness_value_is_rejected(value):
    with pytest.raises(ContractError, match="consciousness"):
        parse_sample(with_field("consciousness", value))


@pytest.mark.parametrize("value", [-1, 6, 2.5, "2", True])
def test_noaa_s_scale_out_of_range_or_wrong_type_is_rejected(value):
    with pytest.raises(ContractError, match="noaa_s_scale"):
        parse_sample(with_field("noaa_s_scale", value))


@pytest.mark.parametrize("value", [0, 5])
def test_noaa_s_scale_boundaries_are_inclusive(value):
    assert parse_sample(with_field("noaa_s_scale", value)).noaa_s_scale == value


def test_noaa_s_scale_explicit_null_is_accepted():
    assert parse_sample(with_field("noaa_s_scale", None)).noaa_s_scale is None
