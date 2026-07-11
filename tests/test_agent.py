from __future__ import annotations

import time
import unittest

from app.agent import TernRouteAgent
from app.config import Config
from app.contracts import Task
from app.errors import RemoteError
from app.fireworks_client import Completion


class _FakeClient:
    def __init__(self, responses: list[Completion | Exception]) -> None:
        self.responses = responses
        self.models: list[str] = []

    async def complete(self, **kwargs: object) -> Completion:
        self.models.append(str(kwargs["model"]))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _completion(content: str) -> Completion:
    return Completion(content, 5, 1, 6, "stop")


class AgentTests(unittest.IsolatedAsyncioTestCase):
    def config(self) -> Config:
        return Config(
            api_key="secret",
            endpoint="https://example.test/chat/completions",
            allowed_models=("minimax-general", "gemma-compact"),
            task_budget_seconds=5,
            request_read_budget_seconds=2,
        )

    async def test_success_returns_answer(self) -> None:
        client = _FakeClient([_completion("Paris")])
        agent = TernRouteAgent(self.config(), client)  # type: ignore[arg-type]
        result = await agent.solve(
            Task("t1", "What is the capital of France?"),
            batch_deadline=time.monotonic() + 10,
        )
        self.assertEqual(result.answer, "Paris")
        self.assertEqual(client.models, ["minimax-general"])

    async def test_unavailable_model_uses_allowlisted_alternative(self) -> None:
        client = _FakeClient(
            [
                RemoteError("missing", status_code=404),
                _completion("Paris"),
            ]
        )
        agent = TernRouteAgent(self.config(), client)  # type: ignore[arg-type]
        result = await agent.solve(
            Task("t1", "What is the capital of France?"),
            batch_deadline=time.monotonic() + 10,
        )
        self.assertEqual(result.answer, "Paris")
        self.assertEqual(client.models, ["minimax-general", "gemma-compact"])


if __name__ == "__main__":
    unittest.main()
