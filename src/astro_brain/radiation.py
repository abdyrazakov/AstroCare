"""Radiation exposure flags (dose rate, NOAA scale and optional cumulative dose).

Two mutually exclusive severities: ``RADIATION_CRITICAL`` (red) takes
precedence over ``RADIATION_ELEVATED`` (yellow); a sample never carries both.
Cumulative limits are independent and follow those existing radiation flags.
"""

from __future__ import annotations

from astro_brain.contract import VitalsSample
from astro_brain.evidence import EVIDENCE_BY_CODE
from astro_brain.flags import Flag

# Legacy design choices, not NASA limits: docs/EVIDENCE.md.
# NOAA S-scale context: https://www.swpc.noaa.gov/noaa-scales-explanation
RADIATION_ELEVATED_USVH = 100.0
RADIATION_CRITICAL_USVH = 1000.0
NOAA_S_ELEVATED = 2
NOAA_S_CRITICAL = 3


# NASA-STD-3001 Vol.1 §4.8.2 [V1 4030]: VERIFIED; docs/EVIDENCE.md.
# https://www.nasa.gov/reference/4-0-human-performance/
CAREER_EFFECTIVE_DOSE_LIMIT_MSV = 600.0
# NASA-STD-3001 Vol.1 Table 4.8-1 (BFO, 30-day): VERIFIED in mGy-Eq.
# https://www.nasa.gov/reference/4-0-human-performance/
# ASSUMPTION: compare mSv input numerically, without an organ/RBE conversion.
THIRTY_DAY_BFO_LIMIT_MGY_EQ = 250.0
# Operational choices, not NASA warning levels: docs/EVIDENCE.md (DESIGN DECISION).
WARN_FRACTION = 0.5
CRITICAL_FRACTION = 1.0


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
    return Flag(
        code="RADIATION_CRITICAL", evidence=EVIDENCE_BY_CODE["RADIATION_CRITICAL"],
        severity="red", message=message, value=value,
        threshold=threshold
    )


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
    return Flag(
        code="RADIATION_ELEVATED", evidence=EVIDENCE_BY_CODE["RADIATION_ELEVATED"],
        severity="yellow", message=message, value=value,
        threshold=threshold
    )


def _instantaneous_flags(sample: VitalsSample) -> tuple[Flag, ...]:
    """Radiation flags for ``sample``: never both elevated and critical."""
    dose = sample.radiation_dose_rate
    noaa = sample.noaa_s_scale

    if _dose_tripped(dose, RADIATION_CRITICAL_USVH) or _noaa_tripped(noaa, NOAA_S_CRITICAL):
        return (_critical_flag(dose, noaa),)
    if _dose_tripped(dose, RADIATION_ELEVATED_USVH) or _noaa_tripped(noaa, NOAA_S_ELEVATED):
        return (_elevated_flag(dose, noaa),)
    return ()


def _limit_flag(dose: float | None, limit: float, code: str, label: str) -> Flag | None:
    if dose is None or dose < limit * WARN_FRACTION:
        return None
    critical = dose >= limit * CRITICAL_FRACTION
    fraction = CRITICAL_FRACTION if critical else WARN_FRACTION
    return Flag(
        code=code, evidence=EVIDENCE_BY_CODE[code],
        severity="red" if critical else "yellow",
        message=f"{label} dose {dose:g} mSv is {dose / limit:.0%} of the limit.",
        value=dose,
        threshold=limit * fraction,
    )


def radiation_flags(sample: VitalsSample) -> tuple[Flag, ...]:
    """Existing rate/NOAA flag followed by at most one flag per cumulative limit."""
    cumulative = (
        _limit_flag(sample.radiation_dose_30day_msv, THIRTY_DAY_BFO_LIMIT_MGY_EQ,
                    "RADIATION_30DAY_LIMIT", "30-day (BFO proxy; assumed unit equivalence)"),
        _limit_flag(sample.radiation_dose_career_msv, CAREER_EFFECTIVE_DOSE_LIMIT_MSV,
                    "RADIATION_CAREER_LIMIT", "Career effective"),
    )
    return _instantaneous_flags(sample) + tuple(flag for flag in cumulative if flag is not None)
