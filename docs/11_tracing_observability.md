# Tracing and Observability

## Event kinds
- prompt_sent
- model_output
- tool_called
- tool_result
- handoff
- approval_requested
- approval_received
- error
- completed

## Requirements
- Every task run emits structured events.
- Every report links back to traces.
