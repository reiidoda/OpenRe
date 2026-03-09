"""HTML benchmark export."""

from __future__ import annotations

from pathlib import Path


def export(title: str, rows: list[dict[str, object]], target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    headers = sorted({key for row in rows for key in row.keys()})
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{row.get(h, '')}</td>" for h in headers) + "</tr>" for row in rows
    )
    html = f"""<!doctype html>
<html>
<head><meta charset=\"utf-8\"><title>{title}</title></head>
<body>
<h1>{title}</h1>
<table border=\"1\"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
</body>
</html>
"""
    target.write_text(html, encoding="utf-8")
    return str(target.resolve())
