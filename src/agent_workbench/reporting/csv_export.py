"""CSV benchmark export."""

from __future__ import annotations

import csv
from pathlib import Path


def export(rows: list[dict[str, object]], target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        target.write_text("", encoding="utf-8")
        return str(target.resolve())

    fields = sorted({key for row in rows for key in row.keys()})
    with target.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return str(target.resolve())
