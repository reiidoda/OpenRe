# Project Board Plan

## Board columns

- Backlog
- Ready
- In Progress
- In Review
- Done

## Label taxonomy

- `milestone:M0` ... `milestone:M5`
- `type:feature`
- `type:docs`
- `type:test`
- `type:safety`
- `type:infra`
- `priority:P0` ... `priority:P3`

## Workflow

1. Open issue from `project/issues/<milestone>/*.md`.
2. Create branch: `fix/issue-<id>-<slug>`.
3. Implement + PR.
4. Merge when checks pass.
