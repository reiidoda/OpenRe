# Roadmap

## Strategic objective
Establish OpenRe as the default framework for testing AI agents by making agent development measurable, testable, auditable, and safer.

## Program phases

## M0 - Repo foundation
- Installable scaffold, baseline CLI, sample dataset, local trace/report artifacts.
- Outcome: fresh clone can execute one end-to-end run.

## M1 - Comparable execution baseline
- Dataset/config validation, multi-config execution, structured traces, JSON/CSV/HTML outputs, storage adapters.
- Outcome: same tasks across configs with consistent artifacts.

## M2 - Evaluation and regression loop
- Output + trace graders, regression thresholds, CI gates, failure labels.
- Outcome: quality and safety regressions fail CI predictably.

## M3 - Optimization loop
- Prompt/tool/config search, weighted objectives, dev/test validation, best-config registry.
- Outcome: repeatable quality improvements backed by benchmark evidence.

## M4 - Safety and approval core
- Policy chain, risk classifier, allowlists, approval queue, immutable audit logs.
- Outcome: risky actions are blocked or approval-gated with full evidence.

## M5 - Multimodal and polished demo
- Image tasks, browser/computer demo path, dashboard baseline, public benchmark narrative.
- Outcome: shareable project story with trace-backed evidence.

## M6 - Enterprise hardening and scale
- Event-driven internals, domain data ownership, load controls, SRE policies, cost governance.
- Outcome: production-ready reliability, scalability, and operational controls.

## M7 - Architecture, quality, and governance
- Complete HLD/LLD/UML package, SCM standards, quality model, maintenance model.
- Outcome: enterprise-grade architecture governance and execution clarity.

## M8 - AI improvement science
- Failure modeling, confidence-aware scoring, active benchmark curation, safety scorecards.
- Outcome: measurable long-term improvement loops for agent behavior.

## M9 - Product interfaces and developer experience
- Canonical `openre` CLI command set, Python SDK, REST API, gRPC contract, reproducible `openre init` template.
- Outcome: teams can adopt OpenRe without custom glue code.

## M10 - Dashboard and plugin ecosystem
- Trace viewer, approval queue UI, leaderboard UI, plugin SDKs for adapters/evaluators/exporters.
- Outcome: extensibility and inspectability become first-class adoption drivers.

## M11 - Benchmark packs and GA readiness
- Pack A-E benchmark suites, CI templates, release quality gates, migration/versioning policy, GA checklist.
- Outcome: open-source-ready platform with credible default benchmark content.

## Program KPIs
- Regression escape rate (target: decreasing trend).
- Safety policy violation rate (target: near zero with mandatory gating).
- Benchmark reproducibility rate (target: stable across environments).
- Median time-to-failure-localization via trace (target: decreasing trend).
- Cost per successful task and p95 latency (target: optimized within policy budget bands).

## Milestone dependency path
- M0 -> M1 -> M2 -> M3 -> M4 -> M5
- M6 and M7 run in parallel after M3/M4 baseline stability.
- M8 depends on stable eval/tracing signals from M2-M6.
- M9/M10 depend on stable core contracts from M1-M7.
- M11 finalizes productization after M8-M10.
