# ADR-003: Unit + integration tests, run by GitHub Actions on every PR

**Status:** Accepted
**Date:** 2026-11-10
**Feature:** irs-simulator
**Author:** 10x-Team (QA + DevOps + Architect)

## Context
Six people merge into one `main` branch in parallel. The original brief said "local only, no deployment", and the first plan therefore had no CI. The team then asked for unit and integration tests checked automatically when a PR is created. This adds CI for testing only. Deployment stays out of scope.

## Decision
- **Two test layers** in `tests/unit/` (one module in isolation, owned by its module owner) and `tests/integration/` (real modules together: the domain pipeline (M1) and the full app via Streamlit `AppTest` (M6), plus a smoke test that passes against the kickoff skeleton). Spec §10.
- **CI:** a single GitHub Actions workflow, `.github/workflows/tests.yml`, triggered on `pull_request` and `push` to `main`. It installs `requirements.txt` on Python 3.11 and runs `pytest -q`. It has read-only permissions, no secrets and no deploy step. The YAML is given verbatim in spec §12.
- **Merge gate:** branch protection on `main` requires a green `pytest` check plus one approval.
- Integration tests that depend on code not yet merged are marked `xfail(strict=False)`, and the marks are removed on integration day. CI therefore stays green while members work in parallel (keeps ADR-002 intact).

## Alternatives Considered
| Alternative | Pros | Cons | Why Not |
|---|---|---|---|
| No CI; run `pytest` locally by convention | Zero setup | Easy to forget; broken `main` blocks 5 other people | The team asked for automatic checks |
| GitLab CI / CircleCI / Jenkins | Capable | An extra account or server; the repo is on GitHub | Violates minimal setup |
| Matrix over Python 3.11–3.13 | Catches version issues | 3× the runs and slower feedback | YAGNI; 3.11 is the floor and newer versions are backward compatible for this code |
| Browser E2E (Playwright) for integration | Real browser | Heavy install, flaky, slow | `AppTest` covers the UI headlessly with no extra dependency |
| Separate lint job (ruff/flake8) | Style consistency | Another tool and dependency | YAGNI; review covers style |

## Consequences
### Positive
- Every PR is automatically checked against the spec's worked example and cross-module behaviour.
- `main` stays green and runnable for all six members.
- Free, with no new accounts and no new Python dependencies.
### Negative
- About 1–2 minutes of waiting per PR.
- The `xfail` bookkeeping must be cleaned up on integration day.
### Risks
- Someone weakens a test to get CI green. Mitigation: the WORK_PLAN rule never to skip or delete another member's test, plus review.
- Branch protection is unavailable on a private repo with a free plan. Mitigation: the team enforces "no merge on red" by hand (spec §12).

## Dependencies
- Builds on ADR-001 (pytest + AppTest) and ADR-002 (skeleton keeps CI green from day 1).
- Supersedes the "no CI" part of README requirement R2. Deployment remains out of scope.
