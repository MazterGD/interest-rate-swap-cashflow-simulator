# Senior Engineer — irs-simulator: implementation notes per workstream
- **M1:** compute `net_payer = floating - fixed`, then negate it for RECEIVE_FIXED. Accumulate the cumulative total in the same loop. Do not round. Use `pytest.approx` in tests.
- **M2:** use `random.Random(seed)`, never the global `random`, and `round(max(0.0, r), 6)`. The `data_editor` takes a DataFrame with Rate (%), keyed as in spec §7, with the Period column disabled. Convert back with `/100`.
- **M3:** use `st.columns(2)` for the 2x2 grid. `st.segmented_control` returns `None` when deselected, so fall back to the default. Convert the fixed rate with `/100`.
- **M4:** use a real minus sign (U+2212) in `fmt_signed_money`. Render the hero with `st.markdown` and an inline colour span. This is the only place custom HTML is allowed, and its content is our own formatted number only. Use `column_config` or a pandas Styler for number formats.
- **M5:** use `alt.condition` for the green/red colour and treat net == 0 as neutral (`MUTED`). Build with `alt.vconcat(top, bottom)`, use muted axes and hide legends.
- **M1 (integration):** in `test_pipeline.py`, parametrise over `RatePreset` × `{1, 2, 4}` and assert `sum(net) == total_net == cash_flows[-1].cumulative_net`. Read the CSV back with `pandas.read_csv(io.BytesIO(...))`.
- **M6:** keep `app.py` at about 40 lines with no maths. In AppTest, find the position widget by its key, change it, then assert that the hero text changes sign. The smoke test only asserts `not at.exception`, so it passes against the skeleton. Copy the CI YAML and `pyproject.toml` verbatim from spec §12.
- **Tricky parts:** data_editor state (M2), zero/break-even display (M4), the colour of zero bars (M5).
