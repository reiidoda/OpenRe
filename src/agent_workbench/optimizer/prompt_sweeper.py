"""Prompt sweeper."""

from __future__ import annotations


def generate_variants(base_prompt: str) -> list[str]:
    return [
        base_prompt,
        f"{base_prompt}\nBe concise and cite sources.",
        f"{base_prompt}\nUse tools only when necessary.",
    ]
