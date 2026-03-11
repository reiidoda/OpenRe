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

## Objective
`0.50 quality + 0.20 trace + 0.10 safety + 0.10 latency + 0.10 cost`

## Loop
Candidate generation -> run -> evaluate -> rank -> select -> validate.
