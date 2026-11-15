# Step 1: Stabilize and document the existing project

## Result

**Passed.** The original AgriShift ZIP was preserved, its project code was integrated into the existing repository architecture, real and demo data modes were separated, and the app was run locally. The original ZIP's existing tests and the integrated project's tests were both executed.

## Source and working copy

- Original source: `Downloads/agrishift.zip`
- SHA-256: `1F0383ED884A6934F086E30D5A7F0D0D0435B3E811431BE6AB9B5E237958884B`
- Project root: `field shift/agrishift-ai/`
- Preserved backup: `field shift/agrishift-ai-backup-20261115-1042-09PKT/`
- Original ZIP code review: `docs/archive/agrishift-zip-code-documentation.md`

## Implemented

- Activated the original FastAPI backend, static frontend, and crop-rotation engine in the existing structure.
- Added explicit real/demo modes. Real mode never reads `features.example.json`; absent real features produce `insufficient_data`.
- Added SQLite tables for requests, results, source metadata, and model runs.
- Added consistent JSON error contracts, request IDs, local-only default CORS, analysis reload, and a database lifespan hook.
- Limited crop-rule hard rejection to verified, explicit hard constraints; unverified rules incur a soft penalty and an expert-review warning.
- Added confidence scoring components and confidence caps for unverified crop rules.
- Removed hardcoded front-end mock responses and hardcoded map bounds. The existing page reads its API and map metadata.
- Kept the original sample files and marked the supplied feature example as demo-only.

## Recorded tests and smoke checks

- Original ZIP tests: **52 passed, 1 third-party pytest warning**.
- Integrated tests at the step checkpoint: **69 passed, 1 third-party pytest warning**.
- `ruff check .`: passed.
- `python -m compileall -q -x '\\.venv' .`: passed.
- Local API smoke: health, page, OpenAPI, analyze response, analysis reload, weather status, context, slope metadata, and slope PNG all returned successfully.
- Browser automation/console inspection was not completed because the computer-use policy helper could not identify the current browser URL. API and static-page HTTP checks were run instead.

## Step 2 boundary

The project is not ready for real field recommendations. Landsat `SR_B2` through `SR_B7`, `ST_B10`, `QA_PIXEL`, and MTL metadata are absent from the expected scene directory. The project therefore has no real multi-point feature file or K-Means metrics/artifacts. No missing values were replaced with the supplied example row.

The runnable demo and full audit are described in `README_FINAL_DEMO.md` and `docs/audit/step-1-final-report.md`.
