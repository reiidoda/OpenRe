# Database Strategy and Distributed Data Design

## Strategy
Use domain-owned data stores with explicit contracts. Avoid tightly-coupled shared schemas across bounded contexts.

## Core storage classes

Relational state (primary):
- tasks
- configs
- runs
- task runs
- evaluations
- approvals
- reports metadata

Trace/event data:
- append-only event records
- optional derived/materialized views for query-heavy dashboards

Artifact storage:
- JSON/CSV/HTML reports
- screenshots
- tool outputs
- run attachments

Cache/coordination:
- Redis for queue coordination, cache, and lightweight locks

Optional semantic index:
- vector store for semantic trace/task search

## Domain data topology example
- `run_db`
- `trace_db`
- `eval_db`
- `approval_db`
- `report_db`
- `audit_db`

## Consistency model
- strong consistency for approvals, security policy decisions, billing-sensitive paths
- eventual consistency for analytics/leaderboards/derived trend views
- idempotent writes for event consumers

## Cross-domain transaction model
- avoid distributed 2PC
- use outbox pattern
- use idempotent consumers
- use saga-style orchestration for multi-step workflows

## Event contract baseline
Required fields:
- `event_id`
- `correlation_id`
- `causation_id`
- `timestamp`
- `event_type`
- `version`

## Retention and backup
- PITR for operational relational stores
- immutable retention tier for audit logs
- lifecycle policies for large trace/artifact data
- scheduled restore drills with RPO/RTO objectives

## Distributed runtime considerations
- partition by run_id/benchmark_id for horizontal scale
- backpressure and admission controls
- queue depth and p95 latency SLO monitoring
- retry with dead-letter handling for failing workers

## Reference
See [32_openre_default_framework_spec.md](32_openre_default_framework_spec.md) for full deployment and subsystem context.
