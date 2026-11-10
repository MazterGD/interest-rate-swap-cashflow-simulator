# Staff Engineer — irs-simulator
- **Patterns:** pure functions in `swap/`. UI functions are named `render_*`. Chart building is separate from rendering (`build_*` is pure and testable).
- **Shared helpers:** `ui/formatting.py` (money, rate and sign formatting, colour constants) is owned by M4. Other UI modules may import it, and the kickoff placeholders keep it importable before M4 merges.
- **Cross-cutting:** validation happens once, in `app.py`, via `swap/validation.py`. There is no logging (local demo). Errors are user-facing messages only.
- **Testing:** one unit-test file per module in `tests/unit/`; cross-module tests in `tests/integration/` with `@pytest.mark.integration`. The spec §3 worked example is the canonical fixture, defined locally in each test file so there is no shared conftest to conflict on. CI runs everything on every PR (ADR-003).
