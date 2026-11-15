# Step 1 final verification

Executed from the project root on Python 3.11.9:

| Command/check | Result |
|---|---|
| `python -m pytest -q` | 69 passed, 1 third-party AnyIO/pytest deprecation warning |
| `ruff check .` | Passed |
| `python -m compileall -q -x '\\.venv' .` | Passed |
| `GET /api/v1/health` | 200; 12 crops; explicit demo mode detected |
| `GET /` and `GET /openapi.json` | 200 |
| `GET /api/v1/context` | 200; context-only; reports non-aligned source dates |
| Demo `POST /api/v1/analyze` | 200; status `ok`; exactly 3 distinct options; `data_mode=DEMO` |
| `GET /api/v1/analyses/{analysis_id}` | 200; saved analysis reloaded from SQLite |
| `GET /api/v1/weather` in demo mode | 200; saved response flagged sample and not live |
| `GET /api/v1/layers/slope.png` and metadata | 200; metadata supplies real bounds and source |
| Real feature generation | Correctly stopped: no Landsat `SR_B2` asset found |
| K-Means training | Correctly stopped: real `features.json` is absent; no artifacts or metrics created |

Browser console and interactive visual QA could not be completed because the computer-use policy helper halted before UI input when it could not identify a browser URL. The app page and all listed flows were exercised through local HTTP instead.
