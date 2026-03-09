"""Tool schema registry."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class SchemaRegistry:
    schemas: dict[str, dict[str, object]] = field(default_factory=dict)

    def register(self, name: str, schema: dict[str, object]) -> None:
        self.schemas[name] = schema

    def get(self, name: str) -> dict[str, object] | None:
        return self.schemas.get(name)
