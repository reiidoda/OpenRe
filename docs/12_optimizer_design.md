# Optimizer Design

## Search space
- System prompts
- Tool schema text
- Tool ordering
- Routing/handoff rules
- Model and decoding parameters

## Prompt sweeper contract
- Input: base prompt + constraints (`concise`, `citations`, tool-usage mode, extra directives, max variants).
- Candidate IDs are deterministic (`prompt_000`, `prompt_001`, ...).
- Sweep output records candidate id, aggregate score, and per-task dev split scores.
- Ranking is deterministic: sort by descending score, then ascending candidate id.

## Tool schema sweeper contract
- Input: base tool schema + configured field-path search space (example: `strict`, `description`, `parameters.additionalProperties`).
- Candidate IDs are deterministic (`schema_000`, `schema_001`, ...).
- Each candidate outcome records `variant_id`, score, and trace id for run-level traceability.
- Safety prechecks execute before candidate run (policy decision + risk classification), and blocked variants are not executed.

## Objective
`0.50 quality + 0.20 trace + 0.10 safety + 0.10 latency + 0.10 cost`

## Weighted objective ranker
- Implementation: `WeightedObjectiveRanker` (`src/agent_workbench/optimizer/config_search.py`).
- Objective weights are configurable at runtime with a mapping under `weights`.
- Weights can be normalized automatically (`normalize_weights: true`).
- Tie handling is stable and deterministic: sort by descending score, then ascending candidate id.
- Legacy compatibility is preserved through `WeightedObjectiveSearch` weight fields (`quality_w`, `trace_w`, `safety_w`, `latency_w`, `cost_w`).

### Config example
```yaml
weights:
  task_quality: 0.50
  trace_quality: 0.20
  safety_compliance: 0.10
  latency_score: 0.10
  cost_efficiency: 0.10
normalize_weights: true
```

## Loop
Candidate generation -> run -> evaluate -> rank -> select -> validate.
