"""v0.3 contract, mapping and adapter coverage."""

import json

import pytest

from astro_brain.adapters.astralis import stream_tick_to_input
from astro_brain.adapters.frontend import to_brain_tick
from astro_brain.body_map import ZONE_IDS, body_systems, zones_for_flag
from astro_brain.contract import ContractError, parse_sample
from astro_brain.environment import cabin_co2_flags
from astro_brain.mock import nominal_raw
from astro_brain.neuro import neuro_flags
from astro_brain.pipeline import Brain
from astro_brain.doctor.layer import DoctorLayer
from astro_brain.doctor.ollama_client import OllamaClient


def core_raw():
    return {"timestamp": "t", "astronaut_id": "A", "hr": 70, "spo2": 98,
            "bp": {"systolic": 120, "diastolic": 80}, "temp_c": 36.5,
            "resp_rate": 14, "radiation_dose_rate": 20.0}


def offline_brain():
    return Brain(doctor=DoctorLayer(OllamaClient(), enabled=False))


def test_lifestyle_fields_can_be_omitted():
    sample = parse_sample(core_raw())
    assert sample.sleep_hours is None and sample.mood_score is None


@pytest.mark.parametrize("field", ["exercise_minutes_today", "required_exercise_minutes", "caloric_intake", "caloric_target"])
def test_lifestyle_pairs_reject_one_sided_input(field):
    raw = core_raw(); raw[field] = 10
    with pytest.raises(ContractError): parse_sample(raw)


@pytest.mark.parametrize("field,value", [
    ("mission_day", 1), ("mission_phase", "PHASE_2_LONG_DURATION"),
    ("cabin_ppco2_mmhg", 3.0), ("iop_mmhg", 22.0), ("hrv_rmssd_ms", 50.0),
    ("pvt_slowest10_rt_ms", 501.0), ("medical_kit", ["O2", "IV_FLUID"]),
])
def test_v03_optional_fields_round_trip(field, value):
    raw = core_raw(); raw[field] = value
    sample = parse_sample(raw)
    assert getattr(sample, field) == (tuple(value) if field == "medical_kit" else value)


@pytest.mark.parametrize("field,value", [("cabin_ppco2_mmhg", -1), ("iop_mmhg", 61),
                                           ("hrv_rmssd_ms", 301), ("pvt_slowest10_rt_ms", 99)])
def test_v03_ranges_are_rejected(field, value):
    raw = core_raw(); raw[field] = value
    with pytest.raises(ContractError, match=field): parse_sample(raw)


@pytest.mark.parametrize("value,code,severity", [(3.0, "CABIN_CO2_ELEVATED", "yellow"),
                                                   (7.6, "CABIN_CO2_HIGH", "red"),
                                                   (20.0, "CABIN_CO2_HIGH", "red")])
def test_co2_boundaries(value, code, severity):
    raw = {**nominal_raw("t"), "cabin_ppco2_mmhg": value}
    flags = cabin_co2_flags(parse_sample(raw))
    assert [(flag.code, flag.severity) for flag in flags] == [(code, severity)]


@pytest.mark.parametrize("value,expected", [(500, ()), (500.1, ("PVT_SLOW",)), (21, ()), (21.1, ("IOP_HIGH",))])
def test_neuro_boundaries(value, expected):
    field = "pvt_slowest10_rt_ms" if value <= 1000 and value != 21 and value != 21.1 else "iop_mmhg"
    raw = {**nominal_raw("t"), field: value}
    assert tuple(flag.code for flag in neuro_flags(parse_sample(raw))) == expected


@pytest.mark.parametrize("code,zone", [("HR_HIGH", "heart"), ("SPO2_LOW", "lungs"),
                                        ("CABIN_CO2_HIGH", "lungs"), ("IOP_HIGH", "eyes"),
                                        ("CALORIC_LOW", "stomach_gi"), ("EXERCISE_DEFICIT", "muscles_legs"),
                                        ("RADIATION_30DAY_LIMIT", "skeleton_upper")])
def test_flag_zone_map(code, zone):
    assert zone in zones_for_flag(code)


def test_body_map_always_has_frontend_zones():
    result = body_systems(({"code": "HR_HIGH", "severity": "yellow"},), ())
    assert tuple(result) == ZONE_IDS and result["heart"] == "yellow"


def test_body_map_condition_confidence_adds_yellow():
    result = body_systems((), ({"code": "SEPSIS", "confidence": 0.5},))
    assert result["heart"] == "yellow" and result["skin_immune"] == "yellow"


def test_frontend_tick_contains_zod_required_keys():
    raw = nominal_raw("t"); output = offline_brain().process(raw)
    tick = to_brain_tick(output, raw, 4)
    assert {"timestamp", "alertLevel", "activeFlags", "rawVitals", "doctorRecommendation"} <= set(tick)
    assert len(tick["rawVitals"]) >= 7 and tick["seq"] == 4


def test_frontend_tick_uses_warning_and_vitals_enum():
    raw = {**nominal_raw("t"), "cabin_ppco2_mmhg": 3.0}
    output = offline_brain().process(raw); flag = to_brain_tick(output, raw, 1)["activeFlags"][0]
    assert flag["severity"] == "warning" and flag["type"] == "vitals"


def test_frontend_tick_marks_ground_medical_step():
    raw = {**nominal_raw("t"), "cabin_ppco2_mmhg": 7.6}
    tick = to_brain_tick(offline_brain().process(raw), raw, 1)
    assert any(step.get("escalation") for step in tick["steps"])


def test_astralis_adapter_units_and_bp():
    tick = {"timestamp": "t", "astronaut_id": "A", "mission_day": 1,
            "mission_phase": "PHASE_1_ACUTE_ADAPTATION", "hr": 70.6, "spo2": 98.4,
            "systolic_bp": 120, "diastolic_bp": 80, "temp_c": 36.5, "resp_rate": 14.4,
            "radiation_dose_rate": 0.013, "cabin_ppco2": 2.4, "iop_mmhg": 15,
            "hrv_rmssd": 40, "pvt_slowest10_rt": 300}
    result = stream_tick_to_input(tick)
    assert result["radiation_dose_rate"] == 13 and result["hr"] == 71
    assert result["bp"] == {"systolic": 120, "diastolic": 80}


def test_astralis_daily_merge():
    tick = {"timestamp": "t", "astronaut_id": "A", "mission_day": 2,
            "mission_phase": "PHASE_2_LONG_DURATION", "hr": 70, "spo2": 98,
            "systolic_bp": 120, "diastolic_bp": 80, "temp_c": 36.5, "resp_rate": 14,
            "radiation_dose_rate": 0.01, "cabin_ppco2": 2, "iop_mmhg": 15,
            "hrv_rmssd": 40, "pvt_slowest10_rt": 300}
    result = stream_tick_to_input(tick, {"sleep_duration_h": 5.5, "ared_exercise_completed": False,
                                         "cumulative_radiation_msv": 10})
    assert result["sleep_hours"] == 5.5 and result["exercise_minutes_today"] == 0
    assert result["radiation_dose_career_msv"] == 10


@pytest.mark.parametrize("code", ["CABIN_CO2_ELEVATED", "CABIN_CO2_HIGH", "PVT_SLOW", "IOP_HIGH"])
def test_new_flags_have_evidence(code):
    from astro_brain.evidence import EVIDENCE_BY_CODE
    assert EVIDENCE_BY_CODE[code]
