"""Evidence coverage for every reachable flag and its serialized output."""

from pathlib import Path

import pytest

from astro_brain.contract import parse_sample
from astro_brain.dashboard import build_brain
from astro_brain.flags import Flag
from astro_brain.mock import nominal_raw
from astro_brain.scoring import assess

TRIGGERS = {
    "HR_HIGH": {"hr": 125},
    "HR_LOW": {"hr": 35},
    "SPO2_LOW": {"spo2": 92},
    "BP_LOW": {"bp": {"systolic": 95, "diastolic": 60}},
    "BP_HIGH": {"bp": {"systolic": 220, "diastolic": 80}},
    "TEMP_HIGH": {"temp_c": 39.5},
    "TEMP_LOW": {"temp_c": 34.5},
    "RESP_HIGH": {"resp_rate": 22},
    "RESP_LOW": {"resp_rate": 7},
    "CONSCIOUSNESS_ALTERED": {"consciousness": "altered"},
    "NEWS2_MEDIUM": {"spo2": 89},
    "NEWS2_HIGH": {"hr": 140, "spo2": 89, "resp_rate": 26},
    "RADIATION_ELEVATED": {"radiation_dose_rate": 150},
    "RADIATION_CRITICAL": {"radiation_dose_rate": 1500},
    "RADIATION_30DAY_LIMIT": {"bfo_dose_30day_mgy_eq": 250},
    "RADIATION_CAREER_LIMIT": {"radiation_dose_career_msv": 600},
    "EXERCISE_DEFICIT": {"exercise_minutes_today": 0},
    "CALORIC_DEFICIT": {"caloric_intake": 0},
    "CALORIC_LOW": {"caloric_intake": 2400},
    "SLEEP_DEFICIT": {"sleep_hours": 4},
    "LOW_MOOD": {"mood_score": 3},
    "CABIN_CO2_ELEVATED": {"cabin_ppco2_mmhg": 3.0},
    "CABIN_CO2_HIGH": {"cabin_ppco2_mmhg": 7.6},
    "PVT_SLOW": {"pvt_slowest10_rt_ms": 501},
    "IOP_HIGH": {"iop_mmhg": 22},
}


@pytest.mark.parametrize("code,overrides", TRIGGERS.items())
def test_assess_and_pipeline_have_evidence_for_each_flag(code, overrides):
    from astro_brain.evidence import EVIDENCE_BY_CODE

    raw = {**nominal_raw("test"), **overrides}
    assessment = assess(parse_sample(raw))
    assert code in assessment.flag_codes()
    for flag in assessment.flags:
        assert isinstance(flag.evidence, str) and flag.evidence.strip()
        assert flag.evidence == EVIDENCE_BY_CODE[flag.code]
    output = build_brain(offline=True).process(raw)
    for detail in output["flagDetails"]:
        assert detail["evidenceRef"] == EVIDENCE_BY_CODE[detail["code"]]


def test_evidence_mapping_and_document_cover_all_twenty_codes():
    from astro_brain.evidence import EVIDENCE_BY_CODE

    assert len(EVIDENCE_BY_CODE) == 25
    assert set(EVIDENCE_BY_CODE) == set(TRIGGERS)
    document = Path(__file__).resolve().parents[1] / "docs" / "EVIDENCE.md"
    rows = {line.split("|")[1].strip().strip("`") for line in document.read_text().splitlines()
            if line.startswith("|")}
    assert set(EVIDENCE_BY_CODE) <= rows


def test_flag_evidence_is_optional_and_serializes_explicit_reference():
    flag = Flag("CUSTOM", "yellow", "message")
    assert flag.evidence is None
    assert flag.to_dict()["evidenceRef"] is None
    assert Flag("CUSTOM", "red", "message", None, None, "custom source").to_dict()[
        "evidenceRef"
    ] == "custom source"


def test_evidence_mapping_is_read_only():
    from astro_brain.evidence import EVIDENCE_BY_CODE

    with pytest.raises(TypeError):
        EVIDENCE_BY_CODE["LOW_MOOD"] = "unreviewed"
