"""Prompt text for the Ollama-backed doctor recommendation.

Kept separate from ``layer.py`` and ``ollama_client.py`` so the wording can be
tuned without touching request plumbing or caching logic.
"""

from __future__ import annotations

import json
from typing import Protocol

SYSTEM_PROMPT = (
    "You are a flight-surgeon assistant aboard a crewed spacecraft. You are given an "
    "astronaut's current alert level, NEWS2 score, and active clinical/operational flags. "
    "Respond with exactly 3 to 4 sentences of plain-language guidance for the crew. "
    "Even with only one flag, write at least three sentences: the first sentence "
    "gives immediate actions, the second sentence gives follow-up monitoring or "
    "reassessment actions, and an optional third action sentence covers remaining flags. "
    "Include one concrete action for every active flag; address all flags, combining "
    "related actions in a sentence when needed. The final sentence must state when "
    "to contact ground medical. Never state or imply a diagnosis. Never use markdown "
    "or a preamble; respond with advice only. Never repeat input numbers. You may also "
    "receive likelyConditions: ranked possibilities, never diagnoses; use them only to "
    "prioritize monitoring and never present them as confirmed. Recommend only resources "
    "marked onboard: true; if a needed resource is missing, say so explicitly and direct "
    "the crew to ground medical."
)


class _AssessmentLike(Protocol):
    """The subset of the scoring ``Assessment`` shape this module depends on."""

    alert_level: str
    news2_total: int
    flags: tuple[object, ...]


def build_user_prompt(assessment: _AssessmentLike) -> str:
    """Explicit flag checklist followed by a compact JSON summary of ``assessment`` for the user turn of the chat request."""
    payload = {
        "alertLevel": assessment.alert_level,
        "news2Score": assessment.news2_total,
        "flags": [flag.to_dict() for flag in assessment.flags],
        "likelyConditions": [
            condition.to_dict() for condition in getattr(assessment, "likely_conditions", ())
        ],
    }
    codes = ", ".join(flag.code for flag in assessment.flags)
    return f"Flags to address (all of them): {codes}\n" + json.dumps(
        payload, separators=(",", ":")
    )
