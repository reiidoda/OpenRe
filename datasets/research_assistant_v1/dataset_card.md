# research_assistant_v1

## Purpose
Baseline dataset for research-assistant tasks over local files and web sources.

## Composition
- 5 reproducible tasks covering summarization, comparison, citation retrieval, multimodal reasoning, and safety-aware planning.
- Mixed modalities to support a gradual path from text-first to browser/computer-enabled execution.

## Splits
- train: 3 tasks
- dev: 1 task
- test: 1 task

## Safety notes
- Every task includes a risk label (`LOW`, `MEDIUM`, `HIGH`) used by policy and approval-flow tests.
- Browser-oriented tasks are intentionally marked as higher risk to validate approval boundaries.
