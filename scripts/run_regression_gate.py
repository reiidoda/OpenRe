#!/usr/bin/env python3
"""Run CI regression gate using repository-configured thresholds."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from agent_workbench.evals.regression_gate import format_regression_gate_markdown
from agent_workbench.evals.regression_gate import load_regression_gate_config
from agent_workbench.evals.regression_gate import regression_gate_payload
from agent_workbench.evals.regression_gate import run_regression_gate


def _append_step_summary(markdown: str) -> None:
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    path = Path(summary_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(markdown)
        handle.write("\n")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OpenRe regression gate.")
    parser.add_argument(
        "--config",
        default="configs/ci/regression_gate.yaml",
        help="Path to regression-gate YAML config.",
    )
    parser.add_argument(
        "--artifact-root",
        default=".artifacts",
        help="Artifact root used by runner.",
    )
    parser.add_argument(
        "--output",
        default=".artifacts/regression/gate_report.json",
        help="Path to write machine-readable regression report JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    config_path = Path(args.config)
    artifact_root = Path(args.artifact_root)
    output_path = Path(args.output)

    config = load_regression_gate_config(config_path)
    result = run_regression_gate(config, artifact_root=artifact_root)

    markdown = format_regression_gate_markdown(result)
    payload = regression_gate_payload(result)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    print(markdown)
    print(f"\nJSON report: {output_path}")
    _append_step_summary(markdown + f"\n\nJSON report: `{output_path}`")

    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
