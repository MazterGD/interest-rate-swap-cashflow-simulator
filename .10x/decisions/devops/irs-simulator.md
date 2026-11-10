# DevOps — irs-simulator
- Run locally: `python -m venv .venv` → `pip install -r requirements.txt` → `streamlit run app.py`.
- **CI (ADR-003):** `.github/workflows/tests.yml` (verbatim in spec §12) runs on `pull_request` and `push` to `main`: Ubuntu, Python 3.11, pip cache, `pip install -r requirements.txt`, `pytest -q`. `permissions: contents: read`, no secrets.
- **Merge gate:** branch protection on `main` requires the `pytest` check and 1 approval. If it is unavailable (private repo, free plan), the team enforces it by hand.
- **No deployment, Docker or hosting** (README R2). CI never deploys.
- Owner: M6 (commits the workflow in the kickoff skeleton).
