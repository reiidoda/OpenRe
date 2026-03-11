# Low-Level Design

## Runtime decomposition
- `Runner`: coordinates dataset/config execution.
- `DatasetLoader` and `ConfigLoader`: strict schema validation.
- `ResponsesAdapter`: model invocation contract.
- `JsonTraceSink`: append-only NDJSON event persistence.
- `EvalHarness`: output and trace scoring.

## Core request flow

```mermaid
sequenceDiagram
  participant CLI as CLI
  participant Runner as Runner
  participant DL as DatasetLoader
  participant CL as ConfigLoader
  participant Adapter as ResponsesAdapter
  participant Safety as PolicyEngine
  participant Sink as TraceSink
  participant Eval as EvalHarness

  CLI->>Runner: run(dataset, configs)
  Runner->>DL: load_tasks()
  Runner->>CL: load(config)
  Runner->>Safety: evaluate(action risk)
  Safety-->>Runner: allow / require_approval / deny
  Runner->>Adapter: run_task(task, config)
  Adapter-->>Runner: output_text
  Runner->>Sink: write(prompt_sent/model_output/tool_called/...)
  Runner->>Eval: evaluate(output, expected)
  Eval-->>Runner: scores + labels
```

## TaskRun state model

```mermaid
stateDiagram-v2
  [*] --> CREATED
  CREATED --> RUNNING
  RUNNING --> WAITING_APPROVAL
  WAITING_APPROVAL --> RESUMED
  WAITING_APPROVAL --> REJECTED
  RUNNING --> EVALUATING
  RESUMED --> EVALUATING
  EVALUATING --> COMPLETED
  RUNNING --> FAILED
  RESUMED --> FAILED
  EVALUATING --> FAILED
```

## Validation contracts
- Dataset rows must include: `task_id`, `instruction`, `modality`, `risk_label`.
- Agent config must include provider/model/tools/budgets and valid numeric bounds.
- Adapter must fail with actionable messages (path + field + reason).

## Error handling strategy
- User errors: deterministic validation exceptions with source context.
- Integration errors: retriable wrappers for transient network/tool failures.
- Safety errors: explicit deny responses, never silent fallthrough.

## Internal extension points
- `AgentAdapter` protocol for provider substitution.
- `Evaluator` strategy for score composition.
- `TraceSink` observer for local/cloud observability backends.
