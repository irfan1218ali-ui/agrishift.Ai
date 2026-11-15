# AgriShift AI Hackathon MVP

The local app serves the existing English, Urdu, and Sindhi farmer flow with the real Hyderabad pilot data by default. It uses the rule based rotation engine, validated feature points, neutral environmental clustering, map overlays, forecast context, and local SQLite persistence. It does not diagnose crop disease or predict yield.

## Start

Requires Python 3.11. From the project root:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
python scripts\start_demo.py
```

Open `http://127.0.0.1:8000`. The launcher serves the frontend and API together, defaults to `REAL DATA`, initializes `data/agrishift.db`, and labels the saved Meteomatics forecast as a sample. Optional credentials can enable live weather. To explicitly use the placeholder example data, set `$env:DEMO_MODE='true'` before starting; the page then displays `DEMO DATA`.

## Included behavior

- Loads 149 real feature points and chooses the nearest point using Haversine distance, capped at 2 km.
- Returns `not_applicable` outside supported coverage or beyond the nearest-point limit; returns `insufficient_data` when required core features are missing.
- Loads the checksum and version-checked K-Means scaler, model, profiles, and metrics. Labels are `Relatively vegetated`, `Intermediate condition`, and `Higher bare/thermal exposure`.
- Serves NDVI, NDMI, BSI, and slope overlays with bounds from `data/layers/metadata.json`.
- Reports Meteomatics as live, saved sample, expired sample, or unavailable. Weather does not block rotation analysis.
- Persists requests, results, dataset metadata, and model metadata in SQLite. Results are retrievable by analysis ID.
- Keeps the existing farmer flow, three rotation cards, expert view, map pin, and WhatsApp sharing. Unverified crop rules carry a penalty and expert-review warning rather than independent hard rejection.

## API

- `GET /api/v1/health`
- `POST /api/v1/analyze`
- `GET /api/v1/analyses/{analysis_id}`
- `GET /api/v1/context`
- `GET /api/v1/weather?lat=...&lon=...`
- `GET /api/v1/layers/metadata`
- `GET /api/v1/layers/{ndvi|ndmi|bsi|slope}.png`

## Verify

```powershell
python -m pytest -q
python -m ruff check .
python -m compileall -q -x '\\.venv' .
```

## Limits

The analysis uses the nearest precomputed point and its 150 m local summary; it is not an exact field measurement. SMAP and GPM are coarse regional context, and their observation periods do not align with each other and Landsat. GPM is a weekly mean daily rate, not a daily rainfall series. Local field inspection and agronomic review remain necessary.