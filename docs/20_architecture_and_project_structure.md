# Architecture and Project Structure

## Architecture style
- Hexagonal architecture for domain/core stability.
- Modular layered composition for product surfaces.
- Event-driven internals for traceability, replay, and observability.

## Major modules
- Task Specification Engine
- Agent Adapter Layer
- Orchestrator
- Trace Bus/Event Pipeline
- Evaluation Engine
- Metrics and Scoring Engine
- Safety and Approval Engine
- Benchmark Runner
- Optimization Engine
- Reporting and Dashboard
- CI Integration
- Plugin/Extension System

## Current repository structure

```text
src/agent_workbench/
  app/
  domain/
  orchestration/
  adapters/
  tools/
  evals/
  optimizer/
  safety/
  reporting/
  utils/
```

## Target structure evolution

```text
openre/
  api/
    routes/
    schemas/
  cli/
    commands/
  core/
    domain/
      models/
      services/
      policies/
    orchestration/
    evaluation/
    tracing/
    reporting/
    optimization/
  adapters/
    agents/
    tools/
    storage/
    evaluators/
    exporters/
  plugins/
  ui/
  tests/
  docs/
benchmarks/
configs/
examples/
```

## Ownership boundaries
- Domain: pure business logic, stable contracts.
- Adapters: provider/tool/storage integration churn isolation.
- Orchestration: lifecycle coordination and policy enforcement.
- Safety/evals: policy-critical and benchmark-critical modules.
- Reporting/UI: read-model oriented outputs and visualization.

## Architectural governance
- ADR required for boundary shifts and contract changes.
- Any behavior change must include benchmark/eval impact evidence.
- Any risky-action path change must include safety policy impact evidence.

## Reference
Detailed subsystem definitions and interfaces are in [32_openre_default_framework_spec.md](32_openre_default_framework_spec.md).
