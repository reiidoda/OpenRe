"""HTML benchmark export."""

from __future__ import annotations

from html import escape
from pathlib import Path


def _render_rows_table(rows: list[dict[str, object]]) -> str:
    headers = sorted({key for row in rows for key in row.keys()})
    if not headers:
        return "<p>No run rows available.</p>"

    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(str(row.get(h, '')))}</td>" for h in headers) + "</tr>"
        for row in rows
    )
    return f'<table border="1"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def _render_failure_clusters(cluster_details: list[dict[str, object]]) -> str:
    if not cluster_details:
        return "<p>No failure clusters detected.</p>"

    headers = [
        "label",
        "count",
        "representative_task_id",
        "representative_config_id",
        "representative_task_run_id",
        "representative_trace",
    ]
    head = "".join(f"<th>{escape(column)}</th>" for column in headers)
    body_rows: list[str] = []

    for cluster in cluster_details:
        label = escape(str(cluster.get("label", "")))
        count = escape(str(cluster.get("count", "")))
        representative = cluster.get("representative")
        representative_map = representative if isinstance(representative, dict) else {}
        task_id = escape(str(representative_map.get("task_id", "")))
        config_id = escape(str(representative_map.get("config_id", "")))
        task_run_id = escape(str(representative_map.get("task_run_id", "")))
        trace_path = str(representative_map.get("trace_path", ""))
        trace_href = (
            f"{escape(trace_path)}#task_run_id={task_run_id}" if trace_path and task_run_id else ""
        )
        if trace_href:
            trace_cell = f'<a href="{trace_href}">{escape(trace_path)}</a>'
        else:
            trace_cell = escape(trace_path)

        body_rows.append(
            "<tr>"
            f"<td>{label}</td>"
            f"<td>{count}</td>"
            f"<td>{task_id}</td>"
            f"<td>{config_id}</td>"
            f"<td>{task_run_id}</td>"
            f"<td>{trace_cell}</td>"
            "</tr>"
        )

    body = "".join(body_rows)
    return f'<table border="1"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def export(
    title: str,
    rows: list[dict[str, object]],
    target: Path,
    *,
    cluster_details: list[dict[str, object]] | None = None,
) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    rows_table = _render_rows_table(rows)
    clusters_section = _render_failure_clusters(cluster_details or [])
    html = f"""<!doctype html>
<html>
<head><meta charset=\"utf-8\"><title>{escape(title)}</title></head>
<body>
<h1>{escape(title)}</h1>
<h2>Result Table</h2>
{rows_table}
<h2>Failure Clusters</h2>
{clusters_section}
</body>
</html>
"""
    target.write_text(html, encoding="utf-8")
    return str(target.resolve())
