"""Serialization helpers."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import datetime
import json
from typing import Any


def to_jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if is_dataclass(value):
        return {k: to_jsonable(v) for k, v in asdict(value).items()}
    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [to_jsonable(item) for item in value]
    return value


def dumps(value: Any) -> str:
    return json.dumps(to_jsonable(value), ensure_ascii=True, sort_keys=True)
