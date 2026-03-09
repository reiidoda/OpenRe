# Domain Model

## Entities
- `TaskSpec`
- `RunSession`
- `TaskRun`
- `TraceEvent`
- `EvaluationResult`
- `ApprovalRequest`
- `BenchmarkReport`

## Value objects
- `Score`
- `RiskLevel`
- `TokenCost`

## Entity graph

```mermaid
classDiagram
  class TaskSpec {
    +task_id: str
    +instruction: str
    +modality: text|image|browser|computer
    +risk_profile: RiskLevel
    +tags: list
  }

  class RunSession {
    +run_id: str
    +dataset_id: str
    +config_ids: list
    +status: RunStatus
  }

  class TaskRun {
    +task_run_id: str
    +run_id: str
    +task_id: str
    +config_id: str
    +status: TaskRunStatus
    +scores: dict
  }

  class TraceEvent {
    +event_id: str
    +run_id: str
    +task_run_id: str
    +kind: TraceEventKind
  }

  class EvaluationResult {
    +evaluator_name: str
    +metric_name: str
    +score: float
  }

  class ApprovalRequest {
    +request_id: str
    +task_run_id: str
    +action: str
    +risk_level: RiskLevel
    +status: ApprovalStatus
  }

  class BenchmarkReport {
    +dataset_id: str
    +compared_configs: list
    +summary_table: list
    +best_config: str
  }

  class RiskLevel {
    <<enumeration>>
    LOW
    MEDIUM
    HIGH
    CRITICAL
  }

  class Score {
    +value: float
    +max_value: float
    +normalized(): float
  }

  class TokenCost {
    +input_tokens: int
    +output_tokens: int
    +usd: float
  }

  RunSession "1" --> "*" TaskRun : contains
  TaskSpec "1" --> "*" TaskRun : executed_as
  TaskRun "1" --> "*" TraceEvent : emits
  TaskRun "1" --> "*" EvaluationResult : produces
  TaskRun "0..1" --> "0..1" ApprovalRequest : may_request
  RunSession "1" --> "1" BenchmarkReport : summarized_by
  TaskSpec --> RiskLevel
  ApprovalRequest --> RiskLevel
```
