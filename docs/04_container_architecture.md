# Container Architecture

## Containers
- CLI/API: command and control entrypoint
- Orchestration: run lifecycle coordination
- Evaluation: grading and metrics
- Safety: policy checks and approval queue
- Observability: trace and event sinks
- Reporting: JSON/CSV/HTML exports

## Data flow
`CLI/API -> Orchestration -> Agent/Tools -> Trace -> Evals -> Reports`

## Container interaction graph

```mermaid
flowchart LR
  CLI["CLI/API"] --> Orchestrator["Orchestration"]
  Orchestrator --> Agent["Agent Adapter"]
  Orchestrator --> Safety["Safety"]
  Orchestrator --> Trace["Observability"]
  Agent --> Tools["Tools / Providers"]
  Safety --> Approval["Approval Queue"]
  Safety --> Trace
  Orchestrator --> Eval["Evaluation"]
  Eval --> Report["Reporting"]
  Trace --> Report
```

## Run sequence graph

```mermaid
sequenceDiagram
  participant U as User
  participant C as CLI/API
  participant O as Orchestration
  participant S as Safety
  participant A as Agent Adapter
  participant T as Trace Sink
  participant E as Evaluators
  participant R as Reporter

  U->>C: awb run/compare
  C->>O: start RunSession
  O->>S: pre-check action risk
  alt approval required
    S-->>O: WAITING_APPROVAL
    O->>T: approval_requested event
    S-->>O: approval_received
  end
  O->>A: execute task
  A->>T: prompt/tool/model events
  O->>E: score final output + trace
  E-->>O: evaluation results
  O->>R: export JSON/CSV/HTML
  R-->>U: artifact paths
```
