"""CLI entrypoint for Open Agent Workbench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from typing import Sequence
from typing import TextIO

from agent_workbench.orchestration.runner import Runner


def _emit(payload: dict[str, Any], *, stream: TextIO | None = None) -> None:
    if stream is None:
        stream = sys.stdout
    stream.write(json.dumps(payload, indent=2, sort_keys=True))
    stream.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="awb", description="Open Agent Workbench CLI")
    parser.add_argument(
        "--artifact-root",
        default=".artifacts",
        help="Directory for generated traces and report artifacts.",
    )
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


def _planned(command: str, **fields: Any) -> dict[str, Any]:
    return {"command": command, "status": "planned", **fields}


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runner = Runner(artifact_root=Path(args.artifact_root))

    try:
        if args.command == "run":
            payload = {
                "command": "run",
                **runner.run(dataset=args.dataset, config_paths=[args.config]),
            }
            _emit(payload)
            return 0

        if args.command == "compare":
            payload = {
                "command": "compare",
                **runner.run(dataset=args.dataset, config_paths=args.configs),
            }
            _emit(payload)
            return 0

        if args.command == "eval":
            _emit(
                _planned(
                    "eval",
                    run_id=args.run_id,
                    message="Eval pipeline scaffolded",
                )
            )
            return 0

        if args.command == "optimize":
            _emit(
                _planned(
                    "optimize",
                    dataset=args.dataset,
                    search_space=args.search_space,
                    message="Optimizer pipeline scaffolded",
                )
            )
            return 0

        if args.command == "approve":
            _emit(
                {
                    "command": "approve",
                    "request_id": args.request_id,
                    "decision": args.decision,
                    "status": "recorded",
                }
            )
            return 0

        if args.command == "report":
            run_dir = Path(args.artifact_root) / "reports" / args.run_id
            _emit(
                {
                    "command": "report",
                    "run_id": args.run_id,
                    "format": args.format,
                    "path": str(run_dir / f"report.{args.format}"),
                }
            )
            return 0

    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        _emit(
            {
                "command": str(args.command),
                "status": "error",
                "error": {"type": exc.__class__.__name__, "message": str(exc)},
            },
            stream=sys.stderr,
        )
        return 1

    _emit(
        {"status": "error", "error": {"type": "UnknownCommand", "message": "Unsupported command"}}
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
