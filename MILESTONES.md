# Milestones

## Guiding statement
OpenRe is intended to improve AI system development and deployment quality (evaluation, safety, governance, repeatability), not to directly invent a new base model architecture.

## M0 - Foundation for reproducible evaluation
- Goal: installable and credible baseline with deterministic local execution.
- Exit criteria:
  - fresh clone runs one end-to-end benchmark command
  - trace and report artifacts are generated predictably

## M1 - Comparable agent execution
- Goal: run identical tasks across multiple configs under shared contracts.
- Exit criteria:
  - same task runs across at least two configs
  - result table and trace artifacts are auto-generated

## M2 - Eval and regression governance
- Goal: enforce eval-driven development in CI.
- Exit criteria:
  - PRs fail on score regressions above threshold
  - failure labels and trace-grade outputs are present

## M3 - Optimization loop
- Goal: search and rank config variants with explicit objective tradeoffs.
- Exit criteria:
  - optimizer improves at least one dev metric
  - improvements are validated against held-out split

## M4 - Safety and human oversight
- Goal: policy checks, allowlists, approval queue, audit log.
- Exit criteria:
  - high-risk tool calls block without approval
  - all approvals/denials are audit logged with context

## M5 - Multimodal maturity and adoption
- Goal: image/browser workflows plus clear benchmark communication.
- Exit criteria:
  - shareable README + demo + HTML benchmark dashboard
  - reproducible failure-case and improvement narratives

## M6 - Enterprise scale and reliability
- Goal: production-grade architecture characteristics (SLOs, distributed data strategy, cost controls).
- Exit criteria:
  - reliability/error-budget policy is operational
  - domain-level data ownership and inter-DB contracts are documented and testable
  - API and security posture is benchmarked and continuously verified
