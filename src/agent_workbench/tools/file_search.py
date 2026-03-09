"""File search tool."""

from __future__ import annotations

from pathlib import Path


def run(query: str, root: str = ".") -> list[str]:
    matches: list[str] = []
    for path in Path(root).rglob("*"):
        if not path.is_file():
            continue
        if path.suffix in {".png", ".jpg", ".jpeg", ".gif", ".drawio"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if query.lower() in text.lower():
            matches.append(str(path))
            if len(matches) >= 20:
                break
    return matches
