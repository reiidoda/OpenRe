"""Retry policy for tool/model operations."""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Callable, TypeVar

T = TypeVar("T")


@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 0.1

    def run(self, operation: Callable[[], T]) -> T:
        attempts = 0
        while True:
            attempts += 1
            try:
                return operation()
            except Exception:
                if attempts >= self.max_attempts:
                    raise
                time.sleep(self.backoff_seconds)
