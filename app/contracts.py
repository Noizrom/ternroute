"""Strict file contracts for the judging harness."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import ContractError


@dataclass(frozen=True, slots=True)
class Task:
    task_id: str
    prompt: str


@dataclass(frozen=True, slots=True)
class Result:
    task_id: str
    answer: str


def load_tasks(path: Path) -> list[Task]:
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"Input file not found: {path}") from exc
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"Unable to read valid input JSON: {exc}") from exc

    if not isinstance(raw, list):
        raise ContractError("Input JSON must be an array")

    tasks: list[Task] = []
    seen: set[str] = set()
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise ContractError(f"Task at index {index} must be an object")
        task_id = item.get("task_id")
        prompt = item.get("prompt")
        if not isinstance(task_id, str) or not task_id:
            raise ContractError(f"Task at index {index} has an invalid task_id")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ContractError(f"Task {task_id!r} has an invalid prompt")
        if task_id in seen:
            raise ContractError(f"Duplicate task_id: {task_id}")
        seen.add(task_id)
        tasks.append(Task(task_id=task_id, prompt=prompt))
    return tasks


def validate_results(tasks: list[Task], results: list[Result]) -> None:
    if len(tasks) != len(results):
        raise ContractError("Result count does not match task count")
    for index, (task, result) in enumerate(zip(tasks, results, strict=True)):
        if task.task_id != result.task_id:
            raise ContractError(f"Result order/ID mismatch at index {index}")
        if not isinstance(result.answer, str) or not result.answer.strip():
            raise ContractError(f"Task {task.task_id!r} has an empty answer")


def write_results_atomic(path: Path, tasks: list[Task], results: list[Result]) -> None:
    validate_results(tasks, results)
    payload = [
        {"task_id": result.task_id, "answer": result.answer}
        for result in results
    ]
    serialized = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f"{path.name}.tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
        reparsed = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"Unable to finalize output JSON: {exc}") from exc

    if reparsed != payload:
        raise ContractError("Output JSON changed during finalization")
