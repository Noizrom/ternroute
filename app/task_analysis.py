"""Zero-token task classification used only for routing and output policy."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

from .output_spec import OutputSpec, parse_output_spec


class Category(str, Enum):
    FACTUAL = "factual"
    MATH = "math"
    SENTIMENT = "sentiment"
    SUMMARIZATION = "summarization"
    NER = "ner"
    CODE_DEBUGGING = "code_debugging"
    LOGIC = "logic"
    CODE_GENERATION = "code_generation"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class TaskAnalysis:
    category: Category
    output_spec: OutputSpec
    evidence: tuple[str, ...]


def analyze_task(prompt: str) -> TaskAnalysis:
    lower = prompt.lower()
    category = Category.UNKNOWN
    evidence: list[str] = []

    rules: tuple[tuple[Category, tuple[str, ...]], ...] = (
        (
            Category.CODE_DEBUGGING,
            (r"\bdebug\b", r"\bfix (?:this|the) (?:bug|code|function)\b", r"\bidentify the bug\b"),
        ),
        (
            Category.CODE_GENERATION,
            (r"\bwrite (?:a|an|the) .*?\b(?:function|class|program|script)\b", r"\bimplement\b"),
        ),
        (
            Category.SUMMARIZATION,
            (r"\bsummari[sz]e\b", r"\bcondense\b", r"\bwrite a summary\b"),
        ),
        (
            Category.NER,
            (r"\bnamed entit", r"\bextract\b.*\b(?:person|organization|location|date|entities)\b"),
        ),
        (
            Category.SENTIMENT,
            (r"\bsentiment\b", r"\bclassify\b.*\b(?:positive|negative|neutral|mixed)\b"),
        ),
        (
            Category.MATH,
            (r"\bcalculate\b", r"\bsolve\b.*(?:\d|equation)", r"\b\d+(?:\.\d+)?\s*%\b"),
        ),
        (
            Category.LOGIC,
            (r"\bexactly one\b", r"\beach .* different\b", r"\blogic puzzle\b", r"\bconstraints?\b"),
        ),
    )

    for candidate, patterns in rules:
        matched = [pattern for pattern in patterns if re.search(pattern, lower, re.DOTALL)]
        if matched:
            category = candidate
            evidence.extend(matched)
            break

    if category is Category.UNKNOWN:
        if re.search(r"\b(?:what|who|when|where|why|how|define|explain)\b", lower):
            category = Category.FACTUAL
            evidence.append("factual-question-form")
        else:
            evidence.append("unknown-fallback")

    return TaskAnalysis(
        category=category,
        output_spec=parse_output_spec(prompt),
        evidence=tuple(evidence),
    )
