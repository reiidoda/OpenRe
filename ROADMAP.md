# Roadmap

## Strategic objective
Make agent development measurable, testable, auditable, and safer through an eval-driven engineering workflow.

## M0 - Foundation for measurability
- Installable repo, baseline CLI, local traces, sample dataset.
- Outcome: reproducible baseline run in a fresh clone.

## M1 - Comparable execution baseline
- Dataset/config loaders, adapter contracts, structured traces, JSON/CSV export.
- Outcome: same tasks run across multiple configs with comparable outputs.

## M2 - Eval-driven quality loop
- Output + trace grading, regression gates, failure labels.
- Outcome: changes can be blocked on quality/safety regressions.

## M3 - Optimization and repeatable improvement
- Prompt/tool schema sweeps, ranking objective, best config registry.
- Outcome: benchmark-backed improvement loop beyond ad-hoc prompting.

## M4 - Safety and governance hardening
- Risk classifier, allowlists, approval queue, audit log, guarded computer-use stubs.
- Outcome: risky actions are policy-controlled and auditable.

## M5 - Multimodal adoption and evidence sharing
- Image tasks, browser/computer demo, HTML dashboard, diagrams, demo assets.
- Outcome: shareable benchmark narrative and reproducible artifacts for teams.

## M6 - Enterprise hardening and scale
- Domain database decomposition with inter-DB contracts.
- Event-driven scaling and reliability SLO rollout.
- API security hardening and protocol/edge strategy.
- Software quality metrics + SCM governance baseline.
- AI/ML system expansion roadmap with performance/cost guardrails.

## Program-level KPIs
- Regression escape rate (target: decreasing trend).
- Policy violation rate (target: near-zero with enforced gates).
- Benchmark reproducibility rate (target: stable across environments).
- Cost per successful task and p95 latency (target: optimized within budget bands).
