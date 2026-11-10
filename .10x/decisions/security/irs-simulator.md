# Security — irs-simulator (planned threat model)
- **Surface:** local Streamlit on localhost; no auth, secrets, network calls or persisted data.
- **Input:** numeric widgets with bounds, plus `validate_*` (spec §8). No uploaded files are parsed.
- **HTML:** `unsafe_allow_html` is used only for the hero amount, and only with our own formatted numbers, never raw user strings.
- **CSV:** numeric values only, so there is no formula-injection risk (no user text in the export).
- **Dependencies:** two well-known packages, pinned to a major version.
- **CI:** read-only `GITHUB_TOKEN` (`permissions: contents: read`), no secrets, `pull_request` trigger (not `pull_request_target`), official `actions/*` only.

Review against the built code in Phase 5.
