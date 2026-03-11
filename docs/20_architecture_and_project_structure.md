# Architecture and Project Structure

## Architecture style
- Hexagonal architecture for domain isolation.
- Config-driven runtime for reproducibility.
- Event-oriented telemetry for observability and replay.

## Container-level view

```mermaid
flowchart TB
  Gateway["CLI/API Gateway"] --> Orchestration["Orchestration"]
  Orchestration --> Adapters["Provider Adapters"]
  Orchestration --> Safety["Safety/Approval"]
  Orchestration --> Evals["Evals/Regression"]
  Orchestration --> Reports["Reporting"]
  Orchestration --> Data["Dataset/Config Services"]
  Orchestration --> Events["Events/Trace Stream"]

  Events --> TraceStore["Trace Store"]
  Events --> MetricStore["Metrics Store"]
  Reports --> ArtifactStore["Artifact Store"]
```

## Repository structure map

```text
src/agent_workbench/
  app/                 # CLI/API entrypoints and runtime settings
  domain/              # entities, value objects, interfaces, core services
  orchestration/       # runner, scheduling, lifecycle state machine
  adapters/            # OpenAI/Opik/local/storage integrations
  tools/               # local/web/browser/computer tool contracts
  evals/               # graders, metrics, regression policy
  optimizer/           # config and prompt search strategies
  safety/              # risk classification, approval, audit
  reporting/           # JSON/CSV/HTML benchmark outputs
  utils/               # ID, clock, serialization, hashing utilities
```

## Module ownership recommendations
- Domain: strict backward compatibility expectations.
- Adapters: provider-specific churn isolated behind interfaces.
- Evals/safety: policy-critical reviews + mandatory regression tests.
- Docs/configs: versioned alongside code changes.

## Architecture governance
- Architectural changes require ADR updates.
- Performance/security-sensitive changes require benchmark + risk impact section in PR.
