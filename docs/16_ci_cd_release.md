# CI/CD and Release

## CI pipeline
1. Lint
2. Type check
3. Unit and integration tests
4. Regression benchmark gate
5. Security scanning
6. Build and publish artifacts

## Regression gate contract
- Workflow: `.github/workflows/eval-regression.yml` runs on pull requests.
- Config: `configs/ci/regression_gate.yaml` defines dataset, baseline/candidate configs, and per-metric thresholds.
- Output: CI job summary includes baseline vs candidate deltas and uploads `.artifacts/regression/gate_report.json`.

## Release policy
- Semantic versioning (`0.x` initially)
- Changelog required
- Benchmark snapshots published with minors
