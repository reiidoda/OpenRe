"""CLI entrypoint for Open Agent Workbench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from agent_workbench.orchestration.runner import Runner


def _print(payload: dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="awb", description="Open Agent Workbench CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run benchmark for one agent config")
    run.add_argument("--dataset", required=True)
    run.add_argument("--config", required=True)

    compare = sub.add_parser("compare", help="Run benchmark for multiple configs")
    compare.add_argument("--dataset", required=True)
    compare.add_argument("--configs", nargs="+", required=True)

    evaluate = sub.add_parser("eval", help="Evaluate a previous run")
    evaluate.add_argument("--run-id", required=True)

    optimize = sub.add_parser("optimize", help="Run optimizer search")
    optimize.add_argument("--dataset", required=True)
    optimize.add_argument("--search-space", required=True)

    approve = sub.add_parser("approve", help="Resolve approval request")
    approve.add_argument("--request-id", required=True)
    approve.add_argument("--decision", choices=["approve", "deny"], required=True)

    report = sub.add_parser("report", help="Get report paths")
    report.add_argument("--run-id", required=True)
    report.add_argument("--format", choices=["json", "csv", "html"], required=True)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runner = Runner(artifact_root=Path(".artifacts"))

    if args.command == "run":
        payload = runner.run(dataset=args.dataset, config_paths=[args.config])
        _print(payload)
        return 0

    if args.command == "compare":
        payload = runner.run(dataset=args.dataset, config_paths=args.configs)
        _print(payload)
        return 0

    if args.command == "eval":
        _print({"run_id": args.run_id, "status": "planned", "message": "Eval pipeline scaffolded"})
        return 0

    if args.command == "optimize":
        _print(
            {
                "dataset": args.dataset,
                "search_space": args.search_space,
                "status": "planned",
                "message": "Optimizer pipeline scaffolded",
            }
        )
        return 0

    if args.command == "approve":
        _print(
            {
                "request_id": args.request_id,
                "decision": args.decision,
                "status": "recorded",
            }
        )
        return 0

    if args.command == "report":
        run_dir = Path(".artifacts") / "reports" / args.run_id
        _print({"run_id": args.run_id, "format": args.format, "path": str(run_dir / f"report.{args.format}")})
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
