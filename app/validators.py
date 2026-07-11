"""Mechanical answer normalization and validation."""

from __future__ import annotations

import re

from .output_spec import OutputSpec
from .task_analysis import Category


_FENCE = re.compile(r"^```(?:[A-Za-z0-9_+.-]+)?\s*\n(?P<body>.*)\n```$", re.DOTALL)


def normalize_answer(answer: str, spec: OutputSpec) -> str:
    normalized = answer.strip()
    if spec.code_only:
        match = _FENCE.match(normalized)
        if match:
            normalized = match.group("body").strip()
    if spec.allowed_labels:
        for label in spec.allowed_labels:
            if normalized.casefold() == label.casefold():
                return label
    return normalized


def _sentence_count(text: str) -> int:
    pieces = re.findall(r"[^.!?]+[.!?]+(?:[\"')\]]+)?|[^.!?]+$", text.strip())
    return sum(1 for piece in pieces if piece.strip())


def validate_answer(answer: str, category: Category, spec: OutputSpec) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(answer, str) or not answer.strip():
        return ("empty answer",)

    if spec.allowed_labels and not spec.explanation_required:
        if answer.strip().casefold() not in {label.casefold() for label in spec.allowed_labels}:
            errors.append("answer is not one of the requested labels")

    if spec.max_words is not None:
        word_count = len(re.findall(r"\b\S+\b", answer))
        if word_count > spec.max_words:
            errors.append(f"answer exceeds {spec.max_words} words")

    if spec.exact_sentences is not None and _sentence_count(answer) != spec.exact_sentences:
        errors.append(f"answer does not contain exactly {spec.exact_sentences} sentence(s)")

    if spec.exact_bullets is not None:
        bullets = len(re.findall(r"(?m)^\s*(?:[-*+] |\d+[.)] )", answer))
        if bullets != spec.exact_bullets:
            errors.append(f"answer does not contain exactly {spec.exact_bullets} bullets")

    if category in {Category.CODE_DEBUGGING, Category.CODE_GENERATION} and spec.code_only:
        if not answer.strip():
            errors.append("code answer is empty")

    return tuple(errors)
