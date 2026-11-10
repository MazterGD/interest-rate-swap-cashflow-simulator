# Engineering Manager — irs-simulator
The full breakdown is in **/WORK_PLAN.md**, the team's source of truth.

| # | Workstream | Size |
|---|---|---|
| M1 | Engine + pipeline integration tests | ~1 day |
| M2 | Scenarios + rate editor | ~1 day |
| M3 | Inputs + validation | ~1 day |
| M4 | Summary, table, CSV, formatting | ~1 day |
| M5 | Charts | ~1 day |
| M6 | Kickoff skeleton + CI, app shell, theme, explainer, app integration tests, README | ~1–1.5 days |

**Sequencing:** kickoff skeleton + CI (M6, ~45 min) -> all six in parallel -> PRs + cross-review -> integration day.
**Dependencies between members:** none after kickoff (ADR-002).
**Risks:** contract mistakes (mitigated by the change process); Streamlit `data_editor` state quirks (M2, spec §7 key).
