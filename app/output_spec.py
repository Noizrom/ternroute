"""Conservative extraction of explicit output constraints."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class OutputSpec:
    format: Literal["text", "label", "json", "code", "bullets"] = "text"
    allowed_labels: tuple[str, ...] = ()
    exact_sentences: int | None = None
    max_words: int | None = None
    exact_bullets: int | None = None
    code_only: bool = False
    explanation_required: bool = False


_NUMBER_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def _parse_count(value: str) -> int | None:
    if value.isdigit():
        return int(value)
    return _NUMBER_WORDS.get(value.lower())


def parse_output_spec(prompt: str) -> OutputSpec:
    lower = prompt.lower()
    exact_sentences: int | None = None
    max_words: int | None = None
    exact_bullets: int | None = None

    sentence_match = re.search(
        r"\b(?:in|using|exactly)\s+(one|two|three|four|five|\d+)\s+sentences?\b",
        lower,
    )
    if sentence_match:
        exact_sentences = _parse_count(sentence_match.group(1))
    elif re.search(r"\bone[- ]sentence\b", lower):
        exact_sentences = 1

    word_match = re.search(
        r"\b(?:at most|no more than|maximum(?: of)?|max(?:imum)?)\s+(\d+)\s+words?\b",
        lower,
    )
    if word_match:
        max_words = int(word_match.group(1))

    bullet_match = re.search(
        r"\b(?:exactly|in|using)\s+(one|two|three|four|five|\d+)\s+bullet(?: points?)?\b",
        lower,
    )
    if bullet_match:
        exact_bullets = _parse_count(bullet_match.group(1))

    code_only = bool(re.search(r"\b(?:return|output|provide)\s+(?:only\s+)?(?:the\s+)?code\b", lower))
    explanation_required = bool(re.search(r"\b(?:explain|brief explanation|justify)\b", lower))

    labels: tuple[str, ...] = ()
    sentiment_labels = tuple(
        label for label in ("positive", "negative", "neutral", "mixed") if label in lower
    )
    if "sentiment" in lower and len(sentiment_labels) >= 2:
        labels = sentiment_labels

    if code_only:
        output_format: Literal["text", "label", "json", "code", "bullets"] = "code"
    elif re.search(r"\bjson\b", lower):
        output_format = "json"
    elif exact_bullets is not None or "bullet points" in lower:
        output_format = "bullets"
    elif labels:
        output_format = "label"
    else:
        output_format = "text"

    return OutputSpec(
        format=output_format,
        allowed_labels=labels,
        exact_sentences=exact_sentences,
        max_words=max_words,
        exact_bullets=exact_bullets,
        code_only=code_only,
        explanation_required=explanation_required,
    )
