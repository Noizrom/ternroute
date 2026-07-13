import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from api import route
from app.config import Config
from app.contracts import Result
from app.errors import RemoteError
from app.fireworks_client import Completion, FireworksClient


class DemoApiTests(unittest.TestCase):
    def setUp(self) -> None:
        route._request_times.clear()

    def test_prompt_validation(self) -> None:
        self.assertEqual(route.parse_prompt(b'{"prompt":"  hello  "}'), "hello")
        for body in (b"not-json", b"[]", b'{"prompt":"   "}'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                route.parse_prompt(body)

    def test_rate_limit_resets_after_window(self) -> None:
        for offset in range(route.RATE_LIMIT_REQUESTS):
            self.assertTrue(route.allow_request("client", float(offset)))
        self.assertFalse(route.allow_request("client", 10.0))
        self.assertTrue(route.allow_request("client", route.RATE_LIMIT_WINDOW_SECONDS + 1.0))

    def test_solve_prompt_exposes_route_without_leaking_config(self) -> None:
        config = SimpleNamespace(
            allowed_models=("accounts/demo/models/mini",),
            endpoint="https://example.invalid/chat/completions",
            api_key="secret",
            task_budget_seconds=1.0,
        )
        with (
            patch.object(route.Config, "from_env", return_value=config),
            patch.object(
                route.TernRouteAgent,
                "solve",
                new=AsyncMock(return_value=Result(task_id="demo", answer="Paris")),
            ),
        ):
            payload = asyncio.run(route.solve_prompt("What is the capital of France?"))

        self.assertEqual(payload["answer"], "Paris")
        self.assertEqual(payload["category"], "factual")
        self.assertEqual(payload["initial_model"], config.allowed_models[0])
        self.assertEqual(payload["model_status"], "ok")
        self.assertNotIn("api_key", payload)

    def test_solve_prompt_reports_unavailable_model(self) -> None:
        model = "accounts/demo/models/missing"
        config = Config(
            api_key="secret",
            endpoint="https://example.invalid/chat/completions",
            allowed_models=(model,),
            max_remote_attempts=1,
            task_budget_seconds=2,
            request_read_budget_seconds=1,
        )
        with (
            patch.object(route.Config, "from_env", return_value=config),
            patch.object(
                FireworksClient,
                "complete",
                new=AsyncMock(side_effect=RemoteError("missing", status_code=404)),
            ),
        ):
            payload = asyncio.run(route.solve_prompt("What is the capital of France?"))

        self.assertEqual(payload["model_status"], "unavailable")
        self.assertEqual(payload["unavailable_models"], [model])
        self.assertEqual(payload["answer"], "Unable to complete the task.")

    def test_solve_prompt_reports_successful_reroute(self) -> None:
        models = ("minimax-general", "gemma-compact")
        config = Config(
            api_key="secret",
            endpoint="https://example.invalid/chat/completions",
            allowed_models=models,
            max_remote_attempts=2,
            task_budget_seconds=2,
            request_read_budget_seconds=1,
        )
        responses = [
            RemoteError("missing", status_code=404),
            Completion("Paris", 5, 1, 6, "stop"),
        ]
        with (
            patch.object(route.Config, "from_env", return_value=config),
            patch.object(FireworksClient, "complete", new=AsyncMock(side_effect=responses)),
        ):
            payload = asyncio.run(route.solve_prompt("What is the capital of France?"))

        self.assertEqual(payload["model_status"], "rerouted")
        self.assertEqual(payload["unavailable_models"], [models[0]])
        self.assertEqual(payload["selected_model"], models[1])
        self.assertEqual(payload["answer"], "Paris")


if __name__ == "__main__":
    unittest.main()
