"""Runtime configuration loaded exclusively from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from .errors import ConfigurationError


def parse_allowed_models(raw: str) -> tuple[str, ...]:
    """Parse a comma-separated allowlist, deduplicating without reordering."""

    return tuple(dict.fromkeys(part.strip() for part in raw.split(",") if part.strip()))


def _positive_number(name: str, default: str, cast: type[int] | type[float]) -> int | float:
    raw = os.getenv(name, default)
    try:
        value = cast(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a valid {cast.__name__}") from exc
    if value <= 0:
        raise ConfigurationError(f"{name} must be greater than zero")
    return value


def _endpoint_from_base_url(base_url: str) -> str:
    normalized = base_url.strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ConfigurationError("FIREWORKS_BASE_URL must be an absolute HTTP(S) URL")
    if normalized.endswith("/chat/completions"):
        return normalized
    return f"{normalized}/chat/completions"


@dataclass(frozen=True, slots=True)
class Config:
    api_key: str
    endpoint: str
    allowed_models: tuple[str, ...]
    input_path: Path = Path("/input/tasks.json")
    output_path: Path = Path("/output/results.json")
    max_remote_concurrency: int = 2
    max_remote_attempts: int = 2
    task_budget_seconds: float = 28.0
    batch_budget_seconds: float = 540.0
    request_read_budget_seconds: float = 18.0
    connect_timeout_seconds: float = 4.0

    @classmethod
    def from_env(cls) -> "Config":
        api_key = os.getenv("FIREWORKS_API_KEY", "").strip()
        base_url = os.getenv("FIREWORKS_BASE_URL", "").strip()
        allowed_models = parse_allowed_models(os.getenv("ALLOWED_MODELS", ""))

        missing = [
            name
            for name, value in (
                ("FIREWORKS_API_KEY", api_key),
                ("FIREWORKS_BASE_URL", base_url),
                ("ALLOWED_MODELS", allowed_models),
            )
            if not value
        ]
        if missing:
            raise ConfigurationError(f"Missing required environment: {', '.join(missing)}")

        return cls(
            api_key=api_key,
            endpoint=_endpoint_from_base_url(base_url),
            allowed_models=allowed_models,
            input_path=Path(os.getenv("TERNROUTE_INPUT_PATH", "/input/tasks.json")),
            output_path=Path(os.getenv("TERNROUTE_OUTPUT_PATH", "/output/results.json")),
            max_remote_concurrency=int(
                _positive_number("TERNROUTE_MAX_CONCURRENCY", "2", int)
            ),
            max_remote_attempts=int(
                _positive_number("TERNROUTE_MAX_ATTEMPTS", "2", int)
            ),
            task_budget_seconds=float(
                _positive_number("TERNROUTE_TASK_BUDGET", "28", float)
            ),
            batch_budget_seconds=float(
                _positive_number("TERNROUTE_BATCH_BUDGET", "540", float)
            ),
            request_read_budget_seconds=float(
                _positive_number("TERNROUTE_READ_BUDGET", "18", float)
            ),
            connect_timeout_seconds=float(
                _positive_number("TERNROUTE_CONNECT_TIMEOUT", "4", float)
            ),
        )
