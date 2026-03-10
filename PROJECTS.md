# Project Board Plan

## Board columns

- Backlog
- Ready
- In Progress
- In Review
- Done

## Label taxonomy

- `milestone:M0` ... `milestone:M6`
- `type:feature`
- `type:docs`
- `type:test`
- `type:safety`
- `type:infra`
- `priority:P0` ... `priority:P3`

## Planning lens
- Prioritize work that improves measurability, safety, and repeatability first.
- Require explicit benchmark and risk-impact statements in milestone planning.
- Treat optimization work as valid only when eval evidence improves.

## Program checkpoints
1. Regression prevention effectiveness (quality and safety).
2. Approval-policy enforcement coverage.
3. Trace completeness and auditability.
4. Cost/latency performance trends under benchmark load.

## Workflow

1. Open issue from `project/issues/<milestone>/*.md`.
2. Create branch: `fix/issue-<id>-<slug>`.
3. Implement + PR.
4. Merge when checks pass.
