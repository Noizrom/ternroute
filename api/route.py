import asyncio
import json
import logging
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler

from app.agent import TernRouteAgent
from app.config import Config
from app.contracts import Task
from app.errors import RemoteError, TernRouteError
from app.fireworks_client import Completion, FireworksClient
from app.model_profiles import select_model
from app.task_analysis import analyze_task

MAX_BODY_BYTES = 20_000
MAX_PROMPT_CHARS = 4_000
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW_SECONDS = 60

_request_times: dict[str, deque[float]] = {}
_rate_lock = threading.Lock()


class AvailabilityTrackingClient(FireworksClient):
    def __init__(self, endpoint: str, api_key: str) -> None:
        super().__init__(endpoint, api_key)
        self.unavailable_models: list[str] = []
        self.successful_model: str | None = None

    async def complete(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        timeout_seconds: float,
    ) -> Completion:
        try:
            completion = await super().complete(
                model=model,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
            )
        except RemoteError as exc:
            if exc.status_code in {403, 404} and model not in self.unavailable_models:
                self.unavailable_models.append(model)
            raise
        self.successful_model = model
        return completion


def parse_prompt(raw: bytes) -> str:
    try:
        body = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Request body must be valid JSON.") from exc

    prompt = body.get("prompt") if isinstance(body, dict) else None
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be a non-empty string.")

    prompt = prompt.strip()
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError(f"Prompt must be at most {MAX_PROMPT_CHARS} characters.")
    return prompt


def allow_request(client: str, now: float | None = None) -> bool:
    now = time.monotonic() if now is None else now
    cutoff = now - RATE_LIMIT_WINDOW_SECONDS
    with _rate_lock:
        if client not in _request_times and len(_request_times) >= 2_048:
            _request_times.pop(next(iter(_request_times)))
        requests = _request_times.setdefault(client, deque())
        while requests and requests[0] <= cutoff:
            requests.popleft()
        if len(requests) >= RATE_LIMIT_REQUESTS:
            return False
        requests.append(now)
        return True


async def solve_prompt(prompt: str) -> dict[str, object]:
    config = Config.from_env()
    analysis = analyze_task(prompt)
    initial_model = select_model(config.allowed_models, analysis.category)
    client = AvailabilityTrackingClient(config.endpoint, config.api_key)
    agent = TernRouteAgent(config=config, client=client)
    result = await agent.solve(
        Task(task_id="demo", prompt=prompt),
        batch_deadline=time.monotonic() + config.task_budget_seconds,
    )
    spec = analysis.output_spec
    # ponytail: Result intentionally has no metadata; this fallback text is its stable contract.
    unavailable = bool(client.unavailable_models)
    model_status = (
        "unavailable"
        if unavailable and result.answer == "Unable to complete the task."
        else "rerouted"
        if unavailable
        else "ok"
    )
    return {
        "answer": result.answer,
        "category": analysis.category.value,
        "initial_model": initial_model,
        "selected_model": client.successful_model or initial_model,
        "model_status": model_status,
        "unavailable_models": client.unavailable_models,
        "evidence": list(analysis.evidence),
        "output_spec": {
            "format": spec.format,
            "allowed_labels": list(spec.allowed_labels),
            "exact_sentences": spec.exact_sentences,
            "max_words": spec.max_words,
            "exact_bullets": spec.exact_bullets,
            "code_only": spec.code_only,
            "explanation_required": spec.explanation_required,
        },
    }


class handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        client = self.headers.get("x-forwarded-for", self.client_address[0]).split(",", 1)[0]
        if not allow_request(client):
            self._send_json(429, {"error": "Too many requests. Try again in a minute."})
            return

        if self.headers.get_content_type() != "application/json":
            self._send_json(415, {"error": "Content-Type must be application/json."})
            return

        try:
            content_length = int(self.headers.get("content-length", "0"))
        except ValueError:
            content_length = 0
        if content_length <= 0 or content_length > MAX_BODY_BYTES:
            self._send_json(413, {"error": f"Request body must be under {MAX_BODY_BYTES} bytes."})
            return

        try:
            prompt = parse_prompt(self.rfile.read(content_length))
            response = asyncio.run(solve_prompt(prompt))
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except (TernRouteError, TimeoutError):
            logging.exception("TernRoute demo request failed")
            self._send_json(502, {"error": "The model request failed. Please try again."})
            return
        except Exception:
            logging.exception("Unexpected TernRoute demo error")
            self._send_json(500, {"error": "The demo is temporarily unavailable."})
            return

        self._send_json(200, response)

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)
