"""Brain: wires contract validation, scoring and the Doctor Layer end to end.

``Brain.process`` is the one call the rest of the project needs:
raw input-contract dict -> ``ContractError`` (propagated unchanged) or an
output-contract dict, ready for ``json.dumps``.

``astro_brain.scoring`` is imported lazily, inside ``process``, rather than at
module level: it is owned by a different agent and developed in parallel, so a
module-level import would make importing ``astro_brain.pipeline`` itself fail
(breaking test collection) on any day the two modules are not both present.
"""

from __future__ import annotations

import os
from typing import Any, Protocol

from .contract import parse_sample
from .doctor.layer import DoctorLayer, Recommendation
from .doctor.ollama_client import OllamaClient
from .body_map import body_systems

_ENV_OLLAMA_URL = "ASTRO_OLLAMA_URL"
_ENV_OLLAMA_MODEL = "ASTRO_OLLAMA_MODEL"
_ENV_DOCTOR_OFFLINE = "ASTRO_DOCTOR_OFFLINE"


class _FlagLike(Protocol):
    def to_dict(self) -> dict[str, Any]: ...


class _AssessmentLike(Protocol):
    timestamp: str
    astronaut_id: str
    alert_level: str
    news2_total: int
    flags: tuple[_FlagLike, ...]
    likely_conditions: tuple[Any, ...]

    def flag_codes(self) -> tuple[str, ...]: ...


def to_output(assessment: _AssessmentLike, recommendation: Recommendation) -> dict[str, Any]:
    """Build the exact camelCase output-contract dict described in AGENTS.md section 3."""
    flag_details = [flag.to_dict() for flag in assessment.flags]
    conditions = [condition.to_dict() for condition in assessment.likely_conditions]
    return {
        "timestamp": assessment.timestamp,
        "astronautId": assessment.astronaut_id,
        "alertLevel": assessment.alert_level,
        "news2Score": assessment.news2_total,
        "activeFlags": [flag.code for flag in assessment.flags],
        "flagDetails": flag_details,
        "likelyConditions": conditions,
        "bodySystems": body_systems(flag_details, conditions),
        "doctorRecommendation": recommendation.text,
        "doctorSource": recommendation.source,
    }


def _build_default_doctor() -> DoctorLayer:
    if os.environ.get(_ENV_DOCTOR_OFFLINE) == "1":
        return DoctorLayer(OllamaClient(), enabled=False)

    client_kwargs: dict[str, str] = {}
    base_url = os.environ.get(_ENV_OLLAMA_URL)
    if base_url:
        client_kwargs["base_url"] = base_url
    model = os.environ.get(_ENV_OLLAMA_MODEL)
    if model:
        client_kwargs["model"] = model
    return DoctorLayer(OllamaClient(**client_kwargs))


class Brain:
    """Validates a raw sample, scores it, attaches a recommendation, shapes the output."""

    def __init__(self, doctor: DoctorLayer | None = None) -> None:
        self._doctor = doctor if doctor is not None else _build_default_doctor()

    def process(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Validate ``raw`` against the input contract and return the output contract dict.

        ``ContractError`` from ``parse_sample`` propagates unchanged.
        """
        from .scoring import assess  # lazy: see module docstring

        sample = parse_sample(raw)
        assessment = assess(sample)
        recommendation = self._doctor.recommend(assessment)
        output = to_output(assessment, recommendation)
        for source, target in (("mission_day", "missionDay"), ("mission_phase", "missionPhase"),
                               ("medical_kit", "medicalKit")):
            value = getattr(sample, source)
            if value is not None:
                output[target] = list(value) if source == "medical_kit" else value
        return output
