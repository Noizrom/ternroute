"""Remote baseline agent with bounded retries and exact allowlist routing."""

from __future__ import annotations

import time
from dataclasses import dataclass

from .config import Config
from .contracts import Result, Task
from .errors import RemoteError
from .fireworks_client import FireworksClient
from .model_profiles import select_model
from .prompts import SYSTEM_PROMPTS, max_tokens_for
from .task_analysis import analyze_task
from .telemetry import emit
from .validators import normalize_answer, validate_answer


@dataclass(slots=True)
class TernRouteAgent:
    config: Config
    client: FireworksClient

    async def solve(self, task: Task, *, batch_deadline: float) -> Result:
        started = time.monotonic()
        task_deadline = min(started + self.config.task_budget_seconds, batch_deadline)
        analysis = analyze_task(task.prompt)
        excluded: set[str] = set()
        last_error = "remote attempts exhausted"

        for attempt in range(1, self.config.max_remote_attempts + 1):
            remaining = task_deadline - time.monotonic()
            if remaining <= 1.0:
                last_error = "task deadline exhausted"
                break

            model = select_model(
                self.config.allowed_models,
                analysis.category,
                excluded=frozenset(excluded),
            )
            timeout = min(self.config.request_read_budget_seconds, max(1.0, remaining - 0.5))
            emit(
                "remote_attempt",
                task_id=task.task_id,
                category=analysis.category.value,
                model=model,
                attempt=attempt,
                timeout_seconds=round(timeout, 3),
            )

            try:
                completion = await self.client.complete(
                    model=model,
                    system_prompt=SYSTEM_PROMPTS[analysis.category],
                    user_prompt=task.prompt,
                    max_tokens=max_tokens_for(analysis.category, analysis.output_spec),
                    timeout_seconds=timeout,
                )
                answer = normalize_answer(completion.content, analysis.output_spec)
                errors = validate_answer(answer, analysis.category, analysis.output_spec)
                if errors:
                    last_error = "; ".join(errors)
                    excluded.add(model)
                    emit(
                        "validation_failure",
                        task_id=task.task_id,
                        attempt=attempt,
                        errors=list(errors),
                    )
                    continue

                emit(
                    "remote_success",
                    task_id=task.task_id,
                    category=analysis.category.value,
                    model=model,
                    attempt=attempt,
                    duration_ms=round((time.monotonic() - started) * 1000),
                    prompt_tokens=completion.prompt_tokens,
                    completion_tokens=completion.completion_tokens,
                    total_tokens=completion.total_tokens,
                    finish_reason=completion.finish_reason,
                )
                return Result(task_id=task.task_id, answer=answer)
            except RemoteError as exc:
                if exc.fatal:
                    raise
                last_error = str(exc)
                if exc.status_code in {403, 404}:
                    excluded.add(model)
                emit(
                    "remote_failure",
                    task_id=task.task_id,
                    model=model,
                    attempt=attempt,
                    status_code=exc.status_code,
                    retryable=exc.retryable,
                )
                if not exc.retryable and exc.status_code not in {403, 404}:
                    break

        emit(
            "task_fallback",
            task_id=task.task_id,
            category=analysis.category.value,
            reason=last_error,
            duration_ms=round((time.monotonic() - started) * 1000),
        )
        return Result(task_id=task.task_id, answer="Unable to complete the task.")
