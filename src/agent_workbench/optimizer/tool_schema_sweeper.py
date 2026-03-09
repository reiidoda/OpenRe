"""Tool schema sweeper."""

from __future__ import annotations


def generate_schema_variants(base: dict[str, object]) -> list[dict[str, object]]:
    variants = [dict(base)]
    variant = dict(base)
    variant["strict"] = True
    variants.append(variant)
    return variants
