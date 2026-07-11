"""Dynamic model-family routing constrained by the runtime allowlist."""

from __future__ import annotations

import re

from .errors import ConfigurationError
from .task_analysis import Category


_PREFERENCES: dict[Category, tuple[str, ...]] = {
    Category.CODE_DEBUGGING: (r"kimi.*code", r"coder", r"code", r"minimax", r"gemma"),
    Category.CODE_GENERATION: (r"kimi.*code", r"coder", r"code", r"minimax", r"gemma"),
    Category.MATH: (r"minimax", r"kimi", r"gemma"),
    Category.LOGIC: (r"minimax", r"kimi", r"gemma"),
    Category.SENTIMENT: (r"gemma", r"minimax", r"kimi"),
    Category.NER: (r"gemma", r"minimax", r"kimi"),
    Category.SUMMARIZATION: (r"gemma", r"minimax", r"kimi"),
    Category.FACTUAL: (r"minimax", r"gemma", r"kimi"),
    Category.UNKNOWN: (r"minimax", r"kimi", r"gemma"),
}


def select_model(
    allowed_models: tuple[str, ...],
    category: Category,
    *,
    excluded: frozenset[str] = frozenset(),
) -> str:
    candidates = [model for model in allowed_models if model not in excluded]
    if not candidates:
        candidates = list(allowed_models)
    if not candidates:
        raise ConfigurationError("ALLOWED_MODELS is empty")

    for pattern in _PREFERENCES[category]:
        for model in candidates:
            if re.search(pattern, model, re.IGNORECASE):
                return model
    return candidates[0]
