# Handoff — Planning → Implementation (SDE team, M1–M6)

**From:** Engineering Manager + Senior Engineer · **Date:** 2026-11-10

## Read first
1. `/WORK_PLAN.md`: your workstream, the files you own, the checklist and the "done when" condition.
2. `.10x/specs/2026-11-10-irs-simulator-design.md`: the spec sections listed for your workstream. §3 (formulas), §6 (frozen contracts) and §9 (UI rules) matter most.
3. `.10x/decisions/senior-engineer/irs-simulator.md`: implementation tips and the tricky parts.
4. ADR-001 (stack + layering), ADR-002 (frozen contracts + walking skeleton) and ADR-003 (tests + CI).

## Order
1. M6 commits the kickoff skeleton, the CI workflow and the smoke test to `main` (WORK_PLAN Step 0). The repo owner enables branch protection.
2. Everyone branches (`m1-engine` … `m6-shell`) and replaces only their own placeholders.
3. Open a PR with unit tests (and integration tests for M1/M6) once your "done when" condition is met. CI must be green and one teammate approves.
4. Integration day: remove every `xfail` in `tests/integration/`, keep CI green, and walk through the demo checklist.

## Non-negotiables
- Contracts in spec §6 are frozen; changes go through the contract-change process.
- Rates are decimals in code. Sign: + = receive, − = pay.
- No new dependencies. Never add AI tools as commit co-authors.
