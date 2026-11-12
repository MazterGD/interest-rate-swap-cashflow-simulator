# Work Plan — Interest-Rate Swap Cash-Flow Simulator

> **This is the team's source of truth for who builds what.** The design (formulas, contracts, UI rules, tests, CI) is in [.10x/specs/2026-11-10-irs-simulator-design.md](.10x/specs/2026-11-10-irs-simulator-design.md). Read the spec sections listed for your workstream before you start. The reasons behind each decision are in [README.md](README.md#decision-log).

## Ground rules

1. **KISS and YAGNI.** Build only what the spec lists. If it is not in spec §2 "In scope", it does not get built.
2. **Stay in your files.** Each file has exactly one owner (table below). Do not edit another member's file. Open an issue or message them instead.
3. **Code against the contracts, not against each other.** The types in `swap/models.py` and the signatures in spec §6 are **frozen**. Change them only through the contract-change process below.
4. **No new dependencies.** `requirements.txt` holds `streamlit` and `pytest` only. Altair and pandas come with Streamlit.
5. **Rates are decimals in code** (`0.04`). Only `ui/` converts to and from percent.
6. **Sign convention:** `+` = the user receives, `−` = the user pays. This applies everywhere.
7. **Tests ship with code.** Every PR includes the unit tests for what it adds, and **CI must be green** before merging (spec §10, §12).
8. **Commits:** small, imperative messages (`engine: add summarize`). **Never add an AI tool (Claude, Copilot, ChatGPT, etc.) as co-author.** No `Co-Authored-By:` trailers for AI.

## Kickoff (Step 0 — Member 6, about 45 minutes, before anyone branches)

Member 6 commits a **walking skeleton** to `main` so that every workstream can start in parallel, the app runs from minute one, and CI is green from the first commit:

- `requirements.txt` (`streamlit>=1.40,<2`, `pytest>=8`), `.gitignore` (already in the repo)
- `pyproject.toml` and `.github/workflows/tests.yml`, **copied verbatim** from spec §12
- `swap/models.py`, **copied verbatim** from spec §6.1
- Every other module in spec §5, with its §6.2 signature and a **placeholder body**:
  - `simulate_swap` → one `PeriodCashFlow` per rate, all money `0.0`
  - `summarize` → `SwapSummary` with all zeros
  - `generate_rates` → `[start_rate] * num_periods`
  - `validate_inputs` / `validate_rates` → `[]`
  - `cash_flows_to_dataframe` → empty `DataFrame` with the spec columns; `to_csv_bytes` → `df.to_csv(index=False).encode()`
  - `fmt_*` → `str(x)`
  - `render_*` → `st.write("<module name> — TODO")`, returning sensible defaults (`render_swap_inputs` returns the spec §8 defaults; `render_rate_editor` returns `[0.035] * num_periods`)
  - `build_settlement_chart` → `alt.Chart(pd.DataFrame()).mark_bar()`
- Empty `swap/__init__.py` and `ui/__init__.py`
- `app.py` wired in the spec §5 data-flow order
- `tests/integration/test_smoke.py` (spec §10.2), which passes against the skeleton
- After pushing: the repo owner turns on branch protection for `main` (spec §12, "Merge rule")

After that commit, each member branches from `main` and **replaces only their own placeholders**. Nobody waits for anybody.

## The six workstreams

| # | Workstream | Owns these files (and only these) | Read spec |
|---|---|---|---|
| **M1** | Swap engine (the finance core) + pipeline integration tests | `swap/engine.py`, `tests/unit/test_engine.py`, `tests/integration/test_pipeline.py` | §3, §6, §10 |
| **M2** | Rate scenarios + rate editor | `swap/scenarios.py`, `ui/rates_editor.py`, `tests/unit/test_scenarios.py` | §6, §7, §8, §10 |
| **M3** | Inputs + validation | `ui/inputs.py`, `swap/validation.py`, `tests/unit/test_validation.py` | §6, §8, §9.1, §10 |
| **M4** | Results: summary, table, CSV, formatting | `ui/results.py`, `ui/formatting.py`, `swap/export.py`, `tests/unit/test_export.py`, `tests/unit/test_formatting.py` | §6, §9.1–9.3, §9.5, §10 |
| **M5** | Charts | `ui/chart.py`, `tests/unit/test_chart.py` | §6, §9.2–9.4, §10 |
| **M6** | App shell, theme, explainer, CI, app integration tests | `app.py`, `.streamlit/config.toml`, `ui/explainer.py`, `ui/walkthrough.py`, `tests/unit/test_explainer.py`, `tests/unit/test_walkthrough.py`, `tests/integration/test_smoke.py`, `tests/integration/test_app.py`, `.github/workflows/tests.yml`, `pyproject.toml`, `requirements.txt`, `.gitignore`, `README.md` (Running section), kickoff skeleton | §5, §9, §10, §11, §12 |

`swap/models.py` has no single owner. It is frozen, and any change goes through the contract-change process.

---

### M1 — Swap engine + pipeline integration tests
**Goal:** a correct, unit-tested implementation of the spec §3 formulas, and proof that the domain modules fit together.
- [ ] `simulate_swap`: per-period fixed and floating payments, net in the user's view (flipped for `RECEIVE_FIXED`), cumulative net, `time_years`. Raise `ValueError` on a length mismatch. No rounding.
- [ ] `summarize`: totals, average floating rate, count of receiving and paying periods (zero counts as neither). An empty list gives all zeros.
- [ ] Unit tests (`tests/unit/test_engine.py`): the §3 worked example for **both** positions (use `pytest.approx`), mismatch error, zero and negative rates, 30-year quarterly (120 periods), empty `summarize`.
- [ ] Integration tests (`tests/integration/test_pipeline.py`): the domain chain in spec §10.2. Mark tests that depend on M2/M3/M4 code `xfail(strict=False)` until integration day.
- **Done when** every value in the §3 table is asserted, the pipeline tests are written, and CI is green.

### M2 — Rate scenarios + rate editor
**Goal:** the user picks a rate path in one click and can tweak any period.
- [ ] `generate_rates`: the four presets exactly as in spec §7 (floor 0, round to 6 dp, seeded `random.Random`).
- [ ] `render_rate_editor(num_periods)`: preset `st.segmented_control` (default Rising), start-rate `st.number_input` (default 3.50%), and a collapsed `:material/edit:` "Edit individual periods" expander containing an `st.data_editor` with columns Period (read-only) and Rate (%) (editable, −5 to 30, step 0.05). Key the editor as in spec §7 so that edits reset when the inputs change. Return decimals.
- [ ] Unit tests: each preset's shape and length, the same seed gives the same path, falling never goes below 0, `num_periods=1` works.
- **Done when** switching presets updates the rates instantly, an edited cell flows into the return value, and CI is green.

### M3 — Inputs + validation
**Goal:** swap terms entered in seconds, with bad values impossible or clearly explained.
- [ ] `render_swap_inputs()`: the spec §8 widgets, defaults and ranges, laid out as in the spec §9.1 mock-up (2×2 grid plus a Position row). Give every widget a stable `key=` so AppTest can find it. The Position control must be `st.segmented_control(..., key="position")`, with the **`Position` enum members as options** (show "Pay fixed" / "Receive fixed" through `format_func`), because `tests/integration/test_app.py` relies on this. Sentence-case labels, and every input gets a short `help=` (spec §9.6; was "only Notional" before D8). Convert percent to a decimal before building `SwapInputs`.
- [ ] `validate_inputs` and `validate_rates` using the spec §8 limits. Messages are plain English and name the period for rate errors.
- [ ] Unit tests: each limit at boundary, just inside and just outside; a valid default input gives `[]`; a wrong rate-list length is reported.
- **Done when** an invalid state gives one clear message, valid defaults give none, and CI is green.

### M4 — Results: summary, table, CSV, formatting
**Goal:** the answer is readable at a glance, and the details are one click away.
- [ ] `ui/formatting.py`: `fmt_money`, `fmt_signed_money` (use a real minus sign `−`), `fmt_rate`, and the colour constants from spec §9.3.
- [ ] `render_summary`: hero label ("You receive" / "You pay" / "You break even"), the hero amount in `POSITIVE`/`NEGATIVE` colour at the largest size on the page, the verdict caption (spec §9.5 template), and two small `st.metric`s (Fixed leg, Floating leg).
- [ ] `swap/export.py`: `cash_flows_to_dataframe` (exact column order) and `to_csv_bytes` (2 dp, no index).
- [ ] `render_cash_flow_table`: an expander (open by default) with `st.dataframe` (right-aligned numbers, net column coloured by sign, index hidden) and an `st.download_button` (`:material/download:`, file name `swap_cash_flows.csv`).
- [ ] Unit tests: formatting including the zero and negative cases, column order, rates ×100, CSV parses back with `pandas.read_csv`.
- **Done when** the hero matches the engine total, the CSV opens cleanly in Excel, and CI is green.

### M5 — Charts
**Goal:** one glance shows *why* money flows: floating above fixed means the payer receives.
- [ ] `build_settlement_chart`: Altair `vconcat` exactly as in spec §9.4 (rate lines on top, net bars below, shared x = Period, conditional green/red, zero rule, tooltips, no legend or title, muted axes).
- [ ] `render_settlement_chart`: a thin wrapper at full container width.
- [ ] Unit tests: `to_dict()` contains three sub-charts (rates, net, cumulative; D8) and a colour condition on net sign with grey for zero; empty input and 120 periods both build without error.
- **Done when** the chart for the worked example shows bars −2,500 / 0 / +2,500 / +5,000 with the correct colours, and CI is green.

### M6 — App shell, theme, explainer, CI, app integration tests
**Goal:** the pieces compose into one calm, guided page, and every PR is checked automatically.
- [ ] Kickoff skeleton, CI workflow, `pyproject.toml` and the smoke test (Step 0 above).
- [ ] `app.py`: `st.set_page_config(page_title="IRS Simulator", layout="centered")`, the title and caption, then the calls in spec §5 order, with the validation gate (`st.warning` per message, then `st.stop()`). No business logic in `app.py`.
- [ ] `.streamlit/config.toml`: theme tokens from spec §9.3.
- [ ] `render_explainer()`: a collapsed `:material/school:` "How a swap works" expander of ≤ 120 words using the §3 worked example.
- [ ] `tests/integration/test_app.py` (`AppTest`): the checks in spec §10.2, marked `xfail(strict=False)` until integration day.
- [ ] Update the **Running** section of `README.md`.
- **Done when** `streamlit run app.py` shows the full page with real modules, `pytest` is green locally and in CI, and `main` is protected.

---

## Git workflow

- `main` is always runnable and green. Branches: `m1-engine`, `m2-rates`, `m3-inputs`, `m4-results`, `m5-chart`, `m6-shell`.
- Run `pytest` locally before pushing (`pytest -m "not integration"` is the fast loop while developing).
- Open a PR to `main` when your module meets its "Done when" condition. **CI (`tests / pytest`) runs automatically on the PR.** Merge only when CI is green **and** one teammate has approved after checking the code against the spec section for that workstream. Never force-push to `main`.
- If CI fails, fix it on your branch. Never disable, skip or delete another member's test to make CI pass.
- Because file ownership does not overlap, merges should not conflict. If one does, you touched someone else's file, so revert that part.

## Contract-change process

If you believe a frozen signature or type in spec §6 must change:
1. Post the proposed change and the reason in the group chat.
2. You need agreement from **every member whose module uses it** (search for the name).
3. Update spec §6 **and** `swap/models.py` in one PR. Add an ADR in `.10x/adrs/` if the change alters the architecture.
4. Affected owners update their code and tests in their own branches.

To change a product decision (scope, stack, UI rule, CI), follow the README [decision log](README.md#decision-log): it says what to edit and who is affected.

## Integration day (after all six PRs merge)

1. M1 and M6 remove every `xfail` mark from `tests/integration/`, in one PR each. CI must be green, with no `xfail` or `xpass` remaining.
2. The whole team runs `streamlit run app.py` and walks through the demo check together:
   - The defaults load with no warnings, and the hero reads "You receive" or "You pay" with an amount.
   - Pay fixed ↔ Receive fixed flips the hero sign and the bar colours.
   - Enter the spec §3 worked example (1,000,000 · 4% · 2 yrs · semi-annual · edit the rates to 3.5/4/4.5/5) and the result is +$5,000.
   - Type a rate of 40% into the editor and a clear warning appears with nothing rendered below it.
   - The downloaded CSV opens in Excel with the correct columns.
   - *(D8)* Enter the assignment-brief sample (10,000,000 · 8% · 1 yr · quarterly · rates 6.5/7/9/8.5): Pay fixed shows −$25,000, Receive fixed +$25,000, and the walkthrough for period 1 reads "Party A pays Party B $37,500.00".
   - *(D8)* Click the selected preset again: nothing crashes.
3. Fix bugs in the owner's file only. Each fix comes with a test that would have caught it.

## Timeline (suggested)

| Day | What |
|---|---|
| 1 | Kickoff skeleton + CI (M6, first hour). Everyone reads the spec and builds their module with unit tests. |
| 2–3 | Finish modules and integration tests, open PRs, CI green, cross-review. |
| 4 | Integration day: remove `xfail`s and run the demo check. |
