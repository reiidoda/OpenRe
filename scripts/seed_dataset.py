#!/usr/bin/env python3
"""Seed baseline dataset artifacts (idempotent)."""

from __future__ import annotations

from pathlib import Path


if __name__ == "__main__":
    dataset = Path("datasets/research_assistant_v1")
    if dataset.exists():
        print(f"Dataset already present: {dataset}")
    else:
        raise SystemExit("Dataset path missing; scaffold not initialized.")
