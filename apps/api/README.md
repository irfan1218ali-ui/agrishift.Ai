# AgriShift FastAPI service

The API preserves the public farmer endpoints under `/api/v1` and provides the single-role EXPERT portal under `/api/v2/expert`. It uses validated real pilot data, the existing rule-based rotation engine, saved K-Means environmental clusters, and SQLite. SMAP and GPM are regional context. Weather may be unavailable without blocking a rotation result.

## Start and test

Use the repository-level instructions in `README_FINAL.md`. For backend tests from the project root, run `python -m pytest -q` using the project virtual environment.

## Expert account setup

Configure `EXPERT_EMAIL`, `EXPERT_PASSWORD_HASH`, and `EXPERT_SESSION_SECRET` in the root `.env`. Generate the PBKDF2 password hash using `python scripts/hash_expert_password.py`; the plaintext is prompted invisibly and is never written to the source tree. The API seeds one active EXPERT account and uses an eight-hour signed Secure, HttpOnly, SameSite=Strict cookie. With missing credentials, expert endpoints return a structured `503`; farmer endpoints remain available.

## Routes

Public farmer API: `GET /api/v1/health`, `POST /api/v1/analyze`, `GET /api/v1/analyses/{analysis_id}`, `GET /api/v1/crops`, `GET /api/v1/context`, `GET /api/v1/weather`, `GET /api/v1/layers/metadata`, and `GET /api/v1/layers/{name}.png`.

Expert API: `POST /api/v2/expert/auth/login`, `POST /api/v2/expert/auth/logout`, `GET /api/v2/expert/auth/me`, `GET /api/v2/expert/analyses`, `GET /api/v2/expert/analyses/summary`, `GET /api/v2/expert/analyses/{analysis_id}`, review create/update/history routes, and server-side notes routes. The analysis list supports status, confidence, crop, priority, salinity, waterlogging, date, and search filters with pagination.

SQLite initialization is additive: existing farmer requests/results remain in place while the expert tables are created and old requests receive a `not_reviewed` status.
