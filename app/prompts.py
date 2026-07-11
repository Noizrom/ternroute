"""Short prompt profiles and output-token ceilings."""

from __future__ import annotations

from .output_spec import OutputSpec
from .task_analysis import Category


SYSTEM_PROMPTS: dict[Category, str] = {
    Category.FACTUAL: "Answer exactly as requested. Be concise and accurate.",
    Category.MATH: "Solve accurately. Return only the requested answer and necessary reasoning.",
    Category.SENTIMENT: "Use only the requested label and format.",
    Category.SUMMARIZATION: "Preserve meaning and obey every stated length and format constraint.",
    Category.NER: "Extract only items explicitly present and follow the requested schema.",
    Category.CODE_DEBUGGING: "Return the corrected code or diagnosis requested. Preserve the specified API.",
    Category.LOGIC: "Reason carefully and return only the requested conclusion and necessary justification.",
    Category.CODE_GENERATION: "Return correct executable code matching the specified API and format.",
    Category.UNKNOWN: "Answer exactly as requested. Be concise and accurate.",
}


def max_tokens_for(category: Category, spec: OutputSpec) -> int:
    if spec.format == "label" and not spec.explanation_required:
        return 16
    if category is Category.SENTIMENT:
        return 48
    if category is Category.FACTUAL:
        return 96
    if category is Category.MATH:
        return 128
    if category is Category.NER:
        return 192
    if category is Category.LOGIC:
        return 192
    if category is Category.SUMMARIZATION:
        if spec.max_words is not None:
            return max(32, min(512, spec.max_words * 2 + 16))
        return 256
    if category in {Category.CODE_DEBUGGING, Category.CODE_GENERATION}:
        return 1024
    return 256
