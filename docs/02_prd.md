# Product Requirements Document

## Product goal
Make OpenRe the default framework for testing AI agents.

## Product statement
OpenRe provides benchmark execution, trace inspection, evaluation, regression gating, safety approvals, and reporting for AI-agent systems with engineering-grade repeatability.

## Personas
- AI Engineer
- Research Engineer
- Product Team
- Safety/Compliance Reviewer
- OSS Contributor

## Functional requirements
- define and version task specs, rubrics, and datasets
- register and version agent configurations
- execute tasks across config matrices
- capture full step-level traces and tool events
- evaluate outputs with deterministic and model-based evaluators
- calculate weighted scores and regression deltas
- compare baseline vs candidate runs
- block or approval-gate risky actions
- persist immutable audit logs
- export JSON/CSV/HTML artifacts
- provide leaderboard and run diff views
- support CLI, SDK, API, dashboard, and CI integration
- support plugin extensions for adapters/evaluators/exporters

## Non-functional requirements
- reproducibility and provenance
- reliability and idempotency
- scalability from local to distributed workers
- security and policy enforcement
- observability with trace lineage
- extensibility via stable contracts

## Product constraints
- OpenRe is a framework/platform, not a consumer chatbot.
- OpenRe does not claim base-model breakthroughs.
- Safety must be enforced by architecture, not convention.

## Success criteria
- first benchmark run in under five minutes
- run outputs include trace + score + report artifacts
- regression gates can fail CI automatically
- risky actions can be blocked/approval-gated
- benchmark results are reproducible and inspectable

## Release readiness criteria
- core interfaces documented and versioned
- benchmark packs published with baseline results
- migration notes and compatibility policy in place
- contributor onboarding and plugin docs complete
