# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pre-commit install
make check
```

Run `make precommit` before opening a PR if you want to execute the full hook suite manually.

## Branch and PR workflow

- `main` is always releasable.
- Work starts from a GitHub Issue.
- Branch format: `fix/issue-<id>-short-slug`.
- Open a PR using `.github/PULL_REQUEST_TEMPLATE.md`.
- A maintainer merges after checks pass.

## PR checklist

- Tests and lint pass.
- Benchmark delta is documented when behavior changes.
- Safety impact is assessed.
- Docs and configs are updated when needed.
- Traces/screenshots included for behavior changes.

## Contribution lanes

- Datasets
- Evaluators
- Model/tool adapters
- Optimizer strategies
- Safety policies
- Reporting
