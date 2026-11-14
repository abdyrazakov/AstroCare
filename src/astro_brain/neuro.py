"""Neuro-ocular and vigilance scoring rules."""

from __future__ import annotations

from astro_brain.contract import VitalsSample
from astro_brain.evidence import EVIDENCE_BY_CODE
from astro_brain.flags import Flag

PVT_SLOW_THRESHOLD_MS = 500.0  # Basner & Dinges PVT-B lapse convention; VERIFY.
IOP_HIGH_THRESHOLD_MMHG = 21.0  # OCHMO/HRP SANS context; VERIFY.


def neuro_flags(sample: VitalsSample) -> tuple[Flag, ...]:
    flags: list[Flag] = []
    if sample.pvt_slowest10_rt_ms is not None and sample.pvt_slowest10_rt_ms > PVT_SLOW_THRESHOLD_MS:
        flags.append(Flag(
            code="PVT_SLOW", severity="yellow",
            message=f"PVT slowest-10% reaction time {sample.pvt_slowest10_rt_ms:g} ms exceeds 500 ms.",
            value=sample.pvt_slowest10_rt_ms, threshold=PVT_SLOW_THRESHOLD_MS,
            evidence=EVIDENCE_BY_CODE["PVT_SLOW"],
        ))
    if sample.iop_mmhg is not None and sample.iop_mmhg > IOP_HIGH_THRESHOLD_MMHG:
        flags.append(Flag(
            code="IOP_HIGH", severity="yellow",
            message=f"Intraocular pressure {sample.iop_mmhg:g} mmHg exceeds 21 mmHg.",
            value=sample.iop_mmhg, threshold=IOP_HIGH_THRESHOLD_MMHG,
            evidence=EVIDENCE_BY_CODE["IOP_HIGH"],
        ))
    return tuple(flags)
