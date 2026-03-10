# Contributing

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
pre-commit install
make check
```

Run `make precommit` before opening a PR if you want to execute the full hook suite manually.

## Find a contribution

- Good first issues: [good first issue](https://github.com/reiidoda/OpenRe/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22)
- Help wanted: [help wanted](https://github.com/reiidoda/OpenRe/issues?q=is%3Aopen+is%3Aissue+label%3A%22help+wanted%22)
- Milestones: [milestones](https://github.com/reiidoda/OpenRe/milestones)

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
- Discoverability impact reviewed when docs/metadata are changed.

## Contribution lanes

- Datasets
- Evaluators
- Model/tool adapters
- Optimizer strategies
- Safety policies
- Reporting and developer experience
- Architecture and documentation
