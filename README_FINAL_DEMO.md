# AgriShift AI: local demo and handoff

## Honest status

This package runs the existing AgriShift interface and backend in an explicitly labeled demo mode. Its supplied feature example is marked as placeholder data; it is not a real satellite analysis. The actual local workspace includes measured SRTM slope and regional SMAP/GPM context, and it has a sample-weather parser and SQLite persistence.

The requested Landsat scene is incomplete: the `SR_B2`–`SR_B7`, `ST_B10`, `QA_PIXEL`, and MTL files were not present. Real multi-point features and K-Means outputs therefore do not exist. The final scientific acceptance verdict is **NOT READY**. No model metrics, cluster scores, or real field recommendations are claimed.

## What the system does

- **Rotation recommendations:** Existing rule-based engine produces three distinct strategies only when complete eligible features are present. Crop facts are marked verified/unverified; unverified rules require local review and cannot independently hard-reject a crop.
- **Environmental clustering:** K-Means is reserved for grouping six environmental features. It is not a crop predictor or health diagnosis. The trainer refuses example data and needs at least 20 complete distinct real points. It has not been run.
- **Regional context:** SMAP surface/root-zone soil moisture and GPM weekly mean daily precipitation rate are shown as coarse regional context. The observed periods differ by more than a year; the API returns `temporal_alignment=not_aligned`.
- **Terrain:** Real SRTM slope PNG and source metadata are served. Slope does not diagnose drainage or waterlogging.
- **Weather:** Live Meteomatics is optional. The demo can use a sanitized saved response, labeled as a sample with a valid period and expiry. Real mode returns unavailable if a live forecast cannot be obtained.
- **Persistence:** SQLAlchemy creates `analysis_requests`, `analysis_results`, `dataset_metadata`, and `model_runs` in local SQLite. Raw rasters are not stored in SQLite.
- **Languages and UI:** The existing English/Urdu/Sindhi interface is retained and connected to API responses, confidence, limitations, analysis IDs, sample status, context, and layer metadata.

## Setup

Requires Python 3.11. From the project root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
python scripts\data\create_sanitized_weather_sample.py
```

The ZIP includes the small required runtime products: the supplied placeholder feature example, sanitized saved forecast, real slope overlay/metadata, regional context summary, source manifests, source code, and tests. It excludes raw SMAP/GPM/SRTM/Landsat assets, `.env`, local database files, virtual environments, caches, and model artifacts.

## Start in demo mode

```powershell
python scripts\start_demo.py
```

Open `http://127.0.0.1:8000`. The launcher selects `DEMO_MODE=true` unless a shell variable explicitly overrides it, uses the supplied example feature file unless a shell feature path was explicitly set, initializes SQLite, and binds to loopback by default. Verify the persistent banner says `DEMO DATA — NOT REAL ENVIRONMENTAL ANALYSIS`.

## Start in real mode

Set `DEMO_MODE=false` in the process environment and run:

```powershell
$env:DEMO_MODE = 'false'
uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

Provider credentials, if used, belong only in an ignored local `.env` or process environment. The `.env.example` has blank credential fields. Real analysis requires a generated `data/features/features.json`; without it, the API returns `insufficient_data`. In real mode a failed or unconfigured weather request is unavailable, and the Meteomatics sample is not used.

## Real feature processing when Landsat is supplied

Place the exact scene's original files under `data/raw/landsat/` without renaming them. Required assets are `SR_B2`–`SR_B7`, `ST_B10`, `QA_PIXEL`, and one MTL file. Rebuild the real context/terrain products if needed, then run:

```powershell
python scripts\data\build_terrain_overlay.py
python scripts\data\build_regional_context.py
python scripts\build_real_features.py
python ml\clustering\train_kmeans.py
python ml\clustering\evaluate.py
```

The feature builder reads scale/offset values from MTL, masks QA_PIXEL bits 0–5, computes NDVI/NDMI/BSI and ST_B10 Celsius, samples SRTM elevation/slope and POWER summaries, and adds SMAP/GPM only as regional context. It refuses fewer than 20 complete point rows. Do not run the trainer until that generated real file passes inspection. A trained model needs expert interpretation before neutral labels are considered reviewed.

## API and files

- `GET /api/v1/health`: mode and data availability.
- `POST /api/v1/analyze`: three rule-based rotation strategies when critical real features exist; otherwise an explicit status.
- `GET /api/v1/analyses/{analysis_id}`: persisted request/result.
- `GET /api/v1/context`: sanitized SMAP/GPM context with the period-alignment limitation.
- `GET /api/v1/weather?lat=...&lon=...`: live forecast, demo sample, or unavailable status.
- `GET /api/v1/layers/metadata` and `GET /api/v1/layers/slope.png`: source-aware terrain overlay.

The SQLAlchemy table definitions are in `apps/api/app/db.py`. The full original ZIP source review is in `docs/archive/agrishift-zip-code-documentation.md`; data validation is in `docs/data/source-inventory.md`.

## Tests and troubleshooting

```powershell
python -m pytest -q
ruff check .
python -m compileall -q -x '\\.venv' .
```

The integrated checks currently report 69 passed and one third-party deprecation warning. If the demo says no features are available, confirm that `DEMO_MODE` is not explicitly false and that `data/features/features.example.json` exists. If the API returns `insufficient_data` in real mode, provide and validate the missing Landsat scene and run the real feature builder. If weather is unavailable, configure valid Meteomatics credentials for live weather or start the explicit demo.

## Limitations and responsible use

- SMAP cells are roughly 9 km and GPM cells roughly 0.1°. Neither is a field sensor.
- The supplied GPM asset is a weekly mean rate, not daily totals. Rainy days and maximum daily rainfall cannot be calculated from it.
- SMAP data are from 2026-10-01 to 2026-10-07; GPM data are from 2025-09-01 to 2025-09-07. They are not temporally aligned.
- NASA POWER summarizes a coarse regional grid and one 2015–2025 period; it repeats as context rather than distinguishing neighboring fields.
- No real Landsat vegetation, bare-soil, thermal, or cloud-free values are available.
- No K-Means model was trained; no scores, profiles, or labels are available.
- Crop-rule data are unverified; local agronomic review and field inspection remain necessary.
- DEM slope is not a waterlogging or drainage diagnosis.
- The saved weather response expires after its supplied validity window and is never live.

This is decision support for farmer judgment, not a substitute for soil testing, farm inspection, or local agronomic advice.
