# Design Principles and UML

## Engineering principles
1. Every run is reproducible.
2. Every result is inspectable.
3. Every risky action is auditable.
4. Every benchmark is versioned.
5. Plugin-first extensibility is preserved.

## Required provenance fields
- config fingerprint
- git commit SHA
- dependency snapshot
- model identifier
- prompt version
- evaluator versions

## Patterns by subsystem
- Agent adapters: Adapter, Abstract Factory.
- Evaluators: Strategy, Composite.
- Policies: Chain of Responsibility, rules-engine style.
- Reporting: Builder, Template Method.
- Tracing: Observer, event-sourcing concepts.
- Run lifecycle: State Machine.
- Persistence: Repository + Unit of Work.

## Use case view

```mermaid
flowchart LR
  AIE["AI Engineer"] --> UC1["Define benchmark tasks"]
  AIE --> UC2["Run/compare benchmarks"]
  RES["Research Engineer"] --> UC3["Analyze traces and failures"]
  PT["Product Team"] --> UC4["Gate release on regressions"]
  REV["Reviewer"] --> UC5["Approve or deny risky actions"]
  CI["CI System"] --> UC6["Execute regression pipeline"]
  DEV["Plugin Developer"] --> UC7["Add adapter/evaluator/exporter plugins"]
```

## Class view

```mermaid
classDiagram
  class TaskSpec
  class AgentConfig
  class RunSession
  class TaskRun
  class TraceEvent
  class EvaluationResult
  class ApprovalRequest
  class BenchmarkReport

  RunSession --> TaskRun
  TaskRun --> TaskSpec
  RunSession --> AgentConfig
  TaskRun --> TraceEvent
  TaskRun --> EvaluationResult
  TaskRun --> ApprovalRequest
  RunSession --> BenchmarkReport
```

## Sequence view: benchmark execution

```mermaid
sequenceDiagram
  participant User
  participant CLI
  participant Orch as Orchestrator
  participant Safety
  participant Adapter
  participant Trace
  participant Eval
  participant Report

  User->>CLI: openre test benchmark.yaml
  CLI->>Orch: create run
  Orch->>Safety: pre-check action policy
  Orch->>Adapter: execute task
  Adapter-->>Trace: emit step events
  Adapter-->>Orch: final output
  Orch->>Eval: evaluate output + trace
  Eval-->>Orch: scores
  Orch->>Report: build artifacts
  Orch-->>CLI: summary + artifact paths
```

## Sequence view: risky action approval

```mermaid
sequenceDiagram
  participant Agent
  participant Safety
  participant Policy
  participant Queue
  participant Reviewer
  participant Audit

  Agent->>Safety: request risky action
  Safety->>Policy: assess
  Policy-->>Safety: require_approval
  Safety->>Queue: enqueue request
  Reviewer->>Queue: approve or deny
  Queue->>Safety: decision
  Safety->>Agent: resume or block
  Safety->>Audit: append immutable log
```
