# API and CLI Spec

## CLI

Canonical command family:
- `openre init`
- `openre test`
- `openre run`
- `openre compare`
- `openre trace`
- `openre eval`
- `openre approve`
- `openre report`
- `openre leaderboard`

Compatibility alias:
- `awb` maps to the same CLI entrypoint during transition.

Example flows:

```bash
openre test --benchmark benchmarks/research.yaml --config configs/agents/research_basic.yaml
openre compare --dataset datasets/research_assistant_v1 --configs configs/agents/research_basic.yaml configs/agents/research_multimodal.yaml
openre trace run_142
openre report --run-id run_142 --format html
```

## REST API (target v1)

Run lifecycle:
- `POST /v1/runs`
- `GET /v1/runs/{id}`
- `POST /v1/runs/{id}/cancel`

Trace and artifacts:
- `GET /v1/runs/{id}/trace`
- `GET /v1/runs/{id}/report`
- `GET /v1/runs/{id}/artifacts`

Evaluation and comparison:
- `POST /v1/runs/{id}/evaluate`
- `POST /v1/benchmarks/execute`
- `POST /v1/configs/compare`
- `GET /v1/leaderboard`

Approvals:
- `GET /v1/approvals/pending`
- `POST /v1/approvals/{id}/approve`
- `POST /v1/approvals/{id}/deny`

## gRPC contract (draft)

Service families:
- `RunService`
- `TraceService`
- `ReportService`
- `ApprovalService`

Status:
- REST is implementation priority.
- gRPC is contract-first for enterprise integration.

## API conventions
- resource-oriented naming
- explicit versioning
- additive backward compatibility by default
- idempotency keys for write operations where needed
- structured error payloads with actionable diagnostics
