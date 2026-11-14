"""Central, immutable source identifiers; verification details: docs/EVIDENCE.md."""

from types import MappingProxyType

NEWS2_REF = "RCP NEWS2 2017, Charts 1–2 (pp.29–30); flag colors are design choices"
RADIATION_RATE_REF = "Design thresholds; NOAA SWPC S2/S3; ISS 0.2–0.5 mSv/day — CONFLICT"
RADIATION_30DAY_REF = "NASA-STD-3001 Vol.1 Rev C, Table 4.8-1; BFO mGy-Eq — ASSUMPTION"
RADIATION_CAREER_REF = "NASA-STD-3001 Vol.1 Rev C, §4.8.2; NASA effective dose — VERIFIED"
SLEEP_REF = "Barger et al. 2014, Lancet Neurol, Table 2; 6 h cutoff is a design choice"
CALORIC_REF = "JSC-63555 Energy intake operating bands; 80/90% cutoffs — VERIFIED"
CALORIC_LOW_REF = "JSC-63555 Energy intake operating bands; 80–90% yellow — VERIFIED"
EXERCISE_REF = "NASA SP-20250000273; NTRS 20110016265; 50% cutoff DESIGN DECISION"
MOOD_REF = "Subjective 1–10 mood scale, unvalidated — DESIGN DECISION"
CO2_ELEVATED_REF = "Law et al. 2014, AsMA; OCHMO-TB-004 — VERIFY"
CO2_HIGH_REF = "ISS Flight Rule B17-5 / OCHMO-TB-004 — VERIFY"
PVT_REF = "Basner & Dinges PVT-B lapse convention — VERIFY"
IOP_REF = "OCHMO/HRP SANS ocular hypertension context — VERIFY"

# ExMC EMCL (JSC-65722) / IMM condition vocabulary, used for names only.
# The likelihood score is a prototype design decision, not the IMM Monte Carlo model.
IMM_LITE_REF = (
    "ExMC EMCL/IMM condition vocabulary (JSC-65722; NASA IMM); "
    "evidence score is a prototype design decision, not a calibrated probability — VERIFY"
)

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
    "CALORIC_LOW": CALORIC_LOW_REF,
    "SLEEP_DEFICIT": SLEEP_REF,
    "LOW_MOOD": MOOD_REF,
    "CABIN_CO2_ELEVATED": CO2_ELEVATED_REF,
    "CABIN_CO2_HIGH": CO2_HIGH_REF,
    "PVT_SLOW": PVT_REF,
    "IOP_HIGH": IOP_REF,
})

CONDITION_EVIDENCE_BY_CODE = MappingProxyType({
    "HYPOVOLEMIC_SHOCK": "EMCL Table 2; ICL116; SMEMCL 2011 — VERIFIED",
    "SEPSIS": "EMCL/IMM vocabulary; weights are prototype — VERIFIED",
    "RESPIRATORY_INFECTION_LOWER": "EMCL Table 2; lower respiratory tract infection — VERIFIED",
    "ALTITUDE_SICKNESS": "EMCL Table 2; altitude sickness — VERIFIED",
    "ACUTE_RADIATION_SYNDROME": "EMCL/IMM vocabulary; weights are prototype — VERIFIED",
    "CARDIAC_ARRHYTHMIA": "SMEMCL 2011 priority condition — VERIFIED",
    "SLEEP_DISORDER": "NASA IMM overview; weights are prototype — VERIFIED",
    "DEPRESSION": "NASA IMM overview; weights are prototype — VERIFIED",
    "NUTRITIONAL_DEFICIT": "NASA Appendix E; weights are prototype — VERIFIED",
})
