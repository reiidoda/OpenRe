"""Best config registry."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class BestConfigRegistry:
    entries: dict[str, dict[str, object]] = field(default_factory=dict)

    def set(self, dataset_id: str, config: dict[str, object]) -> None:
        self.entries[dataset_id] = config

    def get(self, dataset_id: str) -> dict[str, object] | None:
        return self.entries.get(dataset_id)
