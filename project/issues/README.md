# Issue Backlog Pack

This folder contains issue specs grouped by milestone.

## How to use

1. Create a GitHub issue from a file in `project/issues/m*/`.
2. Keep title + acceptance criteria aligned with roadmap/milestones.
3. Apply labels noted in each issue.
4. Start a branch: `fix/issue-<id>-<slug>`.

## Milestone groups

- `m0`: foundation
- `m1`: comparable execution baseline
- `m2`: eval and regression loop
- `m3`: optimization loop
- `m4`: safety and approval
- `m5`: multimodal and polish
- `m6`: enterprise hardening and scale
- `m7`: architecture/quality/governance
- `m8`: AI improvement science
- `m9`: product interfaces and DX
- `m10`: dashboard and plugin ecosystem
- `m11`: benchmark packs and GA readiness

## Planning notes

- Every issue should include benchmark/eval impact.
- Safety-sensitive issues must include policy/audit impact.
- Contract changes must include migration/versioning notes.
