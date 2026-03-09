# Security Threat Model

## Threats
- Unsafe external actions
- Prompt injection from web/files
- Secret leakage in traces
- Cost explosion via loops/retries

## Mitigations
- Isolation and allowlists
- Approval gates
- Secret redaction
- Max-step/max-cost budgets
- Immutable audit logs
