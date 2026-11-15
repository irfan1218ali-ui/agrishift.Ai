# Workspace discovery record

Discovery date: 2026-11-15 (Asia/Karachi)

| Item | Location or result |
|---|---|
| Original AgriShift ZIP | `Downloads/agrishift.zip` |
| ZIP SHA-256 | `1F0383ED884A6934F086E30D5A7F0D0D0435B3E811431BE6AB9B5E237958884B` |
| Existing project root | `field shift/agrishift-ai/` |
| Existing architecture backup | `field shift/agrishift-ai-backup-20261115-1042-09PKT/` |
| Git branch at start of implementation | `architecture/six-source-restructure`; no commits or tags existed |
| Stabilization branch | `hackathon/step-1-stabilize` |
| API | FastAPI in `apps/api/app/` |
| Web frontend | Existing static multilingual app in `apps/web/index.html` |
| Rotation engine | `services/rotation-engine/rotation_engine/` |
| Supplied tests | API/client/service and rotation-engine tests |
| Python | 3.11.9 local virtual environment |
| SQLite | `data/agrishift.db` is runtime state and ignored by Git |
| Real feature file | `data/features/features.json` is absent |
| Explicit example features | `data/features/features.example.json`, labeled as placeholder values |
| Landsat scene folder | `data/raw/landsat/USGS_Landsat_C2_L2_Hyderabad_2025-09-22/`; contains manifests and README instructions only |

The original ZIP's contents and per-file code summary are kept at `docs/archive/agrishift-zip-code-documentation.md`. The extracted review copy is under `.tmp-zip-review/agrishift/` and is ignored; it was not used as the working project.

## Existing runtime and safeguards

The runtime uses FastAPI, the existing rotation engine, a static HTML/JavaScript frontend, SQLAlchemy with SQLite, NumPy, scikit-learn, and local source adapters. The initial architecture scaffold named PostgreSQL/PostGIS, Redis, Celery, Next.js, and several future ML tools; those were not introduced into the hackathon runtime. The original architecture docs remain available as historical design material.

`DEMO_MODE` defaults to false. The dedicated `scripts/start_demo.py` entry point makes a local demo explicit and uses the provided example file; the page shows a persistent demo banner. Local `.env`, databases, raw datasets, processed rasters, and model artifacts are excluded from Git.
