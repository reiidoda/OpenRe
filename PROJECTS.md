# Project Board Plan

## Board columns

- Backlog
- Ready
- In Progress
- In Review
- Done

## Label taxonomy

- `milestone:M0` ... `milestone:M11`
- `type:feature`
- `type:docs`
- `type:test`
- `type:safety`
- `type:infra`
- `type:ux`
- `type:api`
- `type:sdk`
- `type:plugin`
- `priority:P0` ... `priority:P3`

## Planning principles

- Benchmark-first: no feature is complete without benchmark/eval impact.
- Trace-first: no result is accepted without inspectable run evidence.
- Safety-first: risky actions must be blocked or approval-gated.
- Reproducibility-first: all run outcomes require provenance metadata.

## Backlog organization

- M0-M5: core execution, evaluation, safety, multimodal foundations.
- M6-M8: enterprise hardening and AI improvement science.
- M9-M11: product interfaces, plugin ecosystem, benchmark pack GA.

## Definition of ready

An issue can move to `Ready` only when it has:
- explicit acceptance criteria
- benchmark/eval impact statement
- safety impact statement
- test plan (unit/integration/contract/e2e as applicable)

## Definition of done

An issue can move to `Done` only when:
- implementation is merged
- required tests and checks pass
- docs are updated (if behavior changed)
- benchmark or regression evidence is attached
- safety approval impact is documented when relevant

## Workflow

1. Pick an issue from the current milestone.
2. Create branch: `fix/issue-<id>-<slug>`.
3. Implement with tests and docs.
4. Open PR with validation summary.
5. Merge after checks and review pass.
6. Move issue to Done and proceed to next.

## Program checkpoints

1. Regression prevention effectiveness.
2. Approval-policy enforcement coverage.
3. Trace completeness and auditability.
4. Cost/latency trend under benchmark load.
5. Time-to-failure-localization from trace evidence.
