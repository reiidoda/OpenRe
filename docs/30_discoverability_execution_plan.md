# Discoverability Execution Plan

## 30/60/90 day plan

### 0-30 days
- Finalize metadata and README keyword alignment.
- Add docs index references and link checks in CI.
- Publish first benchmark snapshot with reproducible artifacts.

### 31-60 days
- Publish technical deep dives (eval loop, safety model, trace analysis).
- Add docs for frequently searched comparisons and use cases.
- Standardize release notes with keyword-consistent structure.

### 61-90 days
- Create recurring benchmark trend reports.
- Publish architecture and operations case studies.
- Measure and tune content based on query and referral data.

## GitHub optimization actions
- Keep issue labels/milestones clean and searchable.
- Maintain clear PR titles and conventional commit messages.
- Tag releases and summarize user-visible improvements.

## Google optimization actions
- Ensure every core topic page has unique, intent-aligned heading structure.
- Expand internal cross-links from README -> docs and docs -> docs.
- Keep diagrams and examples close to explanatory text.

## Quality gate additions
- `make check` includes markdown link validation.
- PR template includes "discoverability impact" note for docs and naming changes.

## Risk controls
- Avoid keyword stuffing and duplicate near-identical pages.
- Prioritize technical depth and accuracy over marketing language.
- Keep claims measurable and source-backed.
