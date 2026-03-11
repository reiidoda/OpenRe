#!/usr/bin/env python3
"""Check relative Markdown links for existence.

This script validates repository-local markdown links in `*.md` files.
It ignores:
- external links (`http://`, `https://`, `mailto:`)
- in-page anchors (`#...`)
"""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SKIP_PREFIXES = ("http://", "https://", "mailto:", "#")


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)


def normalize_target(raw_target: str) -> str:
    target = raw_target.strip().strip("<>")
    if not target:
        return target
    return unquote(target.split("#", 1)[0])


def check_file(path: Path, repo_root: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    for match in LINK_RE.finditer(text):
        target_raw = match.group(1).strip()
        if not target_raw or target_raw.startswith(SKIP_PREFIXES):
            continue

        target = normalize_target(target_raw)
        if not target:
            continue

        candidate = (path.parent / target).resolve()
        if not candidate.exists():
            # Also try repo-root resolution for links starting from project root style.
            repo_candidate = (repo_root / target).resolve()
            if not repo_candidate.exists():
                errors.append(
                    f"{path}: broken link '{target_raw}' (checked '{candidate}' and '{repo_candidate}')"
                )

    return errors


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    failures: list[str] = []

    for md_file in iter_markdown_files(repo_root):
        failures.extend(check_file(md_file, repo_root))

    if failures:
        print("Markdown link check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Markdown link check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
