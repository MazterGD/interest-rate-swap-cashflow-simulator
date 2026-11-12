# SDE — irs-simulator
When a PR merges, its author appends a short section:
`## M<n> — <workstream>`: what was built · deviations from the spec · known tech debt.

## M6 — Kickoff skeleton (Step 0), on `main`
- **Built:**
  - `requirements.txt`, `pyproject.toml` and `.github/workflows/tests.yml` (verbatim from spec §12)
  - `swap/models.py` (verbatim from spec §6.1)
  - every spec §6.2 function with its final signature, a docstring stating the contract, and a placeholder body marked `TODO(M<n>)`
  - a fully wired `app.py`, including the validation gate
  - `tests/integration/test_smoke.py` (module imports + an AppTest run)
- **Verified:** `pytest` gives 12 passed (Python 3.13, Streamlit 1.67, pandas 3.1, Altair 6.3). `streamlit run app.py` serves, and the health check returns 200.
- **Deviations:**
  - `ui/formatting.py` already contains the final colour constants (not placeholders), so M5 can import them now.
  - `ui/chart.py`'s `render_settlement_chart` is already final: `st.altair_chart(..., width="stretch")`, the width argument in Streamlit 1.67.
  - `tests/unit/` exists, but empty (`.gitkeep`).
- **Notes for members:** `pytest -m "not integration"` exits with code 5 ("no tests collected") until the first unit tests land. That is expected. CI runs the full `pytest`, which passes.
- **Tech debt:** none. Every placeholder is replaced by its owner.

## M6 — App shell, theme, explainer, app tests (`m6-shell`)
- **Built:**
  - `.streamlit/config.toml` (spec §9.3 tokens, verified loaded with no warnings)
  - `ui/explainer.py` (collapsed `:material/school:` expander, ~105 words, uses the §3 worked example; text in `EXPLAINER_TEXT`)
  - `tests/unit/test_explainer.py`
  - `tests/integration/test_app.py`
  - README Running section confirmed
  - `app.py` was already final from the kickoff.
- **App tests:**
  - `test_page_shell_renders` passes now.
  - Four tests are `xfail(strict=False)` until integration day: hero verdict (M1+M4), position flip (M1+M3+M4), validation gate (M3), CSV button (M4).
  - All four were checked to **pass** against throwaway stand-in implementations of M1/M3/M4 (not committed).
  - The validation-gate test monkeypatches `ui.rates_editor.render_rate_editor` to return 40% rates, so it does not depend on driving `st.data_editor`.
- **Deviations:** added `tests/unit/test_explainer.py` (not in the original plan; it is now in M6's WORK_PLAN file list). WORK_PLAN M3 now pins the Position control interface (`key="position"`, `Position` enum members as options), which `test_app.py` relies on.
- **Remaining for M6:** remove the `xfail` marks on integration day.

## M1 — Swap engine + pipeline tests
- **Built:** Implemented the frozen `simulate_swap` and `summarize` contracts, including position-aware net settlements, cumulative totals, mismatch errors, zero/negative rates, and empty summaries. Added canonical worked-example, edge-case, and cross-module pipeline tests.
- **Verified:** Edited modules and tests compile; direct checks pass for the worked example, negative rates, and 30-year quarterly input.
- **Deviations:** None.
- **Verified:** The complete suite passes with the M1 additions; remaining `xfail`/`xpass` results belong to the parallel integration workstreams.

## M3 — Inputs + validation (`M3-mok`, 2026-11-11)
- **Built:**
  - `ui/inputs.py`: the spec §8 inputs in a 2×2 grid plus Position, with the specified defaults, limits and steps, stable widget keys, and a Notional tooltip.
  - Position uses `Position` enum options and `key="position"`. Deselected frequency and position controls fall back to semi-annual and Pay fixed. Fixed-rate percentages are converted to decimals.
  - `swap/validation.py`: checks swap-term limits, whole-year tenor, allowed frequency and position, floating-rate count, and inclusive −5% to 30% floating-rate bounds. Rate errors identify the one-based period. NaN and infinite numeric values fail the range checks.
  - `tests/unit/test_validation.py`: 62 cases covering valid defaults, boundaries and values immediately inside/outside, invalid terms, non-finite values, rate counts, period-specific messages, 1/120 periods, and isolated input-widget interactions via AppTest.
- **Verified:**
  - Python 3.14.10, Streamlit 1.67.0: M3 tests **62 passed**; full `python -m pytest -q -rxX` **78 passed, 3 xfailed, 1 xpassed**.
  - The XPASS is M6's invalid-rate validation-gate test: it now succeeds with the real M3 validator. Its existing marker remains for M6 to remove on integration day. The three remaining expected failures depend on unfinished M1/M4 features.
  - A separate localhost Streamlit instance with the agent API verified default controls, changed terms (including 30-year quarterly and Receive fixed), and deselection without exceptions or new console warnings. The temporary instance was stopped afterwards.
- **Deviations:** retained the user's existing member branch `M3-mok`; isolated widget tests share M3's owned test file. No dependency or frozen-contract changes. Static type checking was not run: no checker is configured/installed and the project forbids new dependencies.
- **Remaining:** push/open the M3 PR when requested, obtain a green GitHub Actions run and teammate approval. Local verification does not certify remote CI or branch protection. Whole-app financial demo checks await the other members' implementations.
- **Tech debt:** none introduced.

## Brief review fixes + D8 learning aids (`patch-1`, 2026-11-12)
Cross-workstream edit, agreed by the team; each owner should review their file in the PR.
- **Fixed:**
  - M2 `ui/rates_editor.py`: clicking the selected preset again returned `None` and crashed on `preset.value`. It now falls back to Rising. Added the missing spec §9.1 "Floating rates" subheader and stable keys (`preset`, `start_rate`).
  - M5 `ui/chart.py`: a zero net bar was red. It is now `MUTED` (spec §9.2).
  - M1/M6: removed every `xfail` from `tests/integration/` (integration day step 1). No xfail or xpass remains.
- **Built (D8):**
  - `ui/walkthrough.py` (M6): "Show the maths, step by step". Pure `build_steps` / `settlement_sentence` plus a thin `render_walkthrough`. A period slider, five `st.latex` steps with the user's numbers, and a who-pays-whom sentence in Party A/B terms. Reads engine output only.
  - `ui/chart.py` (M5): a third panel for cumulative net; the rate tooltip shows fixed and floating payments; a one-line reading guide caption.
  - `ui/explainer.py` (M6): symbol table, formulas, Party A/B direction; cap raised to 200 words.
  - `ui/inputs.py` (M3) and `ui/rates_editor.py` (M2): `help=` on every input. `TEXT` colour token added to `ui/formatting.py` (M4).
- **Tests:** `tests/unit/test_walkthrough.py` (new), plus updates to test_chart, test_explainer, test_validation and test_scenarios. The integration tests gain the brief sample end to end (pipeline + AppTest), the walkthrough on the page, and preset deselect. `pytest`: **153 passed**.
- **Deviations:** spec §2/§9.4/§9.5/§10 updated and new §9.6 added; README D8; WORK_PLAN ownership and checklists updated. Position labels are unchanged ("Pay fixed"/"Receive fixed"); the Party mapping lives in help text and the walkthrough.
- **Not verified:** a live browser run (only AppTest), GitHub CI on the PR, and branch protection on `main` (`gh` is not authenticated).
- **Tech debt:** none.

## D9 interactive UI + visual refresh (`patch-1`, 2026-11-12)
Cross-workstream edit, agreed by the team (same terms as D8).
- **Built:**
  - `ui/theme.py` and `.streamlit/config.toml`: theme tokens and CSS that targets only the `st-key-*` and `irs-*` classes. `ui/formatting.py` gets the leg colours (FIXED amber, FLOATING teal) and tint tokens.
  - `ui/quick_scenarios.py`: four scenario buttons. `ui/rates_editor.py` gains `RATE_OVERRIDE_KEY` for the example's custom rates.
  - `ui/flow_diagram.py`: the Party A ⇄ B SVG. `ui/walkthrough.py` now shows the diagram and colours P_fixed and P_float.
  - `ui/results.py`: tinted hero card and `render_insights` chips; the table expander is renamed "Payment schedule" and collapsed.
  - `ui/chart.py`: `build_panels`; three separate fitted charts; shared tooltip band, hover tint, click → `walkthrough_period`.
  - `ui/inputs.py` and `ui/rates_editor.py`: defaults are seeded with `session_state.setdefault` instead of `value=`/`default=`, so scenarios can set widget keys without Streamlit's "default value + Session State" warning.
- **Verified:** `pytest` gives 167 passed. Headless Edge screenshots (desktop 900px and mobile 390px) of the default, assignment-example, rising and choppy scenarios. The impeccable detector found nothing.
- **Deviations:**
  - The chart renders as three charts, not one vconcat. A vconcat cannot fit its axes inside the column; `build_settlement_chart` still returns the vconcat for the §6.2 contract and tests.
  - Panel heights are 180/250/180 because fitted heights include the axes.
- **Known limits:** hover tints only the panel under the pointer (separate charts); the selected-period tint shows in all three. The diagram scrolls sideways on phones under 520px. Streamlit's file watcher did not hot-reload edited modules during testing; restart `streamlit run` after pulling.
- **Tech debt:** none.

## D10 full-width asymmetric layout (`patch-1`, 2026-11-12)
- **Removed:** `ui/quick_scenarios.py`, its tests and the rate-override plumbing in `ui/rates_editor.py`. The presets cover the same cases, and the brief's example is entered through "Edit individual periods". The `session_state.setdefault` default seeding stays.
- **Built:**
  - `app.py`: wide layout; one `GRID = [2, 3]` split for the header and the body; rail (inputs card, rates card, explainer) and canvas (results).
  - `ui/theme.py`: content capped at 1760 px with fluid gutters, a sticky rail ≥ 1024 px, the hero as an internal 1.5fr / 1fr grid, a fluid title and hero sizes, and the diagram capped at 780 px.
  - `ui/inputs.py`: rail-friendly stacking (Notional; Fixed rate | Tenor; Frequency; Position).
  - `ui/walkthrough.py`: full-width diagram, then the steps.
  - `ui/chart.py`: "Cash flows over time" subheader.
- **Verified:** `pytest` gives 163 passed (the 4 scenario tests were removed with the feature). Headless Edge screenshots at 1920, 1280 and 390 px: no clipping or overflow. The impeccable detector found nothing.
- **Known limits:** the sticky rail only shows in a live browser; full-page screenshots show the space below it as empty.
- **Follow-up (same day):**
  - The header uses its own 3 : 2 split, so the title stays on one line at full size (`nowrap` ≥ 1024 px); top padding is 1.25rem.
  - The payment schedule moved into the canvas; the walkthrough is now the last section at full page width, with the diagram (sticky) beside the formula steps.
  - Frequency stays on its own full-width rail row.
  - Verified at 1536 px (1920 at 125 % scaling), 1280 px and 390 px.

## UI review fixes (`patch-1`, 2026-11-12)
- **Found** (from the user's screenshots at 1536 × 730 CSS px, i.e. 1920 × 1080 at 125 %):
  1. The sticky rail had its own scrollbar (`max-height` + `overflow-y: auto`). It trapped the scroll, clipped its bottom and left empty space below it.
  2. The lede sat in a separate right-hand header column, aligned with nothing.
  3. A three-line paragraph explained the chart colours far from the marks; the shaded column was never explained.
  4. The notional showed as `1000000`.
  5. The diagram in "Show the maths" was also sticky.
- **Fixed:**
  - One page scroll: the sticky rules and inner scroll are removed, and the diagram note moved out of the scrolling box. `tests/unit/test_theme.py` guards against `position: sticky`/`fixed`, `overflow-y: auto` and `max-height` coming back.
  - The lede sits under the title on the same edge.
  - Each chart panel has a heading with its unit and an inline colour key, there is one hint line, and the rotated y-axis titles are gone.
  - The walkthrough's period is shaded from the first load.
  - The notional readout is grouped tightly with its field.
- **Streamlit gotcha:** markdown blocks get `margin-bottom: -1rem` (it cancels a closing `<p>`'s margin). An HTML block that ends in a `<div>` must add `margin-bottom: 1rem`, or the next element paints over it; this is what clipped the panel headings. Our `p.irs-*` rules use `.stApp p.irs-…` to outrank Streamlit's `.st-emotion-… p` margins.
- **Verified:**
  - Headless Edge at 1536 × 730 (first screen + full page), 1280 and 390 px. A DOM probe reports no inner vertical scroller except Streamlit's page scroller (`stMain`).
  - `pytest` gives 169 passed. The layout-scope detector found nothing.
- **Known limit:** the rail is shorter than the results column, so on long result pages the space under it is empty. This is deliberate; the alternative was the sticky rail, which was removed.
