"""Compact JSON telemetry written only to stderr."""

from __future__ import annotations

import json
import sys
from typing import Any


def emit(event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")), file=sys.stderr)
