"""CSV benchmark export."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Mapping


def export(
    rows: list[dict[str, object]],
    target: Path,
    metadata: Mapping[str, object] | None = None,
) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    normalized_metadata = dict(metadata or {})
    normalized_rows = [{**normalized_metadata, **row} for row in rows]
    if not rows:
        target.write_text("", encoding="utf-8")
        return str(target.resolve())

    fields = sorted({key for row in normalized_rows for key in row.keys()})
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(normalized_rows)
    return str(target.resolve())
