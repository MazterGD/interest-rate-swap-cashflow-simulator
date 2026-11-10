# ADR-002: Frozen shared contracts + walking skeleton for 6-way parallel work

**Status:** Accepted
**Date:** 2026-11-10
**Feature:** irs-simulator
**Author:** 10x-Team (Architect + Staff Engineer + Engineering Manager)

## Context
Six members must build at the same time without waiting on each other or creating merge conflicts. Modules depend on each other's types: the UI needs the engine output, the chart needs cash flows, and so on.

## Decision
1. All shared types live in `swap/models.py`, written in full in spec §6.1. All cross-module function signatures are listed in spec §6.2. Both are **frozen**.
2. At kickoff, Member 6 commits a **walking skeleton**: the real `models.py` plus every module with its frozen signature and a placeholder body, and `app.py` fully wired. The app runs end to end from the first hour.
3. Every file has exactly one owner (WORK_PLAN.md). Members replace only their own placeholders.
4. Contracts change only through the WORK_PLAN contract-change process, which needs agreement from every affected owner.

## Alternatives Considered
| Alternative | Pros | Cons | Why Not |
|---|---|---|---|
| Sequential build (engine first, then UI) | No stubs needed | Members idle while waiting; the critical path is long | Violates "no dependency between members" |
| Each member defines their own types, then integrate | Freedom | Painful integration with type mismatches | High integration risk |
| Shared mock/fake module per member | Isolation | Duplicate fakes and drift | The skeleton is simpler |

## Consequences
### Positive
- Zero waiting, no merge conflicts, and `main` is always runnable.
- Integration day only swaps placeholders for real code that already matches the signatures.
### Negative
- Up-front design effort, and a ~30-minute kickoff before branching.
- Changing contracts is deliberately slow.
### Risks
- A contract turns out to be wrong mid-build. Mitigation: the lightweight change process, and the contracts are small (3 dataclasses, 2 enums, ~15 functions).

## Dependencies
- Depends on ADR-001's layering.
