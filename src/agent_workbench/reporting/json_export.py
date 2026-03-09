"""JSON benchmark export."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
from typing import Any


def _is_dataclass_instance(value: Any) -> bool:
    return is_dataclass(value) and not isinstance(value, type)


def _convert(value: Any) -> Any:
    if _is_dataclass_instance(value):
        return asdict(value)
    return value


def export(payload: Any, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, default=_convert, indent=2), encoding="utf-8")
    return str(target.resolve())
