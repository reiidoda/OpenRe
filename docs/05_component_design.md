# Component Design

## Core components
- `Runner`: dispatches task runs
- `StateMachine`: enforces lifecycle transitions
- `PolicyEngine`: evaluates risky actions
- `ApprovalQueue`: blocks/resumes actions
- `EvalHarness`: computes output and trace scores
- `ReportBuilder`: assembles benchmark outputs

## Coupling rules
- Domain depends only on interfaces.
- Adapters implement provider-specific behavior.
