from __future__ import annotations

import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from app.errors import RemoteError
from app.fireworks_client import FireworksClient


class _Handler(BaseHTTPRequestHandler):
    status = 200
    response_payload: object = {
        "choices": [
            {
                "message": {"content": "answer"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
    }
    request_payload: dict[str, object] | None = None
    authorization: str | None = None

    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"])
        type(self).request_payload = json.loads(self.rfile.read(length))
        type(self).authorization = self.headers.get("Authorization")
        body = json.dumps(type(self).response_payload).encode("utf-8")
        self.send_response(type(self).status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        pass


class ClientTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        _Handler.status = 200
        _Handler.response_payload = {
            "choices": [{"message": {"content": "answer"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 2, "total_tokens": 12},
        }
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.client = FireworksClient(f"http://{host}:{port}/chat/completions", "secret")

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    async def test_successful_completion(self) -> None:
        completion = await self.client.complete(
            model="exact-allowed-model",
            system_prompt="short",
            user_prompt="question",
            max_tokens=64,
            timeout_seconds=2,
        )
        self.assertEqual(completion.content, "answer")
        self.assertEqual(completion.total_tokens, 12)
        self.assertEqual(_Handler.authorization, "Bearer secret")
        self.assertEqual(_Handler.request_payload["model"], "exact-allowed-model")
        self.assertEqual(_Handler.request_payload["temperature"], 0)
        self.assertEqual(_Handler.request_payload["max_tokens"], 64)

    async def test_retryable_server_error(self) -> None:
        _Handler.status = 503
        _Handler.response_payload = {"error": "busy"}
        with self.assertRaises(RemoteError) as context:
            await self.client.complete(
                model="model",
                system_prompt="short",
                user_prompt="question",
                max_tokens=64,
                timeout_seconds=2,
            )
        self.assertTrue(context.exception.retryable)
        self.assertEqual(context.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
