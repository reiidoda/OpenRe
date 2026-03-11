# Design Principles and UML

## Design principles
- Separation of concerns and clear bounded contexts.
- SOLID for core domain abstractions.
- DRY for shared policy and validation logic.
- KISS and YAGNI for runtime-critical paths.
- Explicit dependencies over hidden side effects.

## Design patterns in OpenRe
- Strategy: evaluators, optimizers, retry policies.
- Adapter: OpenAI/Opik/local providers.
- Factory: config-based object construction.
- Observer: trace/event subscribers.
- Chain of Responsibility: safety rule pipeline.
- State Machine: task lifecycle.
- Repository: storage abstraction.

## UML class view

```mermaid
classDiagram
  class Runner
  class TaskSpec
  class AgentConfig
  class TraceEvent
  class EvaluationResult
  class BenchmarkReport
  class AgentAdapter
  class Evaluator
  class TraceSink
  class ApprovalGateway

  Runner --> TaskSpec
  Runner --> AgentConfig
  Runner --> AgentAdapter
  Runner --> TraceSink
  Runner --> Evaluator
  Runner --> BenchmarkReport
  ApprovalGateway --> Runner
  TraceEvent --> Runner
```

## UML component view

```mermaid
flowchart LR
  CLI["CLI/API"] --> Runner
  Runner --> DatasetLoader
  Runner --> ConfigLoader
  Runner --> AgentAdapter
  Runner --> TraceSink
  Runner --> EvalHarness
  Runner --> ReportExporter
  Runner --> PolicyEngine
```

## UML deployment view

```mermaid
flowchart TB
  DevClient["User/Client"] --> Edge["CDN/Proxy"]
  Edge --> ApiNode["API Nodes"]
  ApiNode --> WorkerPool["Run Workers"]
  ApiNode --> Cache["Redis"]
  WorkerPool --> DBCluster["Domain DB Cluster"]
  WorkerPool --> Broker["Event Broker"]
  Broker --> Analytics["Trace/Metrics Pipeline"]
```
