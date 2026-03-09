"""Simple in-process scheduler."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True)
class Scheduler:
    def run_all(self, jobs: list[Callable[[], None]]) -> None:
        for job in jobs:
            job()
