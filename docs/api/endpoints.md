# Implemented API endpoints

The FastAPI app is in `apps/api/app/main.py`; OpenAPI is served at `/openapi.json`.

| Method and path | Behavior |
|---|---|
| `GET /api/v1/health` | Reports API status, crop count, data availability/mode, and whether Meteomatics credentials are configured (never returns secrets) |
| `GET /api/v1/crops` | Lists localized crop names and rule-verification status |
| `POST /api/v1/analyze` | Validates farmer inputs; returns `not_applicable`, `insufficient_data`, or exactly three distinct rule-based rotation options; persists all outcomes |
| `GET /api/v1/analyses/{analysis_id}` | Reads saved request/result from SQLite |
| `GET /api/v1/context` | Returns sanitized real SMAP/GPM regional context and temporal-alignment limitations |
| `GET /api/v1/weather?lat=...&lon=...` | Returns live Meteomatics data, an explicit demo sample, or unavailable status |
| `GET /api/v1/layers/metadata` | Returns source-aware layer bounds and metadata |
| `GET /api/v1/layers/{name}.png` | Serves whitelisted `ndvi`, `ndmi`, `bsi`, or `slope` layers when present |

Errors use a JSON object containing `error.code`, a safe message, request ID, and details. The `X-Request-ID` response header matches the JSON request ID. The default CORS allowlist is localhost-only; wildcard origins are rejected in production mode.

Unavailable real feature data is not filled from the example file. Real mode returns `insufficient_data` for missing required feature rows. Forecast samples are demo-only and are never labeled live.
