"""IMM-derived phase priors for the IMM-lite condition ranking.

Data source: ``docs/PHASE_PRIORS_AND_RESOURCES_RESEARCH_2026-11-14.md``
(sections 3 and 7), itself grounded in IMM 2015 (NTRS 20150018879), the CliFF
documents, and NASA-STD-3001 Vol.1 Rev C Table E.2-1. This module does not add
any number not present in that report; it only derives the phase-split
multiplier rule documented below.

Mechanism per condition (IMM):

- ``"SA"`` (space adaptation): onset occurs once, within the first few days of
  a mission, and either resolves or persists afterward without new onsets.
- ``"general"``: a constant-rate (Poisson) process across the whole mission.
- ``"spe_conditional"``: conditional on a solar particle event (SPE); not tied
  to mission phase at all, since an SPE can happen in either phase.
- ``"none"``: no IMM/EMCL incidence data was found (``NOT_FOUND``).

Multiplier rule (DESIGN DECISION, not in the report; derived from it):

1. SA-mechanism conditions get a phase-1 onset boost and a phase-2 dampening,
   because new onset is rare once the acute-adaptation window has passed
   (``SA_PHASE1_MULTIPLIER`` / ``SA_PHASE2_MULTIPLIER``).
2. General-rate conditions are phase-independent (the same multiplier applies
   in both phases, since the rate is constant per unit time), and that shared
   multiplier is picked from a base-rate tier of the condition's
   per-person-year rate: ``>= HIGH_RATE_THRESHOLD_PER_YEAR`` keeps the rate
   as-is (``HIGH_RATE_TIER_MULTIPLIER``); the ``MID``/``LOW`` tiers apply a
   mild discount for progressively rarer conditions. A proportion-measured
   condition (not a rate) is treated as the high tier.
3. ``spe_conditional`` conditions (acute radiation syndrome) get no phase
   effect at all: the multiplier is always ``SPE_CONDITIONAL_MULTIPLIER``.
4. An unknown code, a ``NOT_FOUND`` record, or no ``mission_phase`` all fall
   back to ``DEFAULT_MULTIPLIER`` (no adjustment).
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

PHASE_1_ACUTE_ADAPTATION = "PHASE_1_ACUTE_ADAPTATION"
PHASE_2_LONG_DURATION = "PHASE_2_LONG_DURATION"

MECHANISM_SA = "SA"
MECHANISM_GENERAL = "general"
MECHANISM_SPE_CONDITIONAL = "spe_conditional"
MECHANISM_NONE = "none"

STATUS_VERIFIED = "VERIFIED"
STATUS_DERIVED = "DERIVED"
STATUS_VERIFIED_CONDITIONAL = "VERIFIED_CONDITIONAL"
STATUS_NOT_FOUND = "NOT_FOUND"

# Multiplier rule constants (DESIGN DECISION; see module docstring).
SA_PHASE1_MULTIPLIER = 1.25
SA_PHASE2_MULTIPLIER = 0.85
HIGH_RATE_TIER_MULTIPLIER = 1.0
MID_RATE_TIER_MULTIPLIER = 0.9
LOW_RATE_TIER_MULTIPLIER = 0.8
HIGH_RATE_THRESHOLD_PER_YEAR = 0.5
LOW_RATE_THRESHOLD_PER_YEAR = 0.01
SPE_CONDITIONAL_MULTIPLIER = 1.0
DEFAULT_MULTIPLIER = 1.0


@dataclass(frozen=True)
class PhasePrior:
    """One IMM condition's phase-relevant incidence data.

    ``phase_1``/``phase_2`` are in the unit named by ``measure``: events/person
    for ``"rate"``, events/person-at-risk for ``"proportion"``, or probability
    per SPE exposure for ``"conditional_proportion"``. ``rate_per_year`` is the
    original per-person-year rate for ``"rate"`` measures (used for tiering);
    it is ``None`` for every other measure.
    """

    code: str
    emcl_name: str
    mechanism: str
    measure: str
    phase_1: float | None
    phase_2: float | None
    rate_per_year: float | None
    basis: str
    status: str
    note: str | None = None


IMM_PRIORS: MappingProxyType[str, PhasePrior] = MappingProxyType({
    "HYPOVOLEMIC_SHOCK": PhasePrior(
        code="HYPOVOLEMIC_SHOCK",
        emcl_name="ICL116 Traumatic Hypovolemic Shock",
        mechanism=MECHANISM_GENERAL,
        measure="rate",
        phase_1=8.78e-6,
        phase_2=3.073e-4,
        rate_per_year=0.000641,
        basis="0.000641 events/person-year; general Poisson split 5/365 and 175/365 of a 180-day mission",
        status=STATUS_DERIVED,
    ),
    "SEPSIS": PhasePrior(
        code="SEPSIS",
        emcl_name="ICL84 Sepsis",
        mechanism=MECHANISM_GENERAL,
        measure="rate",
        phase_1=3.288e-5,
        phase_2=1.151e-3,
        rate_per_year=0.0024,
        basis="0.0024 events/person-year; general split",
        status=STATUS_DERIVED,
    ),
    "ACUTE_RADIATION_SYNDROME": PhasePrior(
        code="ACUTE_RADIATION_SYNDROME",
        emcl_name="ICL4 Acute Radiation Syndrome",
        mechanism=MECHANISM_SPE_CONDITIONAL,
        measure="conditional_proportion",
        phase_1=0.05,
        phase_2=0.05,
        rate_per_year=None,
        basis="0.05 conditional on SPE exposure; phase depends on SPE timing, not mission phase",
        status=STATUS_VERIFIED_CONDITIONAL,
    ),
    "CARDIAC_ARRHYTHMIA": PhasePrior(
        code="CARDIAC_ARRHYTHMIA",
        emcl_name="ICL10 Atrial Fibrillation/Atrial Flutter",
        mechanism=MECHANISM_GENERAL,
        measure="rate",
        phase_1=6.478e-6,
        phase_2=2.267e-4,
        rate_per_year=0.0004729,
        basis="total mean 0.0004729 events/person-year (male 0.0007107, female 0.0002343); general split",
        status=STATUS_DERIVED,
    ),
    "SLEEP_DISORDER": PhasePrior(
        code="SLEEP_DISORDER",
        emcl_name="ICL95 Space Adaptation - Insomnia",
        mechanism=MECHANISM_SA,
        measure="proportion",
        phase_1=0.4721,
        phase_2=0.0,
        rate_per_year=None,
        basis="381/807 = 0.4721189 SAS insomnia proportion; onset 24-120h, peak at 24h",
        status=STATUS_VERIFIED,
        note=(
            "Late insomnia (NASA-STD-3001 Table E.2-1, 13.85 per mission) is a "
            "separate DERIVED sample-output figure, phase 2 only; it is not "
            "merged into this SA proportion."
        ),
    ),
    "SANS": PhasePrior(
        code="SANS",
        emcl_name="ICL100 Spaceflight Associated Neuro-Ocular Syndrome",
        mechanism=MECHANISM_SA,
        measure="proportion",
        phase_1=0.2789,
        phase_2=0.0,
        rate_per_year=None,
        basis=(
            "model mean Beta 0.2789 (observed IP 0.2593 = 7/27 person-missions); "
            "onset in first 5-7 days, persists through the mission"
        ),
        status=STATUS_VERIFIED,
        note="phase_2 = 0 means no new onset in phase 2, not zero ongoing cases.",
    ),
    "HYPERCAPNIA": PhasePrior(
        code="HYPERCAPNIA",
        emcl_name="Headache - CO2 (ICL64)",
        mechanism=MECHANISM_GENERAL,
        measure="rate",
        phase_1=0.02078,
        phase_2=0.7272,
        rate_per_year=1.5168169,
        basis="69/45.49 = 1.5168169 events/person-year (CO2-induced headache); general split",
        status=STATUS_DERIVED,
        note=(
            "This code is currently named HYPERCAPNIA but maps to EMCL "
            "'Headache - CO2' (ICL64), not a distinct hypercapnia condition; "
            "a code rename is planned."
        ),
    ),
    "RESPIRATORY_INFECTION_LOWER": PhasePrior(
        code="RESPIRATORY_INFECTION_LOWER",
        emcl_name="ICL81/82 Respiratory Tract Infection",
        mechanism=MECHANISM_GENERAL,
        measure="rate",
        phase_1=0.01054,
        phase_2=0.3689,
        rate_per_year=0.7693999,
        basis="35/45.49 = 0.7693999 events/person-year; general split",
        status=STATUS_DERIVED,
    ),
    "DEPRESSION": PhasePrior(
        code="DEPRESSION",
        emcl_name="ICL15 BHP - Depression",
        mechanism=MECHANISM_GENERAL,
        measure="rate",
        phase_1=4.452e-5,
        phase_2=1.558e-3,
        rate_per_year=0.00325,
        basis=(
            "mean of male 0.0029 and female 0.0036 events/person-year = "
            "0.00325 events/person-year; general split"
        ),
        status=STATUS_DERIVED,
        note="Report gives sex-specific rates; this record uses their mean.",
    ),
    "ALTITUDE_SICKNESS": PhasePrior(
        code="ALTITUDE_SICKNESS",
        emcl_name="",
        mechanism=MECHANISM_NONE,
        measure="none",
        phase_1=None,
        phase_2=None,
        rate_per_year=None,
        basis="No CliFF/incidence data for Altitude Sickness as an IMM condition",
        status=STATUS_NOT_FOUND,
    ),
    "NUTRITIONAL_DEFICIT": PhasePrior(
        code="NUTRITIONAL_DEFICIT",
        emcl_name="",
        mechanism=MECHANISM_NONE,
        measure="none",
        phase_1=None,
        phase_2=None,
        rate_per_year=None,
        basis="No CliFF/incidence data; not a modeled IMM/EMCL condition",
        status=STATUS_NOT_FOUND,
    ),
})


def prior_record(code: str) -> PhasePrior | None:
    """Return the IMM phase prior for ``code``, or ``None`` if unknown."""
    return IMM_PRIORS.get(code)


def _rate_tier_multiplier(rate_per_year: float | None) -> float:
    """Base-rate tier multiplier for a general-mechanism condition.

    A non-rate measure (e.g. a proportion) counts as the high tier.
    """
    if rate_per_year is None:
        return HIGH_RATE_TIER_MULTIPLIER
    if rate_per_year >= HIGH_RATE_THRESHOLD_PER_YEAR:
        return HIGH_RATE_TIER_MULTIPLIER
    if rate_per_year >= LOW_RATE_THRESHOLD_PER_YEAR:
        return MID_RATE_TIER_MULTIPLIER
    return LOW_RATE_TIER_MULTIPLIER


def phase_multiplier(condition: str, mission_phase: str | None) -> float:
    """Return the documented DERIVED multiplier for ``condition`` in ``mission_phase``.

    See the module docstring for the full rule. Falls back to
    ``DEFAULT_MULTIPLIER`` for an unknown code, a ``NOT_FOUND`` record, an
    unrecognised phase string, or ``mission_phase is None``.
    """
    if mission_phase is None:
        return DEFAULT_MULTIPLIER
    record = prior_record(condition)
    if record is None or record.status == STATUS_NOT_FOUND:
        return DEFAULT_MULTIPLIER
    if record.mechanism == MECHANISM_SA:
        if mission_phase == PHASE_1_ACUTE_ADAPTATION:
            return SA_PHASE1_MULTIPLIER
        if mission_phase == PHASE_2_LONG_DURATION:
            return SA_PHASE2_MULTIPLIER
        return DEFAULT_MULTIPLIER
    if record.mechanism == MECHANISM_SPE_CONDITIONAL:
        return SPE_CONDITIONAL_MULTIPLIER
    if record.mechanism == MECHANISM_GENERAL:
        return _rate_tier_multiplier(record.rate_per_year)
    return DEFAULT_MULTIPLIER
