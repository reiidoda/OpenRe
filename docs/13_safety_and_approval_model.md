# Safety and Approval Model

## Risk levels
- LOW: read-only operations
- MEDIUM: browser navigation/form drafting
- HIGH: authenticated changes
- CRITICAL: irreversible actions

## Policy defaults
- Default deny for destructive actions.
- Allowlists for domain-restricted tools.
- Human approval required for HIGH/CRITICAL.
- Audit all decisions.
