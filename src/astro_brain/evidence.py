"""Central, immutable source identifiers; verification details: docs/EVIDENCE.md."""

from types import MappingProxyType

NEWS2_REF = "RCP NEWS2 2017, Charts 1–2 (pp.29–30); flag colors are design choices"
RADIATION_RATE_REF = (
    "Design thresholds; NOAA SWPC S2/S3; ISS background 12–30 µSv/h — VERIFY"
)
RADIATION_30DAY_REF = (
    "NASA-STD-3001 Vol.1 Rev C, Table 4.8-1; mSv/BFO mGy-Eq proxy — ASSUMPTION"
)
RADIATION_CAREER_REF = "NASA-STD-3001 Vol.1 Rev C, §4.8.2 [V1 4030]"
SLEEP_REF = "Barger et al. 2014, Lancet Neurol, Table 2; 6 h cutoff is a design choice"
CALORIC_REF = "JSC-63555 Nutritional Requirements — VERIFY; 70% cutoff is a design choice"
EXERCISE_REF = "ISS MORD exercise prescription — VERIFY; 50% cutoff is a design choice"
MOOD_REF = "Ad hoc scale; planned replacement by PHQ-2 (Kroenke 2003), not implemented"

EVIDENCE_BY_CODE = MappingProxyType({
    "HR_HIGH": NEWS2_REF,
    "HR_LOW": NEWS2_REF,
    "SPO2_LOW": NEWS2_REF,
    "BP_LOW": NEWS2_REF,
    "BP_HIGH": NEWS2_REF,
    "TEMP_HIGH": NEWS2_REF,
    "TEMP_LOW": NEWS2_REF,
    "RESP_HIGH": NEWS2_REF,
    "RESP_LOW": NEWS2_REF,
    "CONSCIOUSNESS_ALTERED": NEWS2_REF,
    "NEWS2_MEDIUM": NEWS2_REF,
    "NEWS2_HIGH": NEWS2_REF,
    "RADIATION_ELEVATED": RADIATION_RATE_REF,
    "RADIATION_CRITICAL": RADIATION_RATE_REF,
    "RADIATION_30DAY_LIMIT": RADIATION_30DAY_REF,
    "RADIATION_CAREER_LIMIT": RADIATION_CAREER_REF,
    "EXERCISE_DEFICIT": EXERCISE_REF,
    "CALORIC_DEFICIT": CALORIC_REF,
    "SLEEP_DEFICIT": SLEEP_REF,
    "LOW_MOOD": MOOD_REF,
})
