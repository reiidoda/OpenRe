# Object-Oriented Design

## Key interfaces
- `AgentAdapter`
- `ToolExecutor`
- `TraceSink`
- `Evaluator`
- `Optimizer`
- `ApprovalGateway`
- `DatasetProvider`

## Collaboration
`RunService` orchestrates entities via interfaces and concrete adapters.

## Interface map

```mermaid
flowchart LR
  RS["RunService"] --> AA["AgentAdapter"]
  RS --> TS["TraceSink"]
  RS --> AG["ApprovalGateway"]
  RS --> DP["DatasetProvider"]
  RS --> TE["ToolExecutor"]
  RS --> AR["ArtifactStore"]
  ES["EvalService"] --> EV["Evaluator"]
  OS["OptimizeService"] --> OP["Optimizer"]
  APS["ApprovalService"] --> AG
```

## Runtime collaboration sequence

```mermaid
sequenceDiagram
  participant Runner as Runner
  participant RunService as RunService
  participant Policy as PolicyEngine
  participant Adapter as AgentAdapter
  participant Trace as TraceSink
  participant Eval as EvalService
  participant Report as ReportService

  Runner->>RunService: create_session(dataset, configs)
  Runner->>Trace: write(prompt_sent)
  Runner->>Policy: evaluate(risk)
  alt policy requires approval
    Policy-->>Runner: WAITING_APPROVAL
    Runner->>Trace: write(approval_requested)
  end
  Runner->>Adapter: run_task(task, config)
  Adapter-->>Runner: final_output
  Runner->>Trace: write(completed)
  Runner->>Eval: evaluate(output, expected)
  Eval-->>Runner: EvaluationResult[]
  Runner->>Report: summarize(BenchmarkReport)
```
