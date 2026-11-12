# Interest-Rate Swap Cash-Flow Simulator — Design Spec

**Date:** 2026-11-10
**Feature slug:** `irs-simulator`
**Status:** Approved for planning. Not yet built.
**Related:** [WORK_PLAN.md](../../WORK_PLAN.md) · [ADR-001](../adrs/001-python-streamlit-local-app.md) · [ADR-002](../adrs/002-frozen-contracts-for-parallel-work.md) · [ADR-003](../adrs/003-ci-pytest-on-pull-requests.md)

---

## 1. Goal

A small local app that shows how a **plain-vanilla interest-rate swap (IRS)** works. The user enters swap terms and a floating-rate path. The app shows, for each period:

- the fixed-leg payment
- the floating-leg payment
- the **net settlement** (the only cash that actually changes hands)

It also shows totals, a chart, and a CSV export.

**Primary user goal (≤ 30 seconds):** "If I pay fixed and receive floating on this notional, how much do I pay or receive each period, and overall?"

## 2. Scope

### In scope (MVP — nothing else)
1. Swap terms: notional, fixed rate, tenor (years), payment frequency (annual / semi-annual / quarterly).
2. Position toggle: **Pay fixed** (payer swap) or **Receive fixed** (receiver swap).
3. Floating-rate path from a preset (Flat, Rising, Falling, Volatile) plus a start rate. Any single period's rate can then be edited.
4. Per-period cash-flow table: period, time, floating rate, fixed payment, floating payment, net settlement, cumulative net.
5. Summary: total net settlement (headline), total fixed, total floating, and a one-line plain-English verdict.
6. Charts: rate path (floating vs fixed, tooltip shows both payments) stacked above net settlement bars (green = receive, red = pay, grey = zero) and a cumulative-net line. *(Cumulative panel added 2026-11-12, D8.)*
7. CSV download of the cash-flow table.
8. Collapsible "How a swap works" explainer with symbols, formulas and who-pays-whom (Party A = fixed payer, Party B = floating payer).
9. **Learning aids** *(added 2026-11-12, D8)*: a "Show the maths, step by step" walkthrough that plugs the user's numbers into the §3 formulas for any chosen period, and a `help=` tooltip on every input (§9.6).

### Explicitly out of scope (YAGNI)
Day-count conventions, business-day calendars and real dates, discounting / PV / mark-to-market, amortising notionals, floating spreads, compounding (SOFR in arrears), multiple currencies, saving or loading scenarios, user accounts, databases, deployment. (CI *is* in scope, but only to run tests on PRs. See §12.)

## 3. Financial model (plain vanilla)

| Symbol | Meaning | Unit |
|---|---|---|
| `N` | Notional | currency |
| `K` | Fixed rate (annual) | decimal (0.04 = 4%) |
| `f` | Payments per year | 1, 2 or 4 |
| `T` | Tenor | whole years |
| `n = T·f` | Number of periods | — |
| `α = 1/f` | Accrual fraction per period | years |
| `Lᵢ` | Floating rate for period *i*. It is set at the start of the period and paid at the end. | decimal |

For each period `i = 1..n`:

```
fixed_paymentᵢ    = N · K  · α
floating_paymentᵢ = N · Lᵢ · α
net_payerᵢ        = floating_paymentᵢ − fixed_paymentᵢ   # pay-fixed view
net_settlementᵢ   = net_payerᵢ        if position = PAY_FIXED
                  = −net_payerᵢ       if position = RECEIVE_FIXED
cumulative_netᵢ   = Σ_{j≤i} net_settlementⱼ
time_yearsᵢ       = i · α
```

**Sign convention (used everywhere — engine, table, chart, copy):** a positive net settlement means **you receive** money. A negative one means **you pay**. The notional is never exchanged.

**Worked example (the canonical test case. Every module uses it):**

`N = 1,000,000`, `K = 4%`, `T = 2`, `f = 2` (semi-annual), position = Pay fixed, floating = `[3.5%, 4.0%, 4.5%, 5.0%]`, `α = 0.5`

| Period | Time | Float | Fixed pmt | Float pmt | Net | Cumulative |
|---|---|---|---|---|---|---|
| 1 | 0.5 | 3.50% | 20,000 | 17,500 | −2,500 | −2,500 |
| 2 | 1.0 | 4.00% | 20,000 | 20,000 | 0 | −2,500 |
| 3 | 1.5 | 4.50% | 20,000 | 22,500 | +2,500 | 0 |
| 4 | 2.0 | 5.00% | 20,000 | 25,000 | +5,000 | +5,000 |

Totals: fixed 80,000 · floating 85,000 · net **+5,000** · average float 4.25% · periods receiving 2 · paying 1 (a zero net counts as neither).

With Receive fixed, every net and cumulative value flips sign (total −5,000). The fixed and floating payment amounts do not change.

## 4. Tech stack

| Concern | Choice | Why |
|---|---|---|
| Language | Python ≥ 3.11 | The team knows it, and it suits finance work |
| UI | Streamlit (`streamlit>=1.40,<2`) | One dependency gives widgets, reactivity, a table editor, charts and downloads |
| Charts | Altair (installed with Streamlit) | Conditional colours and layered charts with no extra install |
| Tables / CSV | pandas (installed with Streamlit) | `DataFrame.to_csv` |
| Tests | pytest (`pytest>=8`) plus Streamlit's built-in `streamlit.testing.v1.AppTest` | Plain `assert` tests and a headless app smoke test |
| Randomness | stdlib `random.Random(seed)` | Rate paths you can reproduce |
| CI | GitHub Actions (free), one job that runs `pytest` on every PR to `main` | No extra accounts, since the repo is already on GitHub. See §12. |

`requirements.txt` holds exactly two lines: `streamlit` and `pytest`. **No other dependencies** without a team decision (see the WORK_PLAN change process).

Run: `python -m venv .venv` → activate → `pip install -r requirements.txt` → `streamlit run app.py`. Tests: `pytest`.

## 5. Architecture

A single-process Streamlit app. The **pure-Python domain** (`swap/`) has no Streamlit imports. The **UI** (`ui/`) has thin render functions. `app.py` only wires them together.

```
app.py                  # composition only — page config, call order, validation gate
swap/                   # pure Python, no streamlit import, fully unit-tested
  models.py             # FROZEN contracts (dataclasses + enums) — §6
  engine.py             # simulate_swap, summarize
  scenarios.py          # generate_rates
  validation.py         # validate_inputs, validate_rates
  export.py             # cash_flows_to_dataframe, to_csv_bytes
ui/                     # streamlit render functions, one concern per file
  inputs.py             # render_swap_inputs
  rates_editor.py       # render_rate_editor
  results.py            # render_summary, render_cash_flow_table
  chart.py              # build_settlement_chart, render_settlement_chart
  explainer.py          # render_explainer
  walkthrough.py        # render_walkthrough, build_steps, settlement_sentence (§9.6)
  formatting.py         # fmt_money, fmt_rate, fmt_signed_money (shared helpers)
.streamlit/config.toml  # theme tokens
pyproject.toml          # pytest config only (testpaths, markers) — no packaging
.github/workflows/tests.yml  # CI: pytest on every PR (§12)
tests/
  unit/                 # one test file per module, owned by that module's owner
  integration/          # cross-module tests (§10.2)
```

**Data flow (each rerun, top to bottom):**

```
render_swap_inputs() ─► SwapInputs ─┐
                                    ├─► validate_inputs + validate_rates ─► (errors? show + st.stop)
render_rate_editor(n) ─► rates ─────┘
                                    ▼
                     simulate_swap(inputs, rates) ─► list[PeriodCashFlow]
                                    ▼
                         summarize(cash_flows) ─► SwapSummary
                                    ▼
   render_summary ─► render_settlement_chart ─► render_walkthrough ─► render_cash_flow_table (+CSV) ─► render_explainer
```

**Error handling:** widgets prevent most bad input (min/max on number inputs, fixed option lists). `validate_*` is the single guard before the engine runs. The engine raises `ValueError` only on programmer errors, such as a rate-list length mismatch. The UI shows validation messages with `st.warning` and calls `st.stop()`, so nothing below renders with bad data.

## 6. Frozen contracts (the only shared code)

These signatures are **frozen**. Every member codes against them. Changing one requires the contract-change process in WORK_PLAN.md.

### 6.1 `swap/models.py` (complete file — commit verbatim at kickoff)

```python
"""Shared data contracts. FROZEN — change only via the WORK_PLAN contract-change process."""
from dataclasses import dataclass
from enum import Enum


class Position(str, Enum):
    PAY_FIXED = "pay_fixed"          # payer swap: pay fixed, receive floating
    RECEIVE_FIXED = "receive_fixed"  # receiver swap: receive fixed, pay floating


class RatePreset(str, Enum):
    FLAT = "flat"
    RISING = "rising"
    FALLING = "falling"
    VOLATILE = "volatile"


@dataclass(frozen=True)
class SwapInputs:
    notional: float           # e.g. 1_000_000
    fixed_rate: float         # decimal, 0.04 == 4%
    tenor_years: int          # 1..30
    payments_per_year: int    # 1, 2 or 4
    position: Position

    @property
    def num_periods(self) -> int:
        return self.tenor_years * self.payments_per_year

    @property
    def accrual_fraction(self) -> float:
        return 1 / self.payments_per_year


@dataclass(frozen=True)
class PeriodCashFlow:
    period: int               # 1-based
    time_years: float         # period * accrual_fraction
    floating_rate: float      # decimal
    fixed_payment: float      # N * K * alpha
    floating_payment: float   # N * L * alpha
    net_settlement: float     # user's view: + receive, - pay
    cumulative_net: float


@dataclass(frozen=True)
class SwapSummary:
    total_fixed: float
    total_floating: float
    total_net: float          # user's view: + receive, - pay
    average_floating_rate: float
    periods_receiving: int    # net > 0
    periods_paying: int       # net < 0
```

### 6.2 Function signatures

All rates are **decimals** inside the code. Only the UI converts to and from percent.

| Module | Signature | Contract |
|---|---|---|
| `swap/engine.py` | `simulate_swap(inputs: SwapInputs, floating_rates: list[float]) -> list[PeriodCashFlow]` | Raises `ValueError` if `len(floating_rates) != inputs.num_periods`. Follows the §3 formulas exactly. No rounding. |
| `swap/engine.py` | `summarize(cash_flows: list[PeriodCashFlow]) -> SwapSummary` | An empty list gives all zeros. |
| `swap/scenarios.py` | `generate_rates(preset: RatePreset, num_periods: int, start_rate: float, step: float = 0.0025, seed: int = 42) -> list[float]` | See §7. Deterministic for the same arguments. Returns `num_periods` values. |
| `swap/validation.py` | `validate_inputs(inputs: SwapInputs) -> list[str]` | Returns human-readable error messages. An empty list means valid. Uses the limits in §8. |
| `swap/validation.py` | `validate_rates(rates: list[float], expected_len: int) -> list[str]` | Checks the length and that each rate is in range. A message names the period, e.g. "Period 3 rate must be between −5% and 30%." |
| `swap/export.py` | `cash_flows_to_dataframe(cash_flows: list[PeriodCashFlow]) -> pd.DataFrame` | Columns in this order: `Period, Time (yrs), Floating rate (%), Fixed payment, Floating payment, Net settlement, Cumulative net`. Rates ×100. Money is unrounded floats. |
| `swap/export.py` | `to_csv_bytes(df: pd.DataFrame) -> bytes` | UTF-8, no index, money rounded to 2 dp. |
| `ui/formatting.py` | `fmt_money(x: float) -> str` → `"$1,234,568"`; `fmt_signed_money(x) -> str` → `"+$5,000"` / `"−$2,500"` / `"$0"`; `fmt_rate(r: float) -> str` → `"4.25%"` | Pure functions, unit-tested. |
| `ui/inputs.py` | `render_swap_inputs() -> SwapInputs` | Renders the terms and the position control. |
| `ui/rates_editor.py` | `render_rate_editor(num_periods: int) -> list[float]` | Renders the preset, start rate and editable table. Returns decimals. |
| `ui/results.py` | `render_summary(summary: SwapSummary, inputs: SwapInputs) -> None` | Shows the headline metric, two secondary metrics and the verdict. |
| `ui/results.py` | `render_cash_flow_table(cash_flows: list[PeriodCashFlow]) -> None` | Shows the formatted table and the CSV download button. |
| `ui/chart.py` | `build_settlement_chart(cash_flows: list[PeriodCashFlow], fixed_rate: float) -> alt.Chart` | Pure builder, testable without Streamlit. |
| `ui/chart.py` | `render_settlement_chart(cash_flows, fixed_rate) -> None` | Calls `st.altair_chart` at full container width (use whichever width argument the installed Streamlit version documents). |
| `ui/explainer.py` | `render_explainer() -> None` | One collapsed expander. |
| `ui/walkthrough.py` | `render_walkthrough(cash_flows: list[PeriodCashFlow], inputs: SwapInputs) -> None`; pure helpers `build_steps(flow, inputs) -> list[Step]`, `settlement_sentence(flow, inputs) -> str` | Reads engine output only; never recalculates. Added 2026-11-12 (D8); not part of the original frozen set. |

## 7. Rate scenarios

The start rate is `r₀`. Index `i = 0..n−1`. Generated values are floored at `0.0` and rounded to 6 dp.

| Preset | Rule |
|---|---|
| Flat | `rᵢ = r₀` |
| Rising | `rᵢ = r₀ + step·i` |
| Falling | `rᵢ = max(0, r₀ − step·i)` |
| Volatile | `r₀`, then `rᵢ = max(0, rᵢ₋₁ + gauss(0, step))` using `random.Random(seed)` |

The editor lets the user override any period, including negative rates down to −5%. Edits persist until the preset, the start rate or the number of periods changes. Then the table regenerates. To do this, key the `st.data_editor` on `f"rates-{preset}-{start_rate}-{num_periods}"`.

## 8. Input limits

| Field | Widget | Default | Range / options |
|---|---|---|---|
| Notional | `st.number_input`, step 100,000 | 1,000,000 | 1,000 – 1,000,000,000,000 |
| Fixed rate (%) | `st.number_input`, step 0.05 | 4.00 | 0 – 30 |
| Tenor (years) | `st.number_input` (int) | 5 | 1 – 30 |
| Frequency | `st.segmented_control` | Semi-annual | Annual(1) / Semi-annual(2) / Quarterly(4) |
| Position | `st.segmented_control` | Pay fixed | Pay fixed / Receive fixed |
| Preset | `st.segmented_control` | Rising | Flat / Rising / Falling / Volatile |
| Start rate (%) | `st.number_input`, step 0.05 | 3.50 | 0 – 30 |
| Per-period rate (%) | `st.data_editor` cell | from preset | −5 – 30 |

The maximum number of periods is 30 × 4 = 120.

## 9. UI / UX design

**Principle:** one screen, one job. The eye moves top to bottom: *terms → rates → answer → why*. The app recalculates on every change, so there is **no Run button**.

### 9.1 Layout (`st.set_page_config(layout="centered")`, ~730 px column = natural negative space)

```
 Interest-Rate Swap Simulator                      ← st.title (only H1)
 See what you pay or receive each period.          ← st.caption (muted)

 [ Notional      ] [ Fixed rate % ]                ← 2 columns
 [ Tenor (yrs)   ] [ Annual | Semi | Quarterly ]
 Position  ( Pay fixed | Receive fixed )

 Floating rates                                     ← st.subheader (H3 weight)
 ( Flat | Rising | Falling | Volatile )  [Start %]
 ▸ Edit individual periods                          ← collapsed expander → data_editor

 ───────── whitespace, no divider line ─────────

 You receive                                        ← muted label
 +$12,340                                          ← HERO: largest text, green/red
 over 5 years · floating averaged 4.6% vs 4.00% fixed   ← verdict, muted
 Fixed leg  $200,000      Floating leg  $212,340   ← two small st.metric

 [ rate path chart  — floating line vs dashed fixed ]
 [ net settlement bars — green up / red down       ]

 ▸ Cash-flow table                                  ← expander, open by default
     table …                       [⬇ Download CSV]

 ▸ How a swap works                                 ← collapsed, bottom
```

### 9.2 Visual hierarchy rules
- **One focal point:** the headline net settlement is the largest, boldest element and the only large coloured text on the page.
- **Colour has meaning or is absent:** green and red are used *only* for receive and pay values. The accent blue is used *only* for interactive controls and the floating-rate line. Everything else is greyscale.
- **Never colour alone:** every coloured value also carries a sign (+/−) and a word ("You receive" / "You pay").
- **Whitespace over lines:** separate sections with spacing. Use no `st.divider` and no boxes or borders except Streamlit defaults.
- **Text sizes:** title → subheader → body → caption. No more than 4 sizes. Labels are sentence case.
- **Icons:** at most 3 on the whole page, and functional only: `:material/download:` (CSV), `:material/school:` (explainer), `:material/edit:` (edit periods). No emoji.
- **Numbers:** headline amounts have 0 dp. Table money has 2 dp with thousands separators. Rates have 2 dp with `%`. Numbers are right-aligned in the table.
- **Motion:** none beyond Streamlit's default. Interactivity comes from instant recalculation.

### 9.3 Theme tokens (`.streamlit/config.toml`)

```toml
[theme]
base = "light"
primaryColor = "#2F5BEA"              # accent: controls, floating line
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F6F7F9"  # inputs, expanders
textColor = "#1F2328"
font = "sans serif"

[client]
toolbarMode = "minimal"
```

Colours used in code (keep them in `ui/formatting.py` as constants): `POSITIVE = "#1A7F37"`, `NEGATIVE = "#CF222E"`, `MUTED = "#656D76"`, `FIXED_LINE = "#8C959F"`, `ACCENT = "#2F5BEA"`.

### 9.4 Chart spec (Altair, `vconcat`, shared x = Period)
- **Top (height ~140):** floating rate as a solid `ACCENT` line with points. Fixed rate as a dashed `FIXED_LINE` horizontal rule. Y axis in %. No gridlines except light horizontal ones.
- **Top tooltip:** Period, floating and fixed rate, floating and fixed payment. This is the fixed-vs-floating payment comparison: payments are `N × rate × α`, so they scale with the lines.
- **Middle (height ~220):** net settlement bars, coloured `POSITIVE` if > 0, `NEGATIVE` if < 0 and `MUTED` if 0. A zero baseline rule. Tooltip shows Period, Floating rate, Net settlement.
- **Bottom (height ~140, added 2026-11-12):** cumulative net as a `TEXT`-coloured (greyscale) line with points and a zero rule.
- A one-line `st.caption` above the chart explains how to read the three panels.
- No chart titles inside the chart (the page already gives context). Small axis labels in `MUTED`. Legends are hidden because the colours are explained by the hero and the sign.

### 9.5 Copy
- Verdict template: `"over {T} years · floating averaged {avg} vs {K} fixed"`.
- Hero label: `"You receive"` if total > 0, `"You pay"` if < 0, `"You break even"` if 0.
- Explainer: ≤ 200 words *(was 120; raised 2026-11-12, D8)* covering a symbol table (N, K, Lᵢ, α), the two payment formulas, who pays whom in Party A / Party B terms, what an IRS is, why firms use one (hedging, matching assets to liabilities), that only the net amount is exchanged, and what pay-fixed vs receive-fixed means. Use the §3 worked example as the illustration.

### 9.6 Learning aids (added 2026-11-12, D8)
- **Walkthrough:** `render_walkthrough` sits between the chart and the table in an expander "Show the maths, step by step" (open by default, no icon, so the 3-icon cap holds). A `st.select_slider` picks the period (hidden for a 1-period swap). Five steps, each a bold title + one plain sentence + `st.latex`: (1) `α = 1/f`, (2) `P_fixed = N × K × α`, (3) `P_float = N × Lᵢ × α`, (4) net in the user's view, (5) cumulative total, all with the user's numbers substituted.
- **Who pays whom:** below the steps, one sentence in Party A (fixed payer) / Party B (floating payer) terms, e.g. "Floating (6.50%) is below fixed (8.00%), so Party A pays Party B $37,500.00. You are Party B, so you receive +$37,500." A left border in `POSITIVE`/`NEGATIVE`/`MUTED` matches the sign (never colour alone). A muted rule-of-thumb caption follows.
- **Tooltips:** every swap-term input, the preset, the start rate and the editable rate column carry a short `help=` naming its symbol (N, K, T, f) where one exists. The Position help maps Pay fixed → Party A and Receive fixed → Party B.
- **Settlement direction:** some course material says "P_fixed − P_floating > 0 means Party B pays Party A". That is reversed: if the fixed leg is larger, the fixed payer (A) owes the difference. The app follows §3.

## 10. Testing strategy

There are two layers, both run by plain `pytest` locally and in CI (§12). Integration tests carry the `@pytest.mark.integration` marker, so `pytest -m "not integration"` runs only the fast unit tests while developing.

### 10.1 Unit tests (`tests/unit/`): one module in isolation, owned by that module's owner

| File | Owner | Must cover |
|---|---|---|
| `test_engine.py` | M1 | The §3 worked example (both positions), length mismatch → `ValueError`, zero and negative rates, the quarterly 30-year path (120 periods), `summarize` on an empty list |
| `test_scenarios.py` | M2 | Each preset's shape, length, determinism (same seed gives the same path), floor at 0, `num_periods=1` |
| `test_validation.py` | M3 | Each limit at boundary, just inside and just outside. The message names the period. Defaults are valid. |
| `test_export.py`, `test_formatting.py` | M4 | Column order, rates ×100, CSV round-trip, rounding, sign formatting including the zero case |
| `test_chart.py` | M5 | `build_settlement_chart(...).to_dict()` has 3 sub-charts, the colour condition (grey for zero), payment tooltips and the cumulative panel. Empty input and 120 periods do not crash. |
| `test_walkthrough.py` | M6 | Formulas show the user's numbers (brief sample), receive-fixed net formula, who-pays-whom sentence for both positions and zero, period picker and the 1-period case. |

### 10.2 Integration tests (`tests/integration/`): several real modules working together

| File | Owner | Must cover |
|---|---|---|
| `test_smoke.py` | M6 (kickoff) | Every module imports. `AppTest.from_file("app.py").run()` raises no exception. **Passes from day 1 against the skeleton**, so CI is green before anyone starts. |
| `test_pipeline.py` | M1 | The domain chain without UI: `generate_rates` → `validate_inputs`/`validate_rates` → `simulate_swap` → `summarize` → `cash_flows_to_dataframe` → `to_csv_bytes`. Checks: the worked example end to end, where the CSV's last cumulative value equals `summary.total_net` (5,000); every preset × every frequency gives consistent totals (Σ net == total_net == last cumulative); the position flip negates totals; invalid rates are caught by validation before the engine runs. |
| `test_app.py` | M6 | The full UI via `AppTest`: defaults render a hero with "You receive"/"You pay"; switching Position flips the hero sign; an invalid edited rate shows a warning and stops rendering (no chart or table); the download button is present. |

**Before integration day:** the assertions in `test_pipeline.py` and `test_app.py` depend on other members' real code, so mark them `@pytest.mark.xfail(reason="awaiting M<n>", strict=False)`. They then run in CI without blocking anyone. On integration day the owners remove every `xfail`, and from then on they must pass.

**Definition of done for every module:** the unit tests pass, CI is green on the PR, the module uses only the contract types, and there is no Streamlit import in `swap/`.

## 11. Security & ops (scaled to a local demo)
- Local only. No network calls, secrets, user data or persistence.
- The only untrusted input is form values and the CSV export. Validation bounds stop absurd values, and the export is generated by us, not parsed from users.
- No deployment or monitoring (out of scope by request). CI only runs tests (§12). It has no secrets and no deploy step.

## 12. Continuous integration

GitHub Actions runs the whole test suite on every pull request to `main` and on every push to `main`. It is free for public repos, and private repos get free monthly minutes. M6 commits this file **verbatim** in the kickoff skeleton:

```yaml
# .github/workflows/tests.yml
name: tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"   # lowest supported version
          cache: pip
      - run: pip install -r requirements.txt
      - run: pytest -q
```

And `pyproject.toml` (pytest config only):

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
markers = ["integration: cross-module tests (tests/integration/)"]
```

**Merge rule:** a PR is merged only when the `tests / pytest` check is green and one teammate has approved. The repo owner enables this once in GitHub → Settings → Branches (or Rules) → protect `main` → "Require status checks to pass" (select `pytest`) and "Require a pull request before merging". If the repo is private on a free plan and branch protection is unavailable, the team follows the same rule by hand: no merging on red.
