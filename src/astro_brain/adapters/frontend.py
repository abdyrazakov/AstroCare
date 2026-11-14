"""Shape AstroBrain output into AstroCare's BrainTick schema."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from astro_brain.body_map import zones_for_flag

_TYPE_PREFIXES = {
    "vitals": ("HR_", "SPO2_", "BP_", "TEMP_", "RESP_", "CONSCIOUSNESS_", "NEWS2_", "CABIN_CO2_", "PVT_", "IOP_"),
    "radiation": ("RADIATION_",), "exercise": ("EXERCISE_",), "nutrition": ("CALORIC_",),
    "sleep": ("SLEEP_",), "mood": ("LOW_MOOD",),
}
_UNITS = {"hr": "bpm", "spo2": "%", "bp": "mmHg", "temp_c": "°C", "resp_rate": "/min",
          "radiation_dose_rate": "µSv/h", "cabin_ppco2": "mmHg", "iop": "mmHg",
          "pvt": "ms", "sleep_hours": "h", "mood": "score", "caloric_intake": "kcal"}


def _flag_type(code: str) -> str:
    return next((kind for kind, prefixes in _TYPE_PREFIXES.items() if code.startswith(prefixes)), "vitals")


def _metric(code: str) -> str:
    if code.startswith("HR_"): return "hr"
    if code.startswith("SPO2_"): return "spo2"
    if code.startswith("BP_"): return "bp_sys"
    if code.startswith("TEMP_"): return "temp_c"
    if code.startswith("RESP_"): return "resp_rate"
    if code.startswith("RADIATION_"): return "radiation_dose_rate"
    if code.startswith("CABIN_CO2_"): return "cabin_ppco2"
    if code == "IOP_HIGH": return "iop"
    if code == "PVT_SLOW": return "pvt"
    if code == "SLEEP_DEFICIT": return "sleep_hours"
    if code == "LOW_MOOD": return "mood"
    if code.startswith("EXERCISE_"): return "exercise_minutes"
    if code.startswith("CALORIC_"): return "caloric_intake"
    return "metric"


def _steps(text: str) -> list[dict[str, object]]:
    sentences = [part.strip() for part in text.split(". ") if part.strip()]
    return [{"text": sentence, **({"escalation": True} if "ground medical" in sentence.lower() else {})}
            for sentence in sentences]


def to_brain_tick(output: Mapping[str, Any], raw_input: Mapping[str, Any], seq: int) -> dict[str, Any]:
    details = output.get("flagDetails", [])
    active = []
    for detail in details:
        code = str(detail["code"]); metric = _metric(code); zones = zones_for_flag(code)
        item = {"type": _flag_type(code), "severity": "critical" if detail["severity"] == "red" else "warning",
                "reason": str(detail["message"]), "triggeredValue": detail.get("value") or 0,
                "metric": metric, "unit": _UNITS.get(metric, "")}
        if zones: item["zone"] = zones[0]
        if isinstance(detail.get("threshold"), (int, float)): item["threshold"] = detail["threshold"]
        active.append(item)
    raw = {key: value for key, value in raw_input.items() if isinstance(value, (int, float)) and not isinstance(value, bool)}
    vitals = {"hr": raw_input["hr"], "spo2": raw_input["spo2"], "temp_c": raw_input["temp_c"],
              "resp_rate": raw_input["resp_rate"], "radiation_dose_rate": raw_input["radiation_dose_rate"],
              "bp_sys": raw_input["bp"]["systolic"], "bp_dia": raw_input["bp"]["diastolic"]}
    vitals.update(raw)
    if raw_input.get("radiation_dose_career_msv") is not None:
        vitals["radiation_cumulative_msv"] = raw_input["radiation_dose_career_msv"]
    result = {"timestamp": output["timestamp"], "alertLevel": output["alertLevel"], "activeFlags": active,
              "rawVitals": vitals, "doctorRecommendation": output["doctorRecommendation"], "seq": seq,
              "astronautId": output.get("astronautId", raw_input.get("astronaut_id")),
              "steps": _steps(output["doctorRecommendation"]), **{key: output[key] for key in
              ("likelyConditions", "bodySystems", "news2Score", "flagDetails", "doctorSource") if key in output}}
    if raw_input.get("mission_day") is not None: result["missionDay"] = raw_input["mission_day"]
    if raw_input.get("radiation_dose_career_msv") is not None:
        result["radiation_cumulative_msv"] = raw_input["radiation_dose_career_msv"]
    return result
