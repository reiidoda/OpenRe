"""Identifier helpers."""

from __future__ import annotations

from datetime import datetime, UTC
from secrets import token_hex


def make_id(prefix: str) -> str:
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    return f"{prefix}_{stamp}_{token_hex(3)}"
