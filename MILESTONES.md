# Milestones

## Guiding statement
OpenRe aims to be the standard way to test AI agents before shipping them.

## M0 - Foundation for reproducible evaluation
- Goal: installable baseline with deterministic local run artifacts.
- Exit criteria:
  - fresh clone executes a benchmark run successfully
  - run emits trace + JSON/CSV/HTML artifacts

## M1 - Comparable multi-config execution
- Goal: execute identical tasks across multiple configs with shared contracts.
- Exit criteria:
  - compare command enforces valid multi-config inputs
  - run metadata and artifacts persist through storage adapters
  - result table + summary are generated for each run

## M2 - Eval and regression governance
- Goal: enforce eval-driven quality gates in CI.
- Exit criteria:
  - output and trace graders integrated
  - configurable regression thresholds block PRs
  - failure labels map to trace evidence

## M3 - Optimization and controlled improvement
- Goal: optimize prompts/tools/configs using explicit objective tradeoffs.
- Exit criteria:
  - optimizer generates ranked candidates
  - dev/test split validation prevents overfitting
  - best-config registry tracks promotion history

## M4 - Safety and human oversight
- Goal: policy-driven execution with mandatory approvals for risky actions.
- Exit criteria:
  - high-risk actions require approval before continuation
  - allowlist and policy checks are enforced by default
  - immutable audit trail exists for safety decisions

## M5 - Multimodal maturity and narrative polish
- Goal: deliver image/browser/computer task support with public benchmark storytelling.
- Exit criteria:
  - multimodal tasks run and score consistently
  - dashboard/reporting path supports visual inspection
  - README/demo assets show reproducible evidence

## M6 - Enterprise hardening and distributed scale
- Goal: production reliability, scalability, and security posture.
- Exit criteria:
  - domain data ownership and event contracts are defined
  - load/backpressure/autoscaling controls are validated
  - SRE + cost governance policies are active

## M7 - Architecture and quality governance package
- Goal: complete engineering governance docs and enforceable quality model.
- Exit criteria:
  - HLD/LLD/UML documents align with implementation boundaries
  - SCM/release/maintenance standards are documented and used
  - quality metrics and ownership model are operational

## M8 - AI improvement science and learning loops
- Goal: turn traces and failures into continuous improvement signals.
- Exit criteria:
  - confidence-aware scoring and safety-adjusted scoring implemented
  - failure clustering and drift analysis available
  - safety scorecards published per release candidate

## M9 - Product interfaces and developer experience
- Goal: deliver canonical interfaces for broad adoption.
- Exit criteria:
  - `openre` CLI command family is complete
  - Python SDK and REST API stable contracts published
  - gRPC contract draft available for enterprise integration

## M10 - Dashboard and plugin ecosystem
- Goal: maximize inspectability and extensibility.
- Exit criteria:
  - trace viewer + approval queue + leaderboard UI available
  - plugin SDK for adapters/evaluators/exporters is documented
  - plugin contract tests run in CI

## M11 - Benchmark packs and GA readiness
- Goal: release candidate to general availability path.
- Exit criteria:
  - Pack A-E benchmark suites are shipped/versioned
  - CI templates and migration policy are published
  - GA checklist passes with reproducibility, safety, and regression gates
