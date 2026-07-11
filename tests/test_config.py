from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from app.config import Config, parse_allowed_models
from app.errors import ConfigurationError


class ConfigTests(unittest.TestCase):
    def test_allowlist_is_trimmed_and_deduplicated(self) -> None:
        self.assertEqual(
            parse_allowed_models(" gemma, kimi,gemma,, minimax "),
            ("gemma", "kimi", "minimax"),
        )

    def test_endpoint_is_appended(self) -> None:
        environment = {
            "FIREWORKS_API_KEY": "secret",
            "FIREWORKS_BASE_URL": "https://proxy.example/v1/",
            "ALLOWED_MODELS": "model-a,model-b",
        }
        with patch.dict(os.environ, environment, clear=True):
            config = Config.from_env()
        self.assertEqual(config.endpoint, "https://proxy.example/v1/chat/completions")
        self.assertEqual(config.allowed_models, ("model-a", "model-b"))

    def test_complete_endpoint_is_not_duplicated(self) -> None:
        environment = {
            "FIREWORKS_API_KEY": "secret",
            "FIREWORKS_BASE_URL": "https://proxy.example/v1/chat/completions",
            "ALLOWED_MODELS": "model-a",
        }
        with patch.dict(os.environ, environment, clear=True):
            config = Config.from_env()
        self.assertEqual(config.endpoint, environment["FIREWORKS_BASE_URL"])

    def test_missing_environment_fails(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                Config.from_env()

    def test_invalid_base_url_fails(self) -> None:
        environment = {
            "FIREWORKS_API_KEY": "secret",
            "FIREWORKS_BASE_URL": "not-a-url",
            "ALLOWED_MODELS": "model-a",
        }
        with patch.dict(os.environ, environment, clear=True):
            with self.assertRaises(ConfigurationError):
                Config.from_env()


if __name__ == "__main__":
    unittest.main()
