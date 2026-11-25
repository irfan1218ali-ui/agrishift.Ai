# AgriShift AI

AgriShift AI is a multilingual crop-rotation decision-support application for the Hyderabad, Sindh pilot. It combines validated environmental evidence with an explainable rule-based rotation engine. Its K-Means model groups environmental conditions; it does not predict crops, disease, or yield.

## Current release

- Phase 1 farmer and expert frontend: Next.js, React, TypeScript, Tailwind CSS, and MapLibre.
- Phase 2 Expert Portal: one backend-authenticated EXPERT account, global analysis list, reviews, server-side notes, persistent review status, and eleven explainable score components.
- Existing public farmer APIs and the existing three-option rotation flow are preserved.
- Real mode uses 149 validated feature points and the checked-in runtime K-Means artifacts; demo data requires explicit `DEMO_MODE=true`.
- SQLite initialization is additive and preserves existing farmer analyses.

## Run locally

Use Python 3.11 and Node.js. The startup and expert account steps are documented in [`README_FINAL_DEMO.md`](README_FINAL_DEMO.md). The integrated launcher is:

```powershell
python scripts\start_demo.py
```

Open `http://127.0.0.1:3000`. The frontend uses port 3000 and FastAPI uses port 8000. Install Python dependencies from `requirements.lock.txt` and frontend dependencies with `npm ci` in `apps/web` before starting.

## Verify

```powershell
cd apps/web
npm run typecheck
npm run build
cd ..\..
python -m pytest -q
```

## Project map

- `apps/api/app/`: FastAPI public and expert APIs, domain service, data readers, and SQLite persistence.
- `apps/web/src/`: multilingual farmer flow, Expert Dashboard, analysis detail, and components.
- `services/rotation-engine/`: existing crop-rule loading and three-strategy rotation logic.
- `scripts/start_demo.py`: integrated local launcher; `scripts/hash_expert_password.py`: hidden-input PBKDF2 hash generator.
- `scripts/package_release.py`: validated runnable ZIP builder that excludes raw datasets, local databases, credentials, virtual environments, caches, and `node_modules`.
- `data/`, `ml/`: pilot runtime inputs and the existing verified model artifacts.

See [`docs/data/`](docs/data/) and [`docs/demo/known-limitations.md`](docs/demo/known-limitations.md) for evidence sources and scientific limits. See [`docs/security/README.md`](docs/security/README.md) for account and deployment security notes.
