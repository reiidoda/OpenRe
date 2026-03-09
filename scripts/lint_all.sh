#!/usr/bin/env bash
set -euo pipefail

ruff check src tests examples scripts
mypy src
pytest
