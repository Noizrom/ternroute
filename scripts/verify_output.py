#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_output.py RESULTS_JSON", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"invalid JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(payload, list):
        print("output must be an array", file=sys.stderr)
        return 1
    seen: set[str] = set()
    for index, item in enumerate(payload):
        if not isinstance(item, dict) or set(item) != {"task_id", "answer"}:
            print(f"invalid result object at index {index}", file=sys.stderr)
            return 1
        if not isinstance(item["task_id"], str) or not item["task_id"]:
            print(f"invalid task_id at index {index}", file=sys.stderr)
            return 1
        if item["task_id"] in seen:
            print(f"duplicate task_id at index {index}", file=sys.stderr)
            return 1
        seen.add(item["task_id"])
        if not isinstance(item["answer"], str) or not item["answer"].strip():
            print(f"invalid answer at index {index}", file=sys.stderr)
            return 1
    print(f"valid: {len(payload)} result(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
