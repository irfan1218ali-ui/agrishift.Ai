# AgriShift AI — verified local release

AgriShift AI is a multilingual crop-rotation decision-support application for the Hyderabad, Sindh pilot. The farmer flow is public. The Expert Portal uses one backend-authenticated EXPERT account with server-side analysis reviews and notes. The project uses the existing rule-based rotation engine and environmental K-Means cluster; it does not diagnose crop disease or predict yield.

## Start

Requires Python 3.11 and Node.js. From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
cd apps/web
npm ci
cd ..\..
python scripts\start_demo.py
```

Open `http://127.0.0.1:3000`. Next.js runs on port 3000 and FastAPI on port 8000; Next proxies authenticated expert requests to the API. The API initializes `data/agrishift.db`, defaults to `REAL DATA`, and labels the saved Meteomatics forecast as a sample. Optional Meteomatics credentials enable live weather. To explicitly use the example feature set, set `$env:DEMO_MODE='true'` before starting; the page displays `DEMO DATA`.

## Configure the expert account

Copy `.env.example` to `.env` and set `EXPERT_EMAIL`, `EXPERT_PASSWORD_HASH`, and `EXPERT_SESSION_SECRET`. Generate the password hash with `python scripts/hash_expert_password.py`; it prompts without echoing the password and prints only a PBKDF2 hash. Set a randomly generated session secret of at least 32 characters. Keep `.env` private and restart the API. No expert account is active until these values are set.

The session cookie is Secure, HttpOnly, SameSite=Strict, and expires after eight hours. Logout revokes the active session. Farmer analysis remains public if expert configuration is missing.

## Included behavior

- Loads 149 real feature points and chooses the nearest point using Haversine distance, capped at 2 km.
- Returns `not_applicable` outside supported coverage or beyond the nearest-point limit; returns `insufficient_data` when required core features are missing.
- Loads checksum-validated K-Means scaler, model, profiles, and metrics. Labels are `Relatively vegetated`, `Intermediate condition`, and `Higher bare/thermal exposure`.
- Serves NDVI, NDMI, BSI, and slope overlays with bounds from `data/layers/metadata.json`.
- Reports Meteomatics as live, saved sample, expired sample, or unavailable. Weather does not block rotation analysis.
- Persists farmer requests/results, expert users/reviews/notes, review status, score components, dataset metadata, and model metadata in SQLite. Initialization adds tables without deleting existing analyses.
- Keeps exactly three distinct rotation options and the existing farmer flow. Unverified crop rules receive penalties and warnings, not independent hard rejection. K-Means is environmental clustering, not crop prediction.

## API routes

- Public: `GET /api/v1/health`, `POST /api/v1/analyze`, `GET /api/v1/analyses/{analysis_id}`, `GET /api/v1/crops`, `GET /api/v1/context`, `GET /api/v1/weather`, `GET /api/v1/layers/metadata`, `GET /api/v1/layers/{ndvi|ndmi|bsi|slope}.png`.
- Expert auth: `POST /api/v2/expert/auth/login`, `POST /api/v2/expert/auth/logout`, `GET /api/v2/expert/auth/me`.
- Expert analyses: `GET /api/v2/expert/analyses`, `GET /api/v2/expert/analyses/summary`, `GET /api/v2/expert/analyses/{analysis_id}`.
- Expert reviews: `POST /api/v2/expert/analyses/{analysis_id}/reviews`, `PATCH /api/v2/expert/reviews/{review_id}`, `GET /api/v2/expert/analyses/{analysis_id}/reviews`.
- Expert notes: `GET` and `PUT /api/v2/expert/analyses/{analysis_id}/notes`.

## Verify

```powershell
cd apps/web
npm run typecheck
npm run build
cd ..\..
python -m pytest -q
```

Use `.venv` for pytest when the system Python does not include the project test dependencies.

## Limits and deployment

The analysis uses the nearest precomputed point and its local raster summary; it is not an exact field measurement. SMAP and GPM are coarse regional context. Their observation periods do not fully align with Landsat, and GPM is a weekly mean daily rate, not a daily rainfall series. Local field inspection and agronomic review remain necessary.

This workspace has no configured public deployment target or deployment credentials. The verified release is local; do not expose it publicly until TLS, restricted origins, private secrets, and SQLite backup/retention are configured.
