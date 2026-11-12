# Interest-Rate Swap Cash-Flow Simulator

A small local app that shows how a **plain-vanilla interest-rate swap** works. You enter the swap terms and a floating-rate path. The app compares the fixed and floating payments for each period and shows the **net settlement**, which is the only cash that actually changes hands.

> **Status:** 📐 Planned, not yet built. The design and the team work plan are complete. Implementation follows [WORK_PLAN.md](WORK_PLAN.md).

---

## Contents
- [What is an interest-rate swap?](#what-is-an-interest-rate-swap)
- [What the app does](#what-the-app-does)
- [Running it](#running-it)
- [Project structure](#project-structure)
- [Team and workstreams](#team-and-workstreams)
- [Decision log](#decision-log) ← **start here if you want to change something**
- [Where everything is documented](#where-everything-is-documented)

---

## What is an interest-rate swap?

Two parties agree to exchange interest payments on the same **notional** amount for a set period:

- **Fixed leg:** one side pays a fixed rate (e.g. 4% a year).
- **Floating leg:** the other side pays a floating rate that resets each period (e.g. a SOFR-style reference rate).
- The notional is **never exchanged**. Each period, only the **difference** is paid. This is the *net settlement*.

**Pay fixed** (a payer swap) gains when floating rates rise above the fixed rate. **Receive fixed** (a receiver swap) gains when they fall. Firms use swaps to hedge interest-rate risk, for example to turn a floating-rate loan into a fixed-cost one.

**Worked example** (used across the whole project as the reference test case): a notional of 1,000,000, 4% fixed, 2 years, semi-annual payments, pay fixed, with floating rates of 3.5%, 4.0%, 4.5% and 5.0%.

| Period | Fixed pmt | Floating pmt | Net (you) |
|---|---|---|---|
| 1 | 20,000 | 17,500 | −2,500 (pay) |
| 2 | 20,000 | 20,000 | 0 |
| 3 | 20,000 | 22,500 | +2,500 (receive) |
| 4 | 20,000 | 25,000 | +5,000 (receive) |
| **Total** | 80,000 | 85,000 | **+5,000** |

Formulas: `fixed = N × K × α`, `floating = N × Lᵢ × α`, and `net = floating − fixed` for pay-fixed (the sign flips for receive-fixed), where `α = 1 / payments per year`.

## What the app does

- Enter the notional, fixed rate, tenor and payment frequency.
- Switch between **Pay fixed** and **Receive fixed**.
- Pick a floating-rate path (**Flat / Rising / Falling / Volatile**) and edit any single period.
- See the **total net settlement** first, then a chart of rates and net payments, then the full cash-flow table.
- Download the table as CSV.
- Learn as you go: **"Show the maths, step by step"** plugs your numbers into each formula for any period and says in plain English who pays whom (Party A = fixed payer, Party B = floating payer). Every input has a tooltip, and "How a swap works" lists the symbols and formulas.
- A third chart panel shows the **cumulative net** settlement.
- A full-width layout: the controls on the left, the results on the right, and the step-by-step maths across the bottom. Every chart panel is labelled with its own colour key. Plus a **Party A ⇄ Party B diagram** of who pays whom, **click a chart period** to walk through its maths, and insight chips (break-even fixed rate, periods in your favour, largest settlement).

Everything recalculates as soon as you change a value. There is no "Run" button.

## Running it

Requirements: **Python 3.11+** (free). Nothing else to install beyond the two pip packages. Tested with Python 3.11 (CI) and 3.13 using Streamlit 1.67.

```bash
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py      # opens http://localhost:8501
pytest                    # run all tests (unit + integration)
pytest -m "not integration"   # fast loop: unit tests only
```

To stop the app, press `Ctrl+C` in the terminal. To use a different port: `streamlit run app.py --server.port 8502`. The theme lives in [.streamlit/config.toml](.streamlit/config.toml).

### Tests and CI
- **Unit tests** (`tests/unit/`) check each module on its own. Each module's owner writes them.
- **Integration tests** (`tests/integration/`) check that real modules work together: the finance pipeline from rates to CSV, and the full app run headlessly with Streamlit's built-in `AppTest`.
- **CI:** GitHub Actions ([.github/workflows/tests.yml](.github/workflows/tests.yml)) runs `pytest` on every pull request to `main`. A PR is merged only when the check is green and a teammate has approved it.

## Project structure

```
app.py                  # wires the page together (no business logic)
swap/                   # pure Python finance logic — no UI code
  models.py             # FROZEN shared data types
  engine.py             # cash-flow maths
  scenarios.py          # floating-rate path generator
  validation.py         # input checks
  export.py             # DataFrame / CSV
ui/                     # Streamlit render functions
  inputs.py  rates_editor.py  results.py  chart.py  explainer.py  formatting.py
.streamlit/config.toml  # theme
pyproject.toml          # pytest settings
.github/workflows/tests.yml   # CI: runs pytest on every PR
tests/
  unit/                 # one test file per module
  integration/          # modules working together + full-app AppTest
.10x/                   # design spec, ADRs, role decisions, status (planning memory)
```

## Team and workstreams

The work is split into 6 workstreams that run in parallel. Each member owns separate files and codes against frozen shared contracts, so nobody waits on anybody. Details, checklists and "done when" conditions are in [WORK_PLAN.md](WORK_PLAN.md).

| # | Workstream | Main files |
|---|---|---|
| M1 | Swap engine (finance core) + pipeline integration tests | `swap/engine.py`, `tests/integration/test_pipeline.py` |
| M2 | Rate scenarios + rate editor | `swap/scenarios.py`, `ui/rates_editor.py` |
| M3 | Inputs + validation | `ui/inputs.py`, `swap/validation.py` |
| M4 | Summary, table, CSV, formatting | `ui/results.py`, `ui/formatting.py`, `swap/export.py` |
| M5 | Charts | `ui/chart.py` |
| M6 | App shell, theme, explainer, CI, app integration tests | `app.py`, `.streamlit/config.toml`, `ui/explainer.py`, `.github/workflows/tests.yml`, `tests/integration/test_app.py` |

---

## Decision log

Every decision made during planning: the question, the options, what was chosen and why, and **exactly what to change if you want something different**. "Spec §N" refers to [the design spec](.10x/specs/2026-11-10-irs-simulator-design.md).

**How to change a decision:** agree it with the members listed under "Affected", update the files listed, then update this table (move the old choice to "Options considered" and note the date). For architectural changes, add a new ADR in `.10x/adrs/` that supersedes the old one. Do not edit an accepted ADR.

### Decisions made by the team (asked during planning)

| # | Question | Options considered | Chosen | Why | To change it, edit… | Affected |
|---|---|---|---|---|---|---|
| D1 | Which tech stack? | (a) Plain HTML/CSS/JS, no dependencies *(was recommended for zero setup)* · (b) **Python + Streamlit** · (c) React + Vite | **Python + Streamlit** | The team prefers Python, and Python suits finance. One `pip install` gives widgets, reactivity, tables, charts and downloads. | Spec §4, §5, §9 · [ADR-001](.10x/adrs/001-python-streamlit-local-app.md) (supersede it) · all `ui/` files and `app.py`. The `swap/` logic would need porting only if you leave Python. | M2–M6 (UI); M1 only if you leave Python |
| D2 | Where do the floating rates come from? | (a) **Scenario presets + per-period edit** · (b) manual entry only · (c) presets only | **Presets + edit** | Fast to demo (one click) and still interactive ("what if period 3 spikes?"). | Spec §7, §8 · `swap/scenarios.py`, `ui/rates_editor.py` | M2 |
| D3 | How much financial detail? | (a) **Plain vanilla** · (b) + day-count conventions and real dates · (c) + discounting / present value | **Plain vanilla** | Easy to explain and verify by hand. Shows the core mechanism (netting) without noise. | Spec §2, §3 · `swap/models.py` (**contract change**) · `swap/engine.py`, `swap/export.py` columns, table and chart | M1, M4, M5 (+ M3 for new inputs) |
| D4 | Which extra outputs? | Chart · Payer/receiver toggle · CSV download · Explainer panel | **All four** | Each one helps the user understand or reuse the result, and each is small. | Spec §2, §9 · remove or add the matching render call in `app.py` and the owner's file | M4 (CSV), M5 (chart), M3 (toggle), M6 (explainer) |
| D5 | What deliverables beyond code? | Written report · Presentation / demo · **Code only** | **Code only** | The repo holds only software. No report or slides workstreams are planned here. | Add workstreams to WORK_PLAN.md if this changes | All |
| D6 | Team's Python comfort? | Mixed · **All comfortable** · Mostly beginners | **All comfortable** | The work is split evenly by feature, not by difficulty. | Rebalance the WORK_PLAN.md workstreams | All |
| D8 | Should the app teach, not just calculate? *(added 2026-11-12, after the brief review)* | (a) keep the calculator as specced · (b) **add learning aids: step-by-step formula walkthrough, Party A/B wording, tooltips, cumulative-net chart, longer explainer** | **(b)** | The brief asks the demo to show *who pays whom and why* to someone new to swaps, and lists a cumulative-net chart. The walkthrough reads engine output only, so the maths stays in `swap/`. | Spec §2, §9.4–§9.6, §10 · `ui/walkthrough.py`, `ui/chart.py`, `ui/explainer.py`, `ui/inputs.py`, `ui/rates_editor.py`, `app.py` | M2, M3, M5, M6 |
| D9 | Should the UI be more engaging and interactive? *(added 2026-11-12)* | (a) keep the calm greyscale page · (b) **colour with a job (amber = fixed / Party A, teal = floating / Party B, green/red = your money, indigo = controls), cards and a tinted hero, one-click scenarios, flow diagram, chart → walkthrough click, insight chips** | **(b)** | Makes "who pays whom and why" visible and lets the demo jump straight to the brief's example. Still one column, one focal number, ≤ 3 icons, no new dependencies. | Spec §2, §5, §6.2, §9.3, §9.7 · `.streamlit/config.toml`, `ui/theme.py`, `ui/formatting.py`, `ui/results.py`, `ui/chart.py`, `ui/walkthrough.py`, `ui/flow_diagram.py`, `ui/quick_scenarios.py`, `ui/inputs.py`, `ui/rates_editor.py`, `app.py` | M2–M6 |
| D10 | Centred column or full width? *(added 2026-11-12)* | (a) centred ~730 px column · (b) **full width with one asymmetric 2 : 3 grid: a controls rail beside the results canvas** | **(b)**, and the D9 one-click scenarios are removed because the presets already do the same job. *UI review (same day): the rail is no longer sticky, so the page has one scroll only; the lede sits under the title; chart panels are directly labelled.* | Uses the screen and puts cause (inputs) beside effect (results). A self-scrolling rail clipped its bottom and trapped the scroll, so it was removed. | Spec §9.1 (superseded by §9.8) · `app.py`, `ui/theme.py`, `ui/inputs.py`, `ui/results.py`, `ui/walkthrough.py` | M3, M4, M6 |
| D7 | Should tests run automatically? *(added after the first plan)* | (a) local `pytest` by convention only · (b) **unit + integration tests, run by GitHub Actions on every PR** · (c) another CI service | **(b) GitHub Actions on every PR** | Six people merge into one `main`, and a broken `main` blocks everyone. GitHub Actions is free and needs no new account. | Spec §10, §12 · [ADR-003](.10x/adrs/003-ci-pytest-on-pull-requests.md) · `.github/workflows/tests.yml`, `pyproject.toml` · WORK_PLAN ground rule 7 + Git workflow | M6 (CI), M1 (pipeline tests), all (unit tests) |

### Requirements given up front (from the project brief)

| # | Requirement | What it means in the plan | To change it, edit… |
|---|---|---|---|
| R1 | KISS and YAGNI | Spec §2 has a strict in-scope list and an explicit out-of-scope list | Spec §2 |
| R2 | Local only, no deployment | No hosting, Docker or monitoring. `streamlit run app.py` is the only way to run it. *(Originally "no CI" as well. Superseded by D7: CI now runs tests only and never deploys.)* | Spec §11, `.10x/decisions/devops/` |
| R3 | Free technologies, minimal setup | Two pip packages only (`streamlit`, `pytest`). No accounts or API keys. | Spec §4, `requirements.txt` |
| R4 | 6 members working at the same time, independently | File ownership + frozen contracts + a walking skeleton ([ADR-002](.10x/adrs/002-frozen-contracts-for-parallel-work.md)) | WORK_PLAN.md, ADR-002 |
| R7 | Unit and integration tests, checked in CI when a PR is created *(added after the first plan)* | See D7, P17–P19 | Spec §10, §12, ADR-003 |
| R5 | Minimal, engaging, guiding UI | One centred column, one focal number, colour only with meaning, no Run button | Spec §9 |
| R6 | Never add AI as a commit co-author | Rule in AGENTS.md, CLAUDE.md and WORK_PLAN.md | Those three files |

### Decisions made by the planner (defaults; change freely via the process above)

| # | Decision | Alternatives | Why | To change it, edit… | Affected |
|---|---|---|---|---|---|
| P1 | Architecture: pure `swap/` package (no Streamlit) + thin `ui/` + `app.py` composition only | Everything in one `app.py` | Unit-testable maths, and lets 6 people work in separate files | Spec §5, ADR-001 | All |
| P2 | Frozen contracts in `swap/models.py` + a walking skeleton at kickoff | Each member defines their own types; build in sequence | Removes waiting between members | Spec §6, ADR-002, WORK_PLAN Kickoff | All |
| P3 | Sign convention: **+ = you receive, − = you pay**, always from the user's selected position | Always show from the payer's view | Matches how a user reads "my cash flow" | Spec §3 · `engine.py`, `formatting.py`, `results.py`, `chart.py` | M1, M4, M5 |
| P4 | Floating rate set at the start of the period and paid at the end | Compounded in arrears (SOFR-style) | Textbook vanilla convention, and the simplest | Spec §3 · `engine.py` | M1 |
| P5 | Accrual fraction = `1 / payments per year` (no day count) | 30/360, ACT/360, ACT/365 | Follows from D3 | Spec §3 · `models.py`, `engine.py` | M1 |
| P6 | Rates stored as decimals in code; percent only in the UI | Percent everywhere | Avoids ×100 bugs in the maths | Spec §6.2 | All |
| P7 | Python `float` and round only for display | `decimal.Decimal` | Simpler. Errors are far below 1 cent at these sizes. | `engine.py`, `export.py`, `formatting.py` | M1, M4 |
| P8 | Notional is not exchanged; no floating spread; constant notional | Spread input; amortising notional | YAGNI | Spec §2, §3 · `models.py` (contract change) | M1, M3 |
| P9 | Rate presets: Flat / Rising / Falling / Volatile, step 0.25%, seed 42, floor 0% | More presets; historical data | Covers every story worth telling in a demo | Spec §7 · `scenarios.py` | M2 |
| P10 | Input limits: notional 1k–1T, fixed 0–30%, tenor 1–30 yrs, freq 1/2/4, edited rates −5% to 30% | Other limits | Realistic, and prevents absurd output | Spec §8 · `inputs.py`, `validation.py` | M3 |
| P11 | Defaults: 1,000,000 · 4.00% · 5 yrs · semi-annual · Pay fixed · Rising from 3.50% | — | The first screen already tells a story (floating crosses above fixed) | Spec §8 | M2, M3 |
| P12 | Charts with Altair (installed with Streamlit) | `st.bar_chart`, Plotly, matplotlib | Conditional colours and stacked charts with no extra install | Spec §9.4 · `chart.py` | M5 |
| P13 | Tests: pytest + Streamlit's built-in `AppTest`; split into `tests/unit/` and `tests/integration/` (marker `integration`) | unittest; Selenium/Playwright for integration | Simple asserts, and a headless app test with no browser or extra dependency | Spec §10 | All |
| P17 | CI details: one job, Ubuntu, Python 3.11 only, `pytest -q`, read-only permissions, triggered on PR and push to `main` | Python version matrix; lint job; caching beyond pip | Fast, free and enough. 3.11 is the lowest supported version. | Spec §12 · `.github/workflows/tests.yml` | M6 |
| P18 | Integration tests that need unmerged code are `xfail(strict=False)` until integration day | Write integration tests only at the end | Tests exist early and CI stays green during parallel work | Spec §10.2 · WORK_PLAN Integration day | M1, M6 |
| P19 | Merge gate: green CI + 1 approval, enforced with branch protection on `main` | No gate | Keeps `main` runnable for all six members | Spec §12 · GitHub repo settings | Repo owner |
| P14 | UI: centred layout, no Run button, colour roles from D9 (green/red only for your money, grey for zero), ≤ 3 icons, no dividers, help tooltips on every input (D8) | Sidebar inputs; dashboard grid | Guides the eye from terms to rates to the answer to the reason, without distraction | Spec §9 · `.streamlit/config.toml`, `ui/` | M2–M6 |
| P15 | Currency shown as `$` | Currency selector; no symbol | Simple and recognisable | `ui/formatting.py` | M4 |
| P16 | Git: one branch per member, PR + one reviewer, `main` always runnable | Trunk-based with no reviews | Light process, but catches spec mismatches | WORK_PLAN.md | All |

---

## Where everything is documented

| Document | Purpose |
|---|---|
| [WORK_PLAN.md](WORK_PLAN.md) | Who builds what, file ownership, checklists, git workflow, integration day |
| [.10x/specs/2026-11-10-irs-simulator-design.md](.10x/specs/2026-11-10-irs-simulator-design.md) | Full design: formulas, contracts, UI rules, test strategy |
| [.10x/adrs/](.10x/adrs/) | Architecture Decision Records (why the structure is the way it is) |
| [.10x/decisions/](.10x/decisions/) | Per-role notes (CTO, PM, architect, QA, …) |
| [.10x/status.md](.10x/status.md) | Current phase and progress |
| [AGENTS.md](AGENTS.md) / [CLAUDE.md](CLAUDE.md) | Rules for AI coding assistants used by team members |
