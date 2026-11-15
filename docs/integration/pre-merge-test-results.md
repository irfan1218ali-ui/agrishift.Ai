# Step 1 pre-merge verification

Captured before merging Step 2A on 2026-11-15 (Asia/Karachi), Python 3.11.9.

| Check | Result |
|---|---|
| `python -m pytest -q` | 69 passed, 1 third-party AnyIO/pytest deprecation warning, 14.96 seconds |
| `ruff check .` | Passed |
| `python -m compileall -q -x '\\.venv' .` | Passed |
| Backend/web smoke evidence | The prior Step 1 final verification records 200 responses for health, OpenAPI, the static page and data endpoints; demo analysis returned three distinct options and persisted/reloaded the result. See `docs/audit/test-results-step-1-final.md`. |
| Repeat HTTP smoke in this turn | The Uvicorn launcher started, but the sandbox denied loopback sockets with “An attempt was made to access a socket in a way forbidden by its access permissions.” No product/API error was observed. |

The project has no frontend-specific test runner or package manifest; the farmer UI is the existing static page served by FastAPI. The existing API tests exercise route and service behavior.

This is the Step 1 baseline before the Step 2A merge and application integration changes.
