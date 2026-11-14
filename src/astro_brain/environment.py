"""Cabin-environment scoring rules."""

from __future__ import annotations

from astro_brain.contract import VitalsSample
from astro_brain.evidence import EVIDENCE_BY_CODE
from astro_brain.flags import Flag

CABIN_CO2_ELEVATED_MMHG = 3.0  # NASA-STD-3001 Rev C [V2 6004], 1-hour average; VERIFIED.
CABIN_CO2_HIGH_MMHG = 7.6  # ISS Flight Rule B17-5 / OCHMO-TB-004; VERIFY.


def cabin_co2_flags(sample: VitalsSample) -> tuple[Flag, ...]:
    """Return one CO2 flag, with the high threshold taking precedence."""
    value = sample.cabin_ppco2_mmhg
    if value is None or value < CABIN_CO2_ELEVATED_MMHG:
        return ()
    if value >= CABIN_CO2_HIGH_MMHG:
        return (Flag(
            code="CABIN_CO2_HIGH", severity="red",
            message=(f"Cabin ppCO2 {value:g} mmHg is high; check the scrubber and ventilation, "
                     "move to a better-ventilated module, reduce workload, and contact ground medical."),
            value=value, threshold=CABIN_CO2_HIGH_MMHG,
            evidence=EVIDENCE_BY_CODE["CABIN_CO2_HIGH"],
        ),)
    return (Flag(
        code="CABIN_CO2_ELEVATED", severity="yellow",
        message=f"Cabin ppCO2 {value:g} mmHg is elevated; check ventilation and recheck shortly.",
        value=value, threshold=CABIN_CO2_ELEVATED_MMHG,
        evidence=EVIDENCE_BY_CODE["CABIN_CO2_ELEVATED"],
    ),)
