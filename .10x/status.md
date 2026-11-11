# Status — irs-simulator

**Current phase:** Implementation (Phase 4). The kickoff skeleton is on `main`, so members can branch now.
**Last updated:** 2026-11-11

| Phase | State | Output |
|---|---|---|
| 0 Brainstorming | ✅ Done | `.10x/specs/2026-11-10-irs-simulator-design.md`, README decision log |
| 1 Strategy | ✅ Done | `decisions/cto/`, `decisions/product-manager/` |
| 2 Design | ✅ Done | ADR-001, ADR-002, ADR-003, `decisions/architect/`, `decisions/staff-engineer/` |
| 3 Planning | ✅ Done | `/WORK_PLAN.md`, `decisions/engineering-manager/`, `decisions/senior-engineer/` |
| 4 Implementation | 🔄 In progress | Kickoff skeleton done (M6); M1–M6 in parallel |
| 5 Verification | ⏳ | CI green (unit + integration), no `xfail`s left, demo checklist; QA and security reviews in `.10x/reviews/` |
| 6 Delivery | ⏳ | Local run only (no deployment by requirement); CI runs tests on PRs |

## Task board

| Task | Owner | State |
|---|---|---|
| Step 0: kickoff walking skeleton + CI workflow + smoke test | M6 | ☑ (2026-11-10) |
| Enable branch protection on `main` (green CI + 1 approval) | Repo owner | ☐ |
| Swap engine + unit tests + pipeline integration tests | M1 | ☐ |
| Rate scenarios + editor + tests | M2 | ☐ |
| Inputs + validation + tests | M3 | ☑ Implemented and verified locally on `M3-mok` (2026-11-11); PR, CI and review pending |
| Summary, table, CSV, formatting + tests | M4 | ☐ |
| Charts + tests | M5 | ☐ |
| App shell, theme, explainer, app integration tests, README Running | M6 | 🔄 Built on `m6-shell`; the app tests stay `xfail` until M1/M3/M4 merge |
| Integration day: remove `xfail`s + demo checklist | All | ☐ |

When you finish a task, tick it here in your PR, and add your section to `decisions/sde/irs-simulator.md`.

## Blockers
None.
