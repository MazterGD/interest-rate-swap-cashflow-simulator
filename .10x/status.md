# Status — irs-simulator

**Current phase:** Verification (Phase 5). All six workstreams are merged, integration-day xfails are removed, and D8 learning aids are added.
**Last updated:** 2026-11-12

| Phase | State | Output |
|---|---|---|
| 0 Brainstorming | ✅ Done | `.10x/specs/2026-11-10-irs-simulator-design.md`, README decision log |
| 1 Strategy | ✅ Done | `decisions/cto/`, `decisions/product-manager/` |
| 2 Design | ✅ Done | ADR-001, ADR-002, ADR-003, `decisions/architect/`, `decisions/staff-engineer/` |
| 3 Planning | ✅ Done | `/WORK_PLAN.md`, `decisions/engineering-manager/`, `decisions/senior-engineer/` |
| 4 Implementation | ✅ Done | M1–M6 merged; D8 learning aids added on `patch-1` (2026-11-12) |
| 5 Verification | 🔄 In progress | CI green (unit + integration), no `xfail`s left, demo checklist; QA and security reviews in `.10x/reviews/` |
| 6 Delivery | ⏳ | Local run only (no deployment by requirement); CI runs tests on PRs |

## Task board

| Task | Owner | State |
|---|---|---|
| Step 0: kickoff walking skeleton + CI workflow + smoke test | M6 | ☑ (2026-11-10) |
| Enable branch protection on `main` (green CI + 1 approval) | Repo owner | ☐ |
| Swap engine + unit tests + pipeline integration tests | M1 | ☑ (2026-11-11) |
| Rate scenarios + editor + tests | M2 | ☑ (merged; preset-deselect crash fixed 2026-11-12) |
| Inputs + validation + tests | M3 | ☑ (merged via PR #5) |
| Summary, table, CSV, formatting + tests | M4 | ☑ (merged) |
| Charts + tests | M5 | ☑ (merged; zero bar grey + cumulative panel 2026-11-12) |
| App shell, theme, explainer, app integration tests, README Running | M6 | ☑ (merged; walkthrough added 2026-11-12) |
| Integration day: remove `xfail`s + demo checklist | All | ◐ xfails removed, 153 tests pass (2026-11-12); team still has to walk through the demo checklist live |
| D8 learning aids: walkthrough, tooltips, cumulative chart, explainer | M2/M3/M5/M6 (team-agreed cross-edit) | ☑ on `patch-1` (2026-11-12); needs PR + review |
| QA and security reviews in `.10x/reviews/` | QA / Security | ☐ |

When you finish a task, tick it here in your PR, and add your section to `decisions/sde/irs-simulator.md`.

## Blockers
None.
