# Architect — irs-simulator
- **Components:** spec §5 (`swap/` domain, `ui/` render functions, `app.py` wiring).
- **Contracts:** spec §6 (frozen; `swap/models.py` copied verbatim at kickoff).
- **Data flow:** inputs + rates -> validate -> `simulate_swap` -> `summarize` -> summary, chart, table, explainer. It recomputes on every Streamlit rerun, with no caching needed (<= 120 periods).
- **Failure modes:** invalid input -> `st.warning` + `st.stop()`; rate-length mismatch -> `ValueError` (programmer error); editor state loss -> explicit widget key (spec §7).
- **Trade-offs:** float over Decimal (simplicity); recompute over cache (simplicity); Streamlit theme over custom CSS (KISS).
- **ADRs:** 001 (stack + layering), 002 (frozen contracts + walking skeleton), 003 (unit + integration tests, CI on PRs).
