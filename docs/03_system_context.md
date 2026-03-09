# System Context

## Actors
- Maintainer
- Contributor
- Benchmark user
- Human approver

## External systems
- OpenAI model/tool stack
- Optional Opik observability stack
- Browser/computer harness
- Local artifact storage

## System boundary
Open Agent Workbench orchestrates tasks, tools, policies, traces, evals, and reports.

## Context graph

```mermaid
flowchart LR
  Maintainer["Maintainer"] --> CLI["Open Agent Workbench (CLI/API)"]
  Contributor["Contributor"] --> CLI
  BenchmarkUser["Benchmark User"] --> CLI
  Approver["Human Approver"] --> Approval["Approval Gateway"]

  CLI --> OpenAI["OpenAI Provider Stack"]
  CLI --> Opik["Opik (Optional)"]
  CLI --> Harness["Browser/Computer Harness"]
  CLI --> Storage["Local Storage (SQLite + Filesystem)"]
  CLI --> Approval

  Approval --> CLI
```
