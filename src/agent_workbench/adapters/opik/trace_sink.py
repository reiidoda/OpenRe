"""Opik trace sink placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OpikTraceSink:
    enabled: bool = False

    def write(self, event: object) -> None:
        _ = (self.enabled, event)
