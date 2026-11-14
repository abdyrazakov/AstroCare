"""Doctor Layer: LLM-backed recommendation text with cache/debounce and fallback.

Public surface: ``DoctorLayer`` (the cache/debounce/fallback orchestrator),
``Recommendation`` (its immutable result), ``OllamaClient``/``OllamaError`` (the
stdlib HTTP client to a local Ollama server), and ``build_fallback`` (the
deterministic rule-based text used whenever the model is unavailable).
"""

from __future__ import annotations

from .fallback import build_fallback
from .layer import DoctorLayer, Recommendation
from .ollama_client import OllamaClient, OllamaError

__all__ = [
    "DoctorLayer",
    "Recommendation",
    "OllamaClient",
    "OllamaError",
    "build_fallback",
]
