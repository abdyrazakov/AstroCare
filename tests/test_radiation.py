"""Tests for astro_brain.radiation: dose-rate and NOAA S-scale flags."""

from __future__ import annotations

from astro_brain.radiation import (
    NOAA_S_CRITICAL,
    NOAA_S_ELEVATED,
    RADIATION_CRITICAL_USVH,
    RADIATION_ELEVATED_USVH,
    radiation_flags,
)


def test_nominal_radiation_has_no_flags(nominal_sample):
    assert radiation_flags(nominal_sample()) == ()


def test_dose_just_below_elevated_has_no_flag(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=RADIATION_ELEVATED_USVH - 0.1)
    assert radiation_flags(sample) == ()


def test_dose_at_elevated_threshold_triggers_elevated(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=RADIATION_ELEVATED_USVH)
    flags = radiation_flags(sample)
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == "RADIATION_ELEVATED"
    assert flag.severity == "yellow"
    assert flag.value == RADIATION_ELEVATED_USVH
    assert flag.threshold == RADIATION_ELEVATED_USVH


def test_dose_just_below_critical_is_elevated_not_critical(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=RADIATION_CRITICAL_USVH - 0.1)
    flags = radiation_flags(sample)
    assert len(flags) == 1
    assert flags[0].code == "RADIATION_ELEVATED"


def test_dose_at_critical_threshold_triggers_critical(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=RADIATION_CRITICAL_USVH)
    flags = radiation_flags(sample)
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == "RADIATION_CRITICAL"
    assert flag.severity == "red"
    assert flag.value == RADIATION_CRITICAL_USVH
    assert flag.threshold == RADIATION_CRITICAL_USVH


def test_noaa_below_elevated_has_no_flag(nominal_sample):
    sample = nominal_sample(noaa_s_scale=NOAA_S_ELEVATED - 1)
    assert radiation_flags(sample) == ()


def test_noaa_at_elevated_triggers_elevated_with_noaa_as_value(nominal_sample):
    sample = nominal_sample(noaa_s_scale=NOAA_S_ELEVATED)
    flags = radiation_flags(sample)
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == "RADIATION_ELEVATED"
    assert flag.value == NOAA_S_ELEVATED
    assert flag.threshold == NOAA_S_ELEVATED


def test_noaa_at_critical_triggers_critical_with_noaa_as_value(nominal_sample):
    sample = nominal_sample(noaa_s_scale=NOAA_S_CRITICAL)
    flags = radiation_flags(sample)
    assert len(flags) == 1
    flag = flags[0]
    assert flag.code == "RADIATION_CRITICAL"
    assert flag.value == NOAA_S_CRITICAL
    assert flag.threshold == NOAA_S_CRITICAL


def test_noaa_critical_overrides_dose_only_elevated(nominal_sample):
    # Dose alone is only elevated-level, but NOAA alone is critical: critical wins.
    sample = nominal_sample(radiation_dose_rate=RADIATION_ELEVATED_USVH, noaa_s_scale=NOAA_S_CRITICAL)
    flags = radiation_flags(sample)
    assert len(flags) == 1
    assert flags[0].code == "RADIATION_CRITICAL"


def test_dose_critical_and_noaa_elevated_never_both(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=RADIATION_CRITICAL_USVH, noaa_s_scale=NOAA_S_ELEVATED)
    flags = radiation_flags(sample)
    assert len(flags) == 1
    assert flags[0].code == "RADIATION_CRITICAL"
    # Dose tripped critical, so dose (not the NOAA scale) is reported as the value.
    assert flags[0].value == RADIATION_CRITICAL_USVH


def test_dose_and_noaa_both_critical_still_only_one_flag(nominal_sample):
    sample = nominal_sample(radiation_dose_rate=RADIATION_CRITICAL_USVH, noaa_s_scale=NOAA_S_CRITICAL)
    flags = radiation_flags(sample)
    assert len(flags) == 1
    assert flags[0].code == "RADIATION_CRITICAL"
