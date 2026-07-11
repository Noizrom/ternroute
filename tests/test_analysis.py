from __future__ import annotations

import unittest

from app.output_spec import parse_output_spec
from app.task_analysis import Category, analyze_task


class AnalysisTests(unittest.TestCase):
    def test_debugging_precedes_generation(self) -> None:
        analysis = analyze_task("Debug and implement a fix for this Python function")
        self.assertEqual(analysis.category, Category.CODE_DEBUGGING)

    def test_summary_constraints(self) -> None:
        analysis = analyze_task("Summarize the text in exactly one sentence and at most 25 words.")
        self.assertEqual(analysis.category, Category.SUMMARIZATION)
        self.assertEqual(analysis.output_spec.exact_sentences, 1)
        self.assertEqual(analysis.output_spec.max_words, 25)

    def test_code_only_detection(self) -> None:
        spec = parse_output_spec("Write a Python function. Return only the code.")
        self.assertTrue(spec.code_only)
        self.assertEqual(spec.format, "code")

    def test_sentiment_labels(self) -> None:
        spec = parse_output_spec("Classify the sentiment as positive, negative, neutral, or mixed.")
        self.assertEqual(spec.allowed_labels, ("positive", "negative", "neutral", "mixed"))

    def test_factual_fallback(self) -> None:
        analysis = analyze_task("What is a database index?")
        self.assertEqual(analysis.category, Category.FACTUAL)


if __name__ == "__main__":
    unittest.main()
