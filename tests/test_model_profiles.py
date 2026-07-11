from __future__ import annotations

import unittest

from app.model_profiles import select_model
from app.task_analysis import Category


class ModelProfileTests(unittest.TestCase):
    def test_code_prefers_allowlisted_kimi_code(self) -> None:
        allowed = ("gemma-compact", "kimi-next-code", "minimax-general")
        selected = select_model(allowed, Category.CODE_GENERATION)
        self.assertEqual(selected, "kimi-next-code")
        self.assertIn(selected, allowed)

    def test_extraction_prefers_allowlisted_gemma(self) -> None:
        allowed = ("minimax-general", "gemma-compact", "kimi-next-code")
        selected = select_model(allowed, Category.NER)
        self.assertEqual(selected, "gemma-compact")
        self.assertIn(selected, allowed)

    def test_unknown_names_fall_back_to_first_exact_value(self) -> None:
        allowed = ("opaque-model-z", "opaque-model-a")
        self.assertEqual(select_model(allowed, Category.FACTUAL), "opaque-model-z")

    def test_excluded_model_is_skipped_when_alternative_exists(self) -> None:
        allowed = ("minimax-a", "gemma-b")
        selected = select_model(
            allowed,
            Category.FACTUAL,
            excluded=frozenset({"minimax-a"}),
        )
        self.assertEqual(selected, "gemma-b")


if __name__ == "__main__":
    unittest.main()
