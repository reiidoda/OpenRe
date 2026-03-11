#!/usr/bin/env python3
"""Print report path for a run id."""

from __future__ import annotations

import argparse
import subprocess


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id")
    args = parser.parse_args()

    subprocess.run(
        ["openre", "report", "--run-id", args.run_id, "--format", "html"],
        check=True,
    )
