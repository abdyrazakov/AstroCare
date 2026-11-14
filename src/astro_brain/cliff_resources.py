"""CliFF Essential-resource tables by condition code.

Data-only module: transcribed from docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md
sections 5.2-5.10 (``Essential = Yes`` rows of each CliFF Resource Table, RT),
plus the SANS CRT prose (section 5.9, which has no RT at all). Nothing here is
wired into ``resources.py`` or ``conditions.py``; that wiring happens later.

The CliFF Resource Table (RT) is not the full Capability Resource Table (CRT):
the full CRT lives in an Excel/IMPACT-MD file that is not in the PDF. These
tables therefore describe RT Essential items only, not full capability
coverage; see ``STATUS_BY_CONDITION`` and ``docs/EVIDENCE_IMM.md``.

Units are transcribed exactly as printed: ``"0/1"`` becomes ``(0, 1)``,
fractional values such as ``0.3`` stay ``float``, and ``None`` marks an item
with no published quantity (the SANS CRT-prose items).
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

Units = float | int | None


@dataclass(frozen=True)
class CliffResource:
    """One Essential resource row from a CliFF Resource Table (or CRT prose)."""

    code: str
    name: str
    best_case_units: Units
    worst_case_units: Units
    category: str


def _item(code: str, name: str, best: Units, worst: Units, category: str) -> CliffResource:
    return CliffResource(code=code, name=name, best_case_units=best, worst_case_units=worst, category=category)


# --- HYPOVOLEMIC_SHOCK -- report calls it HYPOVOLEMIA, ICL116 -----------------
# Source: Traumatic Hypovolemic Shock Cliff, 5/11/2020, RT p.7-9.
_HYPOVOLEMIC_SHOCK_ITEMS: tuple[CliffResource, ...] = (
    _item("AMBU_BAG_MASK", "Ambu bag and mask", 0, 1, "airway"),
    _item("ENDOTRACHEAL_STYLET", "Endotracheal stylet", 0, 1, "airway"),
    _item("ENDOTRACHEAL_TUBE", "Endotracheal tube 7.0/8.0", 0, 1, "airway"),
    _item("ETCO2_MONITOR", "EtCO2 monitor", 0, 1, "airway"),
    _item("KING_SGA_TUBE", "King supraglottic airway tube", 0, 1, "airway"),
    _item("LARYNGOSCOPE_BLADE", "Laryngoscope blade", 0, 1, "airway"),
    _item("LARYNGOSCOPE_HANDLE", "Laryngoscope handle", 0, 1, "airway"),
    _item("NASAL_AIRWAY", "Nasal airway 6/7 mm", 0, 1, "airway"),
    _item("ORAL_AIRWAY", "Oral airway", 0, 1, "airway"),
    _item("PEEP_VALVE", "PEEP valve", 0, 1, "airway"),
    _item("SGA_CUE_CARD", "SGA cue card", 0, 1, "airway"),
    _item("SUCTION_CARTRIDGE", "Suction cartridge", 0, 1, "airway"),
    _item("SUCTION_DEVICE", "Suction device", 0, 1, "airway"),
    _item("SUCTION_DEVICE_SYRINGE", "Suction device syringe", 0, 1, "airway"),
    _item("SUCTION_TIP", "Suction tip (mouth)", 0, 1, "airway"),
    _item("SUCTION_TUBING_ET", "Suction tubing, endotracheal", 0, 1, "airway"),
    _item("T_ADAPTER", "T-adapter", 0, 1, "airway"),
    _item("VARIABLE_OXYGEN_SYSTEM", "Variable Oxygen System", 0, 1, "airway"),
    _item("VOS_INTUBATED_HARDWARE", "VOS intubated-patient hardware", 0, 1, "airway"),
    _item("ADRENALINE_1_10000", "Adrenaline 1:10000 10 mL", 0, 4, "medication"),
    _item("BLOOD_OXIMETER", "Blood oximeter", 1, 1, "circulation"),
    _item("BP_CUFF", "Blood pressure cuff", 1, 1, "circulation"),
    _item("BP_MONITOR", "Blood pressure monitor", 1, 1, "circulation"),
    _item("ECG_MONITOR", "ECG monitor", 1, 1, "circulation"),
    _item("ECG_ELECTRODES_12", "Pack of 12 ECG electrodes", 1, 1, "circulation"),
    _item("IV_ADMIN_SET", "IV administration set", 1, 1, "circulation"),
    _item("IV_CATHETER", "IV catheter 18G/20G/22G", 1, 1, "circulation"),
    _item("IV_FLUID_1L", "IV fluid 1 L", 2, 4, "circulation"),
    _item("STETHOSCOPE", "Stethoscope", 1, 1, "circulation"),
    _item("KETAMINE_50MG", "Ketamine 50 mg/mL 10 mL", 0, 0.3, "medication"),
    _item("VALIUM_5MG", "Valium 5 mg/mL 2 mL", 0, 1, "medication"),
    _item("NEEDLE_23G", "Needle 23G", 0, 6, "procedure"),
    _item("SYRINGE_3CC", "Syringe 3cc", 1, 6, "procedure"),
    _item("SYRINGE_10CC", "Syringe 10cc", 0, 1, "procedure"),
    _item("SYRINGE_35CC", "Syringe 35cc", 0, 1, "procedure"),
)

# --- SEPSIS -- ICL84 ----------------------------------------------------------
# Source: Sepsis Cliff, 5/11/2020, RT p.9-11.
_SEPSIS_ITEMS: tuple[CliffResource, ...] = (
    _item("ADRENALINE_1_10000", "Adrenaline 1:10000 10 mL", 0, 4, "medication"),
    _item("AMBU_BAG_MASK", "Ambu bag and mask", 0, 1, "airway"),
    _item("ENDOTRACHEAL_STYLET", "Endotracheal stylet", 0, 1, "airway"),
    _item("ENDOTRACHEAL_TUBE", "Endotracheal tube 7.0/8.0", 0, 1, "airway"),
    _item("ETCO2_MONITOR", "EtCO2 monitor", 0, 1, "airway"),
    _item("KING_SGA_TUBE", "King supraglottic airway tube", 0, 1, "airway"),
    _item("LARYNGOSCOPE_BLADE", "Laryngoscope blade", 0, 1, "airway"),
    _item("LARYNGOSCOPE_HANDLE", "Laryngoscope handle", 0, 1, "airway"),
    _item("NASAL_AIRWAY", "Nasal airway 6/7 mm", 0, 1, "airway"),
    _item("ORAL_AIRWAY", "Oral airway", 0, 1, "airway"),
    _item("PEEP_VALVE", "PEEP valve", 0, 1, "airway"),
    _item("SGA_CUE_CARD", "SGA cue card", 0, 1, "airway"),
    _item("SUCTION_CARTRIDGE", "Suction cartridge", 0, 1, "airway"),
    _item("SUCTION_DEVICE", "Suction device", 0, 1, "airway"),
    _item("SUCTION_DEVICE_SYRINGE", "Suction device syringe", 0, 1, "airway"),
    _item("SUCTION_TIP", "Suction tip (mouth)", 0, 1, "airway"),
    _item("SUCTION_TUBING_ET", "Suction tubing, endotracheal", 0, 1, "airway"),
    _item("T_ADAPTER", "T-adapter", 0, 1, "airway"),
    _item("VARIABLE_OXYGEN_SYSTEM", "Variable Oxygen System", 0, 1, "airway"),
    _item("VOS_INTUBATED_HARDWARE", "VOS intubated-patient hardware", 0, 1, "airway"),
    _item("BLOOD_OXIMETER", "Blood oximeter", 1, 1, "circulation"),
    _item("BP_CUFF", "Blood pressure cuff", 1, 1, "circulation"),
    _item("BP_MONITOR", "Blood pressure monitor", 1, 1, "circulation"),
    _item("ECG_MONITOR", "ECG monitor", 1, 1, "circulation"),
    _item("ECG_ELECTRODES_12", "Pack of 12 ECG electrodes", 1, 1, "circulation"),
    _item("IV_ADMIN_SET", "IV administration set", 1, 1, "circulation"),
    _item("IV_CATHETER", "IV catheter 18G/20G/22G", 1, 1, "circulation"),
    _item("IV_FLUID_1L", "IV fluid 1 L", 2, 4, "circulation"),
    _item("STETHOSCOPE", "Stethoscope", 1, 1, "circulation"),
    _item("ULTRASOUND_GEL", "Ultrasound gel", 2, 2, "diagnostic"),
    _item("ULTRASOUND", "Ultrasound machine", 1, 1, "diagnostic"),
    _item("ERTAPENEM_1G", "Ertapenem 1 g", 1, 3, "medication"),
    _item("KETAMINE_50MG", "Ketamine 50 mg/mL 10 mL", 0, 0.3, "medication"),
    _item("LIDOCAINE_1PCT", "Lidocaine 1% 10 mL", 1, 1, "medication"),
    _item("NEEDLE_23G", "Needle 23G", 1, 6, "procedure"),
    _item("NEEDLE_25G", "Needle 25G", 1, 1, "procedure"),
    _item("SYRINGE_3CC", "Syringe 3cc", 1, 10, "procedure"),
    _item("SYRINGE_10CC", "Syringe 10cc", 0, 1, "procedure"),
    _item("SYRINGE_35CC", "Syringe 35cc", 0, 1, "procedure"),
    _item("ACETAMINOPHEN_325MG", "Tylenol (Acetaminophen) 325 mg", 12, 24, "medication"),
    _item("VALIUM_5MG", "Valium 5 mg/mL 2 mL", 0, 1, "medication"),
)

# --- ACUTE_RADIATION_SYNDROME -- ICL4 -----------------------------------------
# Source: Acute Radiation Syndrome Cliff, 5/11/2020, RT p.6-7.
_ACUTE_RADIATION_SYNDROME_ITEMS: tuple[CliffResource, ...] = (
    _item("BACITRACIN_500U", "Bacitracin 500 units/g", 0, 0.25, "medication"),
    _item("BLOOD_OXIMETER", "Blood oximeter", 1, 1, "circulation"),
    _item("BP_CUFF", "Blood pressure cuff", 1, 1, "circulation"),
    _item("BP_MONITOR", "Blood pressure monitor", 1, 1, "circulation"),
    _item("HYDROMORPHONE_2MG", "Dilaudid 2 mg/mL", 0, 12, "medication"),
    _item("ECG_MONITOR", "ECG monitor", 0, 1, "circulation"),
    _item("ERTAPENEM_1G", "Ertapenem 1 g", 0, 3, "medication"),
    _item("IV_ADMIN_SET", "IV administration set", 0, 1, "circulation"),
    _item("IV_CATHETER", "IV catheter 18G/20G/22G", 0, 1, "circulation"),
    _item("IV_FLUID_1L", "IV fluid 1 L", 0, 4, "circulation"),
    _item("LIDOCAINE_1PCT", "Lidocaine 1% 10 mL", 0, 3, "medication"),
    _item("IBUPROFEN_400MG", "Motrin 400 mg", 3, 0, "medication"),
    _item("NEEDLE_23G", "Needle 23G", 0, 25, "procedure"),
    _item("ECG_ELECTRODES_12", "Pack of 12 ECG electrodes", 0, 1, "circulation"),
    _item("PROMETHAZINE_25MG", "Promethazine 25 mg/mL", 0, 18, "medication"),
    _item("STETHOSCOPE", "Stethoscope", 0, 1, "circulation"),
    _item("SYRINGE_3CC", "Syringe 3cc", 0, 25, "procedure"),
    _item("VALIUM_5MG", "Valium 5 mg/mL 2 mL", 0, 2, "medication"),
    _item("VARIABLE_OXYGEN_SYSTEM", "Variable Oxygen System", 0, 1, "airway"),
    _item("ONDANSETRON_8MG", "Zofran 8 mg", 2, 2, "medication"),
)

# --- CARDIAC_ARRHYTHMIA -- ICL10 ----------------------------------------------
# Source: Atrial Fibrillation/Atrial Flutter Cliff, 5/11/2020, RT p.6.
_CARDIAC_ARRHYTHMIA_ITEMS: tuple[CliffResource, ...] = (
    _item("ASPIRIN_325MG", "Aspirin 325 mg", 0, 3, "medication"),
    _item("BLOOD_OXIMETER", "Blood oximeter", 1, 1, "circulation"),
    _item("BP_CUFF", "Blood pressure cuff", 1, 1, "circulation"),
    _item("BP_MONITOR", "Blood pressure monitor", 1, 1, "circulation"),
    _item("ECG_MONITOR", "ECG monitor", 1, 1, "circulation"),
    _item("METOPROLOL_50MG", "Lopressor (Metoprolol) 50 mg", 0, 12, "medication"),
    _item("ECG_ELECTRODES_12", "Pack of 12 ECG electrodes", 1, 1, "circulation"),
    _item("VARIABLE_OXYGEN_SYSTEM", "Variable Oxygen System", 0, 1, "airway"),
)

# --- SLEEP_DISORDER -- ICL95 Space Adaptation - Insomnia ----------------------
# Source: Insomnia (space adaptation) Cliff, 5/11/2020, RT p.5.
# Note: the RT prose says both Ambien and Sonata are needed (individual choice);
# only Zolpidem (Ambien) has its own RT row. Not silently corrected (see report
# section 8.7 / docs/EVIDENCE_IMM.md).
_SLEEP_DISORDER_ITEMS: tuple[CliffResource, ...] = (
    _item("ZOLPIDEM_5MG", "Zolpidem (Ambien) 5 mg", 1, 2, "medication"),
)

# --- DEPRESSION -- ICL15 BHP - Depression -------------------------------------
# Source: Depression Cliff, 5/11/2020, RT p.5.
_DEPRESSION_ITEMS: tuple[CliffResource, ...] = (
    _item("ARIPIPRAZOLE_5MG", "Abilify (Aripiprazole) 5 mg", 0, 30, "medication"),
    _item("PSYCHOTHERAPY", "Psychotherapy", 1, 1, "procedure"),
    _item("SERTRALINE_50MG", "Zoloft (Sertraline) 50 mg", 60, 60, "medication"),
)

# --- CO2_HEADACHE -- report calls it CO2_HEADACHE, ICL64 -----------------------
# Source: Headache (CO2 induced) Cliff, 5/11/2020, RT p.8.
# Note: EMCL/ICL name is "Headache - CO2" (ICL64), not "Hypercapnia"; a code
# canonical code is CO2_HEADACHE (EMCL ICL64).
_CO2_HEADACHE_ITEMS: tuple[CliffResource, ...] = (
    _item("BP_CUFF", "Blood pressure cuff", 0, 1, "circulation"),
    _item("BP_MONITOR", "Blood pressure monitor", 0, 1, "circulation"),
    _item("ACETAMINOPHEN_325MG", "Tylenol (Acetaminophen) 325 mg", 0, 4, "medication"),
)

# --- SANS -- ICL100 ------------------------------------------------------------
# Source: ICL100_Space Flight Associated Neuro-Ocular Syndrome (Sans) Cliff,
# 9/19/2022, CRT prose p.6. No formal RT exists; no quantities are published,
# so every item below has None for both best- and worst-case units.
_SANS_ITEMS: tuple[CliffResource, ...] = (
    _item("SPACE_ANTICIPATION_GLASSES", "Space anticipation glasses", None, None, "procedure"),
    _item("REPEAT_OPHTHALMIC_TESTING", "Repeat ophthalmic testing", None, None, "procedure"),
    _item("OCT_IMAGER", "OCT imager", None, None, "diagnostic"),
    _item("TONOMETER", "Tonometer (intraocular pressure)", None, None, "diagnostic"),
)

# --- RESPIRATORY_INFECTION_LOWER -- ICL81/82 ----------------------------------
# Source: Respiratory Infection Cliff, 5/11/2020, RT p.6.
_RESPIRATORY_INFECTION_LOWER_ITEMS: tuple[CliffResource, ...] = (
    _item("BENZONATATE_100MG", "Benzonatate 100 mg", 10, 20, "medication"),
    _item("BLOOD_OXIMETER", "Blood oximeter", 1, 1, "circulation"),
    _item("DEXTROMETHORPHAN_15MG", "Dextromethorphan 15 mg", 10, 20, "medication"),
    _item("STETHOSCOPE", "Stethoscope", 1, 1, "circulation"),
    _item("AZITHROMYCIN_250MG", "Zithromax (Azithromycin) 250 mg", 0, 6, "medication"),
)

ESSENTIAL_RESOURCES: MappingProxyType[str, tuple[CliffResource, ...]] = MappingProxyType({
    "HYPOVOLEMIC_SHOCK": _HYPOVOLEMIC_SHOCK_ITEMS,
    "SEPSIS": _SEPSIS_ITEMS,
    "ACUTE_RADIATION_SYNDROME": _ACUTE_RADIATION_SYNDROME_ITEMS,
    "CARDIAC_ARRHYTHMIA": _CARDIAC_ARRHYTHMIA_ITEMS,
    "SLEEP_DISORDER": _SLEEP_DISORDER_ITEMS,
    "DEPRESSION": _DEPRESSION_ITEMS,
    "CO2_HEADACHE": _CO2_HEADACHE_ITEMS,
    "SANS": _SANS_ITEMS,
    "RESPIRATORY_INFECTION_LOWER": _RESPIRATORY_INFECTION_LOWER_ITEMS,
    "ALTITUDE_SICKNESS": (),
    "NUTRITIONAL_DEFICIT": (),
})

SOURCE_BY_CONDITION: MappingProxyType[str, str | None] = MappingProxyType({
    "HYPOVOLEMIC_SHOCK": "Traumatic Hypovolemic Shock Cliff, 5/11/2020, RT p.7-9",
    "SEPSIS": "Sepsis Cliff, 5/11/2020, RT p.9-11",
    "ACUTE_RADIATION_SYNDROME": "Acute Radiation Syndrome Cliff, 5/11/2020, RT p.6-7",
    "CARDIAC_ARRHYTHMIA": "Atrial Fibrillation/Atrial Flutter Cliff, 5/11/2020, RT p.6",
    "SLEEP_DISORDER": "Insomnia (space adaptation) Cliff, 5/11/2020, RT p.5",
    "DEPRESSION": "Depression Cliff, 5/11/2020, RT p.5",
    "CO2_HEADACHE": "Headache (CO2 induced) Cliff, 5/11/2020, RT p.8",
    "SANS": "ICL100_Space Flight Associated Neuro-Ocular Syndrome (Sans) Cliff, 9/19/2022, CRT prose p.6",
    "RESPIRATORY_INFECTION_LOWER": "Respiratory Infection Cliff, 5/11/2020, RT p.6",
    "ALTITUDE_SICKNESS": None,
    "NUTRITIONAL_DEFICIT": None,
})

STATUS_BY_CONDITION: MappingProxyType[str, str] = MappingProxyType({
    "HYPOVOLEMIC_SHOCK": "VERIFIED_RT",
    "SEPSIS": "VERIFIED_RT",
    "ACUTE_RADIATION_SYNDROME": "VERIFIED_RT",
    "CARDIAC_ARRHYTHMIA": "VERIFIED_RT",
    "SLEEP_DISORDER": "VERIFIED_RT",
    "DEPRESSION": "VERIFIED_RT",
    "CO2_HEADACHE": "VERIFIED_RT",
    "SANS": "VERIFIED_CRT_PROSE",
    "RESPIRATORY_INFECTION_LOWER": "VERIFIED_RT",
    "ALTITUDE_SICKNESS": "NO_RT",
    "NUTRITIONAL_DEFICIT": "NO_RT",
})

# Canonical codes that exist only as a legacy-mapping target and are not part
# of any Essential RT/CRT-prose item above: the report explicitly notes these
# are not RT consumables. The portable CO2 monitor (CDM) is an environmental
# diagnostic mentioned only in CliFF prose (report section 6), not an
# Essential RT row for CO2_HEADACHE; it is kept out of ESSENTIAL_RESOURCES so
# that table does not misrepresent it as an RT item.
NON_RT_CANONICAL_CODES: frozenset[str] = frozenset({"PORTABLE_CO2_MONITOR_CDM"})

# Maps the v0.4 provisional codes from resources.RESOURCES_BY_CONDITION to a
# canonical CliFF code above, or to None where no honest mapping exists (the
# legacy code names a concept with no corresponding Essential RT/CRT-prose
# item in the report; never invented). See docs/EVIDENCE_IMM.md for the
# per-code rationale.
LEGACY_CODE_MAP: MappingProxyType[str, str | None] = MappingProxyType({
    "ORAL_REHYDRATION_SALTS": None,
    "IV_FLUIDS": "IV_FLUID_1L",
    "IV_ACCESS_KIT": "IV_CATHETER",
    "ANTIBIOTICS_BROAD_SPECTRUM": "ERTAPENEM_1G",
    "THERMOMETER": None,
    "PULSE_OXIMETER": "BLOOD_OXIMETER",
    "SUPPLEMENTAL_O2": "VARIABLE_OXYGEN_SYSTEM",
    "ANTIEMETICS": "ONDANSETRON_8MG",
    "STORM_SHELTER": None,
    "DOSIMETER": None,
    "ECG_MONITOR": "ECG_MONITOR",
    "AED": None,
    "BETA_BLOCKER": "METOPROLOL_50MG",
    "SLEEP_AID": "ZOLPIDEM_5MG",
    "LIGHT_THERAPY": None,
    "SSRI": "SERTRALINE_50MG",
    "BHP_TELECONSULT": "PSYCHOTHERAPY",
    "NUTRITION_SUPPLEMENTS": None,
    "FOOD_RESERVE": None,
    "CO2_SCRUBBER_SPARE": None,
    "LIOH_CANISTER": None,
    "PORTABLE_CO2_MONITOR": "PORTABLE_CO2_MONITOR_CDM",
    "TONOMETER": "TONOMETER",
    "OCT_IMAGER": "OCT_IMAGER",
    "VISION_TEST_KIT": None,
})


def essential_for(code: str) -> tuple[CliffResource, ...]:
    """Return the transcribed Essential resources for ``code``, or ``()``."""
    return ESSENTIAL_RESOURCES.get(code, ())


def canonical_code(legacy: str) -> str | None:
    """Translate a v0.4 provisional resource code to its canonical CliFF code.

    Returns ``None`` both for an unknown legacy code and for a legacy code
    that has no honest canonical equivalent in the report.
    """
    return LEGACY_CODE_MAP.get(legacy)
