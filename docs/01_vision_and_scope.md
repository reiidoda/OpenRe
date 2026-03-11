# Vision and Scope

## Vision
OpenRe is the default framework for testing AI agents.

OpenRe exists to make agent behavior measurable, testable, auditable, and safer with software-engineering discipline.

## Mission
Give teams a standard workflow for agent quality:
1. define benchmark expectations
2. execute reproducible runs
3. inspect traces and failures
4. evaluate and score outcomes
5. detect regressions
6. improve and re-validate

## Positioning
OpenRe is:
- pytest for AI agents
- CI/CD quality gates for agent behavior
- observability + evaluation + benchmarking + safety in one workflow

## Why this matters
Most teams still validate agents through demos and ad-hoc prompts.
OpenRe formalizes agent engineering with:
- reproducible benchmark suites
- step-level traces and run lineage
- regression gates in CI
- risk-aware approval workflows

## Impact hypothesis
If OpenRe is built and adopted broadly, it can improve AI products by:
- catching regressions earlier
- making behavior changes auditable
- enforcing safer action policies
- making improvement loops data-driven and repeatable

## Explicit limitation
OpenRe does not directly invent a more capable base model architecture.
Its impact is strongest on engineering quality, reliability, safety, and governance for AI systems built by many teams.

## In scope
- benchmark-first run orchestration
- trace-first observability
- evaluation and regression framework
- safety and approval gates
- reporting and leaderboard artifacts
- interfaces: CLI, SDK, API, dashboard, CI integrations, plugins

## Out of scope (current phase)
- consumer chat product UX
- unrestricted autonomous destructive actions
- full cloud-provider abstraction in first release

## Definition of done (program-level)
- install and run benchmark in under five minutes
- every run emits trace + score + report artifacts
- CI can block regressions automatically
- risky actions are policy-gated and auditable
- results are reproducible and inspectable
