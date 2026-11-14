"""Radiation exposure flags (dose rate and NOAA solar radiation storm scale).

Two mutually exclusive severities: ``RADIATION_CRITICAL`` (red) takes
precedence over ``RADIATION_ELEVATED`` (yellow); a sample never carries both.
"""

from __future__ import annotations

from astro_brain.contract import VitalsSample
from astro_brain.flags import Flag

RADIATION_ELEVATED_USVH = 100.0
RADIATION_CRITICAL_USVH = 1000.0
NOAA_S_ELEVATED = 2
NOAA_S_CRITICAL = 3


def _dose_tripped(dose: float, threshold: float) -> bool:
    return dose >= threshold


def _noaa_tripped(noaa: int | None, threshold: int) -> bool:
    return noaa is not None and noaa >= threshold


def _critical_flag(dose: float, noaa: int | None) -> Flag:
    if _dose_tripped(dose, RADIATION_CRITICAL_USVH):
        value, threshold = dose, RADIATION_CRITICAL_USVH
        message = (
            f"Radiation dose rate {dose:.1f} µSv/h is at or above the "
            f"{RADIATION_CRITICAL_USVH:.0f} µSv/h critical threshold; "
            "seek shielding immediately."
        )
    else:
        value, threshold = noaa, NOAA_S_CRITICAL
        message = (
            f"NOAA solar radiation storm scale S{noaa} is at or above the "
            f"critical S{NOAA_S_CRITICAL} threshold; seek shielding immediately."
        )
    return Flag(code="RADIATION_CRITICAL", severity="red", message=message, value=value, threshold=threshold)


def _elevated_flag(dose: float, noaa: int | None) -> Flag:
    if _dose_tripped(dose, RADIATION_ELEVATED_USVH):
        value, threshold = dose, RADIATION_ELEVATED_USVH
        message = (
            f"Radiation dose rate {dose:.1f} µSv/h is above the "
            f"{RADIATION_ELEVATED_USVH:.0f} µSv/h elevated threshold."
        )
    else:
        value, threshold = noaa, NOAA_S_ELEVATED
        message = (
            f"NOAA solar radiation storm scale S{noaa} is at or above the "
            f"elevated S{NOAA_S_ELEVATED} threshold."
        )
    return Flag(code="RADIATION_ELEVATED", severity="yellow", message=message, value=value, threshold=threshold)


def radiation_flags(sample: VitalsSample) -> tuple[Flag, ...]:
    """Radiation flags for ``sample``: never both elevated and critical."""
    dose = sample.radiation_dose_rate
    noaa = sample.noaa_s_scale

    if _dose_tripped(dose, RADIATION_CRITICAL_USVH) or _noaa_tripped(noaa, NOAA_S_CRITICAL):
        return (_critical_flag(dose, noaa),)
    if _dose_tripped(dose, RADIATION_ELEVATED_USVH) or _noaa_tripped(noaa, NOAA_S_ELEVATED):
        return (_elevated_flag(dose, noaa),)
    return ()
