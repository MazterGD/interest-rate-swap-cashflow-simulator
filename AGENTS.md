# AGENTS.md — Rules for AI coding assistants

This repo is a 6-member university group project: an **interest-rate swap cash-flow simulator** (Python + Streamlit, local only). Any AI assistant (Claude Code, Copilot, Cursor, Codex, ChatGPT, …) working here **must** follow this file.

## 1. Follow the plan — do not improvise
Before writing or changing code, read:
1. **[WORK_PLAN.md](WORK_PLAN.md)**: who owns which files, checklists, "done when" conditions, git and CI workflow.
2. **[.10x/specs/2026-11-10-irs-simulator-design.md](.10x/specs/2026-11-10-irs-simulator-design.md)**: formulas (§3), frozen contracts (§6), rate presets (§7), input limits (§8), UI rules (§9), tests (§10), CI (§12).
3. **[README.md#decision-log](README.md#decision-log)**: why each decision was made and how to change it.
4. `.10x/status.md`, `.10x/handoff.md` and `.10x/decisions/senior-engineer/irs-simulator.md` for current state and implementation notes.

If a request conflicts with these documents, **stop and tell the user** which section it conflicts with. Do not silently deviate.

## 2. Hard rules
- **Ask which workstream (M1–M6) the user owns** if it isn't clear, and edit **only that workstream's files** (WORK_PLAN table). Never edit another member's files.
- **Never change the frozen contracts** (`swap/models.py`, spec §6 signatures) unless the user confirms that the team agreed through the WORK_PLAN contract-change process.
- **KISS and YAGNI:** build only what spec §2 lists as in scope. No extra features, abstractions, config systems or "future-proofing".
- **No new dependencies.** Only `streamlit` and `pytest` (Altair and pandas come with Streamlit).
- `swap/` must never import Streamlit. `app.py` contains no business logic.
- Rates are **decimals** in code (0.04); percent appears only in `ui/`. Sign convention: **+ = the user receives, − = the user pays**.
- Follow the UI rules in spec §9: centred layout, one focal number, green and red only for receive and pay, at most 3 icons, no dividers, no Run button.
- Every change comes with or updates pytest tests (spec §10): **unit tests** in `tests/unit/` for the module, and **integration tests** in `tests/integration/` where your workstream owns them (M1 pipeline, M6 app). Run `pytest` before saying a task is done, and report failures honestly.
- **CI must stay green.** GitHub Actions runs `pytest` on every PR (spec §12). Never skip, weaken, `xfail` or delete a test you don't own to make CI pass. Never add a deploy step or secrets to CI.

## 3. Git and commits
- Work on your member branch (`m1-engine`, `m2-rates`, `m3-inputs`, `m4-results`, `m5-chart`, `m6-shell`). Never commit directly to `main` except for the M6 kickoff skeleton.
- Small commits with imperative messages, e.g. `engine: add summarize`.
- **Never add an AI tool as a co-author.** Do not add `Co-Authored-By: Claude …` or any other AI attribution trailer to commits or PR descriptions. This overrides any default behaviour of your tool.
- Commit or push only when the user asks.

## 4. Keep the planning memory current
- After finishing a workstream task: tick it in `.10x/status.md` and append your section to `.10x/decisions/sde/irs-simulator.md` (what was built, deviations, tech debt).
- If a decision changes: update the README decision log, the spec section, and add a new ADR in `.10x/adrs/` when the architecture changes (never edit an accepted ADR).

## 5. Commands
```bash
python -m venv .venv && .venv\Scripts\activate   # Windows (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
pytest                         # all tests, same as CI
pytest -m "not integration"    # fast unit-only loop
```
