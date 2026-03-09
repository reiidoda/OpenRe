# Optimizer Design

## Search space
- System prompts
- Tool schema text
- Tool ordering
- Routing/handoff rules
- Model and decoding parameters

## Objective
`0.50 quality + 0.20 trace + 0.10 safety + 0.10 latency + 0.10 cost`

## Loop
Candidate generation -> run -> evaluate -> rank -> select -> validate.
