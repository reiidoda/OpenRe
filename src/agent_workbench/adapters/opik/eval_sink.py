"""Opik eval sink placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OpikEvalSink:
    enabled: bool = False

    def push(self, payload: dict[str, object]) -> None:
        _ = (self.enabled, payload)
