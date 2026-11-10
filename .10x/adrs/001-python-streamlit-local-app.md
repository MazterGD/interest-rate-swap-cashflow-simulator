# ADR-001: Python + Streamlit single-process local app, pure domain package

**Status:** Accepted
**Date:** 2026-11-10
**Feature:** irs-simulator
**Author:** 10x-Team (Architect + Staff Engineer)

## Context
A 6-member student team needs a local, free, low-setup demo of an interest-rate swap's cash flows. It needs an interactive UI with editable rates, a chart, a table and a CSV export. There is no deployment, no persistence and no auth. The team is comfortable with Python.

## Decision
- Build one Streamlit app run with `streamlit run app.py`. The only runtime dependency is `streamlit`, with Altair and pandas installed alongside it.
- Split the code into three layers:
  - `swap/`: pure Python domain (models, engine, scenarios, validation, export). It never imports Streamlit.
  - `ui/`: thin Streamlit render functions, one concern per file.
  - `app.py`: composition only.
- Tests use pytest for `swap/` and pure UI helpers, plus `streamlit.testing.v1.AppTest` for an app smoke test.

## Alternatives Considered
| Alternative | Pros | Cons | Why Not |
|---|---|---|---|
| Plain HTML/CSS/JS (no dependencies) | Zero install, full design control | The team prefers Python; charts and the table editor must be built by hand | Team chose Python (README D1) |
| React + Vite | Component model, rich ecosystem | npm toolchain, build step, more setup | Violates KISS and minimal setup |
| Flask/FastAPI + HTML front end | Clear separation of API and UI | Two layers to build, more code | YAGNI for a local demo |
| Single `app.py` with everything | Fewest files | Untestable maths, 6 people editing one file | Blocks parallel work |

## Consequences
### Positive
- One `pip install`, and the app gives instant reactivity with no Run button.
- The finance logic is unit-testable in isolation.
- Separate files map onto separate owners.
### Negative
- Streamlit's layout and styling control is limited, so the UI design must work within its widgets and theme.
- The whole script reruns on each change. This is fine at ≤ 120 periods.
### Risks
- Streamlit API changes between versions (e.g. chart width arguments). Mitigation: pin `streamlit>=1.40,<2` and use the documented API of the installed version.
- `st.data_editor` state resets unexpectedly. Mitigation: use the explicit widget key from spec §7.

## Dependencies
- Constrains every UI file to Streamlit primitives.
- ADR-002 builds on this layering.
