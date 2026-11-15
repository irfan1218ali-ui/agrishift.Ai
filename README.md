# AgriShift AI

AgriShift AI is a multilingual crop-rotation decision-support prototype for the Hyderabad, Sindh pilot. It combines a rule-based rotation engine with evidence and uncertainty summaries. It does not diagnose crop disease, predict yield, or replace a local agronomist.

## Current project status

- The Step 2A real-data branch is merged into `hackathon/step-2b-integration`.
- The API loads 149 validated Hyderabad pilot feature points, saved environmental K-Means artifacts, four map overlays, SMAP/GPM summaries, and normalized Meteomatics weather.
- The farmer UI and API run together on FastAPI. Successful analyses are stored in SQLite and can be retrieved by analysis ID.
- The interface labels real and demo modes. Demo example data is used only when `DEMO_MODE=true` is explicitly selected.

See [`docs/data/`](docs/data/) and [`docs/demo/known-limitations.md`](docs/demo/known-limitations.md) for source details and limitations.

## Run the local MVP

Use Python 3.11. From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
python scripts\start_demo.py
```

Open `http://127.0.0.1:8000`. The launcher uses real features by default and serves the frontend and API from one local server. The saved weather forecast is always labelled as a sample. Optional provider credentials enable live weather.

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
- `scripts/data/`: source discovery, validation, manifests, regional summaries, terrain overlay, and weather products.
- `scripts/start_demo.py`: starts the real-data MVP; explicit `DEMO_MODE=true` selects the labelled example mode.
- `ml/clustering/`: K-Means training, evaluation, prediction, and runtime artifacts.
- `data/manifests/`: checksummed source inventory without developer-specific absolute paths.
- `docs/`: architecture, source inventory, API/database notes, audit, limitations, and demo guide.

The full original ZIP code inventory is in `docs/archive/agrishift-zip-code-documentation.md`.
