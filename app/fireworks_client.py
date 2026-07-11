"""Dependency-free, bounded Fireworks Chat Completions client."""

from __future__ import annotations

import asyncio
import json
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .errors import RemoteError


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


@dataclass(frozen=True, slots=True)
class Completion:
    content: str
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    finish_reason: str | None


class FireworksClient:
    def __init__(self, endpoint: str, api_key: str) -> None:
        self._endpoint = endpoint
        self._api_key = api_key
        self._opener = urllib.request.build_opener(_NoRedirect())

    async def complete(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        timeout_seconds: float,
    ) -> Completion:
        return await asyncio.to_thread(
            self._complete_sync,
            model=model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
        )

    def _complete_sync(
        self,
        *,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        timeout_seconds: float,
    ) -> Completion:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0,
            "max_tokens": max_tokens,
        }
        request = urllib.request.Request(
            self._endpoint,
            data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "ternroute/0.1.0",
            },
            method="POST",
        )

        try:
            with self._opener.open(request, timeout=timeout_seconds) as response:
                raw = response.read()
        except urllib.error.HTTPError as exc:
            body = exc.read(4096).decode("utf-8", errors="replace")
            status = exc.code
            raise RemoteError(
                f"Fireworks HTTP {status}: {body}",
                status_code=status,
                retryable=status in {408, 429} or 500 <= status <= 599,
                fatal=status == 401,
            ) from exc
        except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
            raise RemoteError(f"Fireworks network failure: {exc}", retryable=True) from exc

        try:
            decoded = json.loads(raw)
            choice = decoded["choices"][0]
            content = _extract_content(choice["message"]["content"])
            usage = decoded.get("usage") or {}
        except (UnicodeError, json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
            raise RemoteError("Malformed Fireworks response", retryable=True) from exc

        if not content.strip():
            raise RemoteError("Empty Fireworks response", retryable=True)

        return Completion(
            content=content,
            prompt_tokens=_optional_int(usage.get("prompt_tokens")),
            completion_tokens=_optional_int(usage.get("completion_tokens")),
            total_tokens=_optional_int(usage.get("total_tokens")),
            finish_reason=choice.get("finish_reason"),
        )


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _extract_content(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        if parts:
            return "".join(parts)
    raise TypeError("Unsupported assistant content")
