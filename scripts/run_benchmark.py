#!/usr/bin/env python3
"""Run baseline comparison benchmark from local scaffold."""

from __future__ import annotations

import subprocess


if __name__ == "__main__":
    subprocess.run(
        [
            "openre",
            "compare",
            "--dataset",
            "datasets/research_assistant_v1",
            "--configs",
            "configs/agents/research_basic.yaml",
            "configs/agents/research_multimodal.yaml",
        ],
        check=True,
    )
