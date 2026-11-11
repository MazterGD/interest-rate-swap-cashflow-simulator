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
