"""CliFF-backed resource details and legacy-kit compatibility."""
from __future__ import annotations

from astro_brain.cliff_resources import ESSENTIAL_RESOURCES, STATUS_BY_CONDITION, canonical_code, essential_for

NO_RT_STATUS = "no_rt"

RESOURCES_BY_CONDITION = {
    "HYPOVOLEMIC_SHOCK": ("ORAL_REHYDRATION_SALTS", "IV_FLUIDS", "IV_ACCESS_KIT"),
    "SEPSIS": ("ANTIBIOTICS_BROAD_SPECTRUM", "IV_FLUIDS", "THERMOMETER"),
    "RESPIRATORY_INFECTION_LOWER": ("ANTIBIOTICS_BROAD_SPECTRUM", "PULSE_OXIMETER", "SUPPLEMENTAL_O2"),
    "ALTITUDE_SICKNESS": ("SUPPLEMENTAL_O2", "PULSE_OXIMETER"),
    "ACUTE_RADIATION_SYNDROME": ("ANTIEMETICS", "STORM_SHELTER", "DOSIMETER"),
    "CARDIAC_ARRHYTHMIA": ("ECG_MONITOR", "AED", "BETA_BLOCKER"),
    "SLEEP_DISORDER": ("SLEEP_AID", "LIGHT_THERAPY"),
    "DEPRESSION": ("SSRI", "BHP_TELECONSULT"),
    "NUTRITIONAL_DEFICIT": ("NUTRITION_SUPPLEMENTS", "FOOD_RESERVE"),
    "CO2_HEADACHE": ("CO2_SCRUBBER_SPARE", "LIOH_CANISTER", "PORTABLE_CO2_MONITOR"),
    "SANS": ("TONOMETER", "OCT_IMAGER", "VISION_TEST_KIT"),
}


def _canonical_kit(medical_kit: tuple[str, ...] | None) -> set[str] | None:
    if medical_kit is None:
        return None
    known = {item.code for values in ESSENTIAL_RESOURCES.values() for item in values}
    result: set[str] = set()
    for value in medical_kit:
        mapped = canonical_code(value) or value
        if mapped in known:
            result.add(mapped)
    return result


def resource_details(condition: str, medical_kit: tuple[str, ...] | None) -> tuple[dict[str, object], ...]:
    rows = essential_for(condition)
    if not rows:
        return ()
    kit = _canonical_kit(medical_kit)
    return tuple(
        {
            "code": row.code,
            "name": row.name,
            "category": row.category,
            "essentialUnits": {"best": row.best_case_units, "worst": row.worst_case_units},
            "onboard": None if kit is None else row.code in kit,
        }
        for row in rows
    )


def capability(condition: str, details: tuple[dict[str, object], ...]) -> dict[str, object]:
    if STATUS_BY_CONDITION.get(condition) == "NO_RT":
        return {"status": NO_RT_STATUS, "missing": []}
    if not details or details[0]["onboard"] is None:
        return {"status": "unknown", "missing": []}
    missing = [str(item["code"]) for item in details if item["onboard"] is False]
    status = "none" if len(missing) == len(details) else "partial" if missing else "full"
    return {"status": status, "missing": missing}
