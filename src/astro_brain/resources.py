"""Provisional onboard-resource mapping for IMM-lite conditions."""
from __future__ import annotations
from types import MappingProxyType
from typing import Mapping

RESOURCES_BY_CONDITION: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "HYPOVOLEMIC_SHOCK": ("ORAL_REHYDRATION_SALTS", "IV_FLUIDS", "IV_ACCESS_KIT"),
    "SEPSIS": ("ANTIBIOTICS_BROAD_SPECTRUM", "IV_FLUIDS", "THERMOMETER"),
    "RESPIRATORY_INFECTION_LOWER": ("ANTIBIOTICS_BROAD_SPECTRUM", "PULSE_OXIMETER", "SUPPLEMENTAL_O2"),
    "ALTITUDE_SICKNESS": ("SUPPLEMENTAL_O2", "PULSE_OXIMETER"),
    "ACUTE_RADIATION_SYNDROME": ("ANTIEMETICS", "STORM_SHELTER", "DOSIMETER"),
    "CARDIAC_ARRHYTHMIA": ("ECG_MONITOR", "AED", "BETA_BLOCKER"),
    "SLEEP_DISORDER": ("SLEEP_AID", "LIGHT_THERAPY"),
    "DEPRESSION": ("SSRI", "BHP_TELECONSULT"),
    "NUTRITIONAL_DEFICIT": ("NUTRITION_SUPPLEMENTS", "FOOD_RESERVE"),
    "HYPERCAPNIA": ("CO2_SCRUBBER_SPARE", "LIOH_CANISTER", "PORTABLE_CO2_MONITOR"),
    "SANS": ("TONOMETER", "OCT_IMAGER", "VISION_TEST_KIT"),
})


def resource_details(condition: str, medical_kit: tuple[str, ...] | None) -> tuple[dict[str, object], ...]:
    codes = RESOURCES_BY_CONDITION.get(condition, ())
    return tuple({"code": code, "onboard": None if medical_kit is None else code in medical_kit} for code in codes)


def capability(details: tuple[dict[str, object], ...]) -> dict[str, object]:
    if not details or details[0]["onboard"] is None:
        return {"status": "unknown", "missing": []}
    missing = [str(item["code"]) for item in details if item["onboard"] is False]
    if len(missing) == len(details):
        status = "none"
    elif missing:
        status = "partial"
    else:
        status = "full"
    return {"status": status, "missing": missing}
