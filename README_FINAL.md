# AgriShift AI — final local release

AgriShift AI is a multilingual crop-rotation decision-support app for the Hyderabad, Sindh pilot. Farmers can use it without an account. Experts use one authenticated EXPERT account to review saved analyses. Recommendations are rule-based comparisons, not yield forecasts or field prescriptions.

## Workflows and architecture

The farmer flow is a Next.js and React interface written in TypeScript, styled with Tailwind CSS, and mapped with MapLibre. It collects a pin, crop history, water and soil observations, and a priority; it saves the result and opens three rotation options. The Expert Portal is served by Next.js and uses FastAPI v2 endpoints for login, analysis search, reviews, score details, and notes.

FastAPI also serves the public farmer API. SQLite at `data/agrishift.db` stores analyses and expert records. `services/rotation-engine/` scores the three rotation strategies. The existing scikit-learn K-Means model groups environmental conditions; it does not predict crops, disease, or yield.

## Data and model use

- `data/features/features.json` contains 149 validated pilot feature points. The API uses Haversine distance and returns a result only within 2 km.
- Landsat 9 contributes the precomputed NDVI, NDMI, BSI, and surface-temperature summaries at 30 m. PNG layers and their actual bounds come from `data/layers/` and `metadata.json`.
- SRTM supplies elevation and slope context at 30 m. NASA POWER is coarse historical climate context; SMAP and GPM remain regional context.
- Meteomatics can be live when server credentials are configured. Otherwise, the saved weather sample is identified as a sample and becomes expired after its validity date. Missing weather does not block rotation analysis.
- The K-Means scaler, model, profile, metrics, and manifest are existing artifacts. Startup checks their schema and checksums; this release does not retrain the model.

## Install and start

Use Python 3.11 and Node.js. From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
cd apps/web
npm ci
cd ..\..
python scripts\start_demo.py
```

The launcher checks the selected feature file, map layers, model artifacts, Python packages, frontend installation, and SQLite initialization. It starts FastAPI and the local Next.js server, then prints the farmer URL, Expert login URL, and API docs URL. Default addresses are `http://127.0.0.1:3000`, `/expert/login`, and `http://127.0.0.1:8000/docs`.

## Environment settings

Copy `.env.example` to `.env`; keep `.env` private. Common settings are:

- `APP_ENV=development` or `production`
- `DATABASE_URL=sqlite:///data/agrishift.db`
- `CORS_ORIGINS` with explicit allowed origins; production rejects `*`
- `DEMO_MODE=false` and `FEATURES_FILE=data/features/features.json`
- `LAYER_DIRECTORY=data/layers`
- `EXPERT_EMAIL`, `EXPERT_PASSWORD_HASH`, and `EXPERT_SESSION_SECRET`
- `METEOMATICS_USERNAME` and `METEOMATICS_PASSWORD` (optional, server-side only)
- `NEXT_PUBLIC_AGRISHIFT_API_URL` for public browser requests and `AGRISHIFT_API_URL` for the Next.js expert proxy

Production startup requires the expert email, PBKDF2-SHA256 password hash, and a session secret of at least 32 characters. Generate the hash with `python scripts/hash_expert_password.py`; the password prompt is hidden and only the hash is printed. Never place the plain-text password in an environment file. Local development can run the farmer experience without expert credentials; the launcher explains how to configure the expert account.

## API routes

Public routes include `GET /api/v1/health`, `POST /api/v1/analyze`, `GET /api/v1/analyses/{analysis_id}`, `GET /api/v1/crops`, `GET /api/v1/context`, `GET /api/v1/weather`, `GET /api/v1/layers/metadata`, and `GET /api/v1/layers/{ndvi|ndmi|bsi|slope}.png`.

Expert routes include `POST /api/v2/expert/auth/login`, `POST /api/v2/expert/auth/logout`, `GET /api/v2/expert/auth/me`, `GET /api/v2/expert/analyses`, `GET /api/v2/expert/analyses/summary`, `GET /api/v2/expert/analyses/{analysis_id}`, review create/update/history endpoints, and server-side notes endpoints. The analysis list supports filters and page-based pagination.

## Database and data safety

Initialization is additive and idempotent. It creates the five expert tables and adds missing compatible columns without deleting the existing `analysis_requests`, `analysis_results`, `dataset_metadata`, or `model_runs` rows. SQLite foreign-key checks are enabled. Before changing a development database schema, make a copy of `data/agrishift.db`; tests use temporary databases.

## Verification

From the project root:

```powershell
cd apps/web
npm run typecheck
npm run build
cd ..\..
python -m pytest -q
```

The final release was checked with the full Python suite, frontend typecheck and production build, a live farmer browser flow, and a release ZIP content/checksum inspection.

## Security and responsible use

Expert sessions use Secure, HttpOnly, SameSite=Strict cookies with an eight-hour expiry. Login errors are generic. A lightweight in-memory limiter allows at most ten failed attempts per client address per ten minutes; a restart clears it, so a public deployment should also enforce rate limits at its edge proxy. Expert data is stored on the server, and expert API responses are not cached.

Environmental clusters describe satellite patterns only. A nearest-point summary can differ from conditions inside a specific field. Unverified agronomic rules add penalties and warnings instead of independently rejecting crops, and selected unverified rules cap confidence. Confirm suggestions with local field inspection and an agriculture expert, and verify seed availability, sowing dates, and market demand.

## Deployment and known limits

This workspace has no configured deployment target or deployment credentials, so this release is verified locally and is not deployed. A deployment needs HTTPS, a durable persistent location for SQLite, an explicit production `CORS_ORIGINS`, `APP_ENV=production`, the expert hash and session secret, and the correct API URL in both frontend environment settings. Deploy the API with `uvicorn app.main:app --app-dir apps/api --host 0.0.0.0 --port <service-port>` and the frontend with `npm run build` followed by `npm start` in `apps/web`.

The pilot covers one area and uses precomputed environmental points. Weather may be an expired saved sample when live provider credentials are absent. SQLite is intended for the local/single-instance demo; production should use only a host with durable single-instance storage unless the application is deliberately migrated and tested for another database.

## Troubleshooting

- If the launcher reports missing packages, activate `.venv`, install `requirements.lock.txt`, then run `npm ci` inside `apps/web`.
- If startup reports missing feature or model files, restore the packaged runtime assets; do not substitute example data while `DEMO_MODE=false`.
- If expert login returns service unavailable, configure all three `EXPERT_*` settings and restart the API.
- If the frontend cannot reach the API, confirm ports 3000 and 8000 are free and set `NEXT_PUBLIC_AGRISHIFT_API_URL` and `AGRISHIFT_API_URL` to the running API base URL.
- If a forecast is labeled expired or unavailable, rotation analysis should still complete; check the weather status shown on the result.
