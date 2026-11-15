# AgriShift AI

AgriShift AI is a multilingual crop-rotation decision-support prototype for the Hyderabad, Sindh pilot. It combines a rule-based rotation engine with evidence and uncertainty summaries. It does not diagnose crop disease, predict yield, or replace a local agronomist.

## Current project status

- The original ZIP source is preserved and documented in [`docs/archive/agrishift-zip-code-documentation.md`](docs/archive/agrishift-zip-code-documentation.md).
- The FastAPI API, static farmer interface, rotation engine, SQLite persistence, source manifests, SRTM slope overlay, regional SMAP/GPM summary, and guarded feature/K-Means utilities are present.
- The requested Landsat scene bundle is missing its actual raster and MTL files. No real `features.json` can be produced and no K-Means model or metrics have been created.
- The integrated demo can run in explicit demo mode. It uses the supplied, clearly marked example feature row and a saved Meteomatics response. The page displays `DEMO DATA — NOT REAL ENVIRONMENTAL ANALYSIS` persistently.
- Release verdict: **NOT READY for real environmental recommendations** until the Landsat scene is supplied and the real feature workflow, model, and acceptance scenarios pass.

See [`README_FINAL_DEMO.md`](README_FINAL_DEMO.md), [`docs/data/source-inventory.md`](docs/data/source-inventory.md), and [`docs/audit/test-results-step-2.md`](docs/audit/test-results-step-2.md) for setup, results, and known blockers.

## Run the local demo

Use Python 3.11. From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
python scripts\data\create_sanitized_weather_sample.py
python scripts\start_demo.py
```

Open `http://127.0.0.1:8000`. `scripts/start_demo.py` explicitly selects demo mode and the supplied example features unless `DEMO_MODE` or `FEATURES_FILE` was explicitly set in the shell. Never present this demo as a real environmental analysis.

To start the API in real mode, set `DEMO_MODE=false` and use `uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000`. Until `data/features/features.json` has been generated from the real Landsat scene, the analysis endpoint correctly returns `insufficient_data`.

## Checks

```powershell
python -m pytest -q
ruff check .
python -m compileall -q -x '\\.venv' .
```

## Project map

- `apps/api/app/`: FastAPI routes, input schemas, feature reading, NASA POWER and Meteomatics adapters, regional context, and SQLite persistence.
- `apps/web/index.html`: existing multilingual farmer and expert views, connected to the API.
- `services/rotation-engine/`: existing crop-rule loading and three-strategy rotation logic.
- `scripts/data/`: source discovery, validation, manifests, regional summary, terrain overlay, and saved-sample sanitation.
- `scripts/build_real_features.py`: Landsat/SRTM/POWER/SMAP/GPM point builder; fails closed if required Landsat assets are absent.
- `ml/clustering/`: real-row validation, K-Means training, evaluation, and prediction; no example-data fallback.
- `data/manifests/`: checksummed source inventory without developer-specific absolute paths.
- `docs/`: architecture, source inventory, API/database notes, audit, limitations, and demo guide.

The full original ZIP code inventory is in `docs/archive/agrishift-zip-code-documentation.md`.
