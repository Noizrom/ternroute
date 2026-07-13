import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from api import route
from app.contracts import Result


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
        self.assertNotIn("api_key", payload)


if __name__ == "__main__":
    unittest.main()
