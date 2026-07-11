"""TernRoute batch entrypoint."""

from __future__ import annotations

import asyncio
import time

from .agent import TernRouteAgent
from .config import Config
from .contracts import Result, Task, load_tasks, write_results_atomic
from .errors import RemoteError, TernRouteError
from .fireworks_client import FireworksClient
from .telemetry import emit


async def run(config: Config, tasks: list[Task]) -> list[Result]:
    if not tasks:
        return []

    started = time.monotonic()
    batch_deadline = started + config.batch_budget_seconds
    semaphore = asyncio.Semaphore(config.max_remote_concurrency)
    agent = TernRouteAgent(
        config=config,
        client=FireworksClient(config.endpoint, config.api_key),
    )

    async def solve_one(index: int, task: Task) -> tuple[int, Result]:
        async with semaphore:
            result = await agent.solve(task, batch_deadline=batch_deadline)
            return index, result

    coroutines = [solve_one(index, task) for index, task in enumerate(tasks)]
    remaining = max(1.0, batch_deadline - time.monotonic())
    completed = await asyncio.wait_for(asyncio.gather(*coroutines), timeout=remaining)
    completed.sort(key=lambda item: item[0])
    emit(
        "batch_complete",
        tasks=len(tasks),
        duration_ms=round((time.monotonic() - started) * 1000),
    )
    return [result for _, result in completed]


def main() -> int:
    try:
        config = Config.from_env()
        tasks = load_tasks(config.input_path)
        results = asyncio.run(run(config, tasks))
        write_results_atomic(config.output_path, tasks, results)
        return 0
    except RemoteError as exc:
        emit("fatal_remote_error", status_code=exc.status_code, message=str(exc))
        return 1
    except asyncio.TimeoutError:
        emit("fatal_batch_timeout")
        return 1
    except TernRouteError as exc:
        emit("fatal_error", error_type=type(exc).__name__, message=str(exc))
        return 1
    except Exception as exc:  # defensive process boundary
        emit("unexpected_fatal_error", error_type=type(exc).__name__, message=str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
