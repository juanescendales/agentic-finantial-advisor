# Implementation Split

This branch defines integration contracts only. The graph topology is present so
teams can work in parallel, but node internals intentionally raise
`NotImplementedError`.

## Ownership

| Area | Files | Contract |
|---|---|---|
| Validation | `src/nodes/validator.py` | Validate `ticker`; set `company_name` or append `errors`. |
| News fetcher | `src/nodes/fetchers.py` | Populate `news_data: list[NewsItem]`. |
| Fundamentals fetcher | `src/nodes/fetchers.py` | Populate `fundamentals_data: FundamentalsSnapshot`. |
| Market fetcher | `src/nodes/fetchers.py` | Populate `market_data: MarketSnapshot`. |
| Analyst | `src/nodes/analyst.py` | Populate `analyst_report: AnalystReport`. |
| Advisor | `src/nodes/advisor.py` | Populate `decision: AdvisorDecision`. |
| Critic | `src/nodes/critic.py` | Populate `critic_verdict`, `critic_feedback`, and `revision_count` when looping. |
| Graph | `src/graph/builder.py` | Keep topology aligned with `docs/graph-design.md`. |

## Integration Rules

- Node functions receive graph state and return partial state updates.
- Each node owns only the fields listed in its contract.
- Do not add external API calls outside the node that owns that concern.
- Keep placeholder data out of node implementations; fail loudly until the real
  implementation exists.
