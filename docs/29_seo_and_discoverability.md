# SEO and Discoverability Strategy

## Objective
Increase OpenRe discoverability on GitHub and Google for relevant technical searches while keeping content accurate and non-spammy.

## Scope
- GitHub search discoverability.
- Google indexing quality of repository pages and docs content.
- Packaging metadata discoverability (PyPI-style ecosystems).

## Important constraint
No repository can guarantee "top" ranking by itself. Ranking depends on authority signals, adoption, backlinks, stars, contribution activity, and query intent.

## GitHub discoverability checklist
- Strong repository description with core terms: AI agents, evaluation, benchmarking, tracing, safety.
- Repository topics aligned to search intent.
- Readme headline + first paragraph matching user queries.
- Frequent high-quality commits and release notes.
- Good issue/PR hygiene and active maintenance.

## Google discoverability checklist
- Clear headings (`H1/H2`) and semantic structure in README/docs.
- Internal linking between docs (topic hub model).
- Stable canonical terms across pages.
- High-value technical pages that answer specific intent.
- Fast-loading assets and minimal broken links.

## Content strategy
- Publish benchmark reports and postmortems as indexable markdown pages.
- Add comparison pages for common keywords (e.g., "agent eval framework", "LLM safety workbench").
- Keep changelog and roadmap updated to show project freshness.

## Metadata strategy
- `pyproject.toml`: keywords, classifiers, URLs.
- `CITATION.cff`: structured citation metadata.
- README badges and concise value proposition.

## Link quality and crawl health
- Enforce markdown link checks in CI.
- Avoid orphan docs; ensure every major doc is linked from README or docs index.
- Use descriptive link text instead of "click here".

## Security and trust signals
- Maintain `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, and license.
- Surface CI status, test coverage trend, and release cadence.

## Query intent clusters to target
- "AI agent evaluation framework"
- "LLM benchmark and trace tooling"
- "AI safety approval workflow"
- "multimodal agent observability"
- "agent regression testing"

## Operational metrics
- GitHub: stars/month, forks/month, issue response time, merged PR cadence.
- Docs: page views, referral sources, docs-to-contributor conversion.
- Search: impressions and CTR by query (if external docs site is connected to Search Console).
