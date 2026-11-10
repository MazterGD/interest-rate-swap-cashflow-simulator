# CTO — irs-simulator
- **Problem:** the course needs a working demonstration of how an interest-rate swap's fixed and floating legs net into a settlement over multiple periods.
- **Build vs buy:** build. Existing tools (Bloomberg SWPM, Excel templates) are paid, opaque or not ours to present. The scope is small (~500 LOC).
- **Stack:** Python >= 3.11 + Streamlit, chosen by the team (README D1). Plain HTML/JS was recommended for zero setup and is recorded as the alternative.
- **Constraints:** free, local only, two pip packages, no deployment or DB. CI is only for tests on PRs (GitHub Actions, free; ADR-003).
- **Risk:** low. The main risk is scope creep into valuation and day counts. Mitigation: the spec §2 out-of-scope list.
