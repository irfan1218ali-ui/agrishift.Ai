# API contract summary

The running FastAPI service exposes public farmer routes under `/api/v1` and the authenticated single-EXPERT portal under `/api/v2/expert`. OpenAPI is available from the running service at `/openapi.json`.

## Public farmer routes

`GET /api/v1/health`, `GET /api/v1/crops`, `POST /api/v1/analyze`, `GET /api/v1/analyses/{analysis_id}`, `GET /api/v1/context`, `GET /api/v1/weather`, `GET /api/v1/layers/metadata`, and `GET /api/v1/layers/{ndvi|ndmi|bsi|slope}.png`.

An accepted farmer analysis is persisted in SQLite. The retrieval response includes `review_status` so the public results page can show the saved expert decision. Farmer routes do not require authentication.

## Expert routes

- Auth: `POST /api/v2/expert/auth/login`, `POST /api/v2/expert/auth/logout`, `GET /api/v2/expert/auth/me`.
- Analysis list/detail: `GET /api/v2/expert/analyses`, `GET /api/v2/expert/analyses/summary`, `GET /api/v2/expert/analyses/{analysis_id}`.
- Reviews: `POST /api/v2/expert/analyses/{analysis_id}/reviews`, `PATCH /api/v2/expert/reviews/{review_id}`, `GET /api/v2/expert/analyses/{analysis_id}/reviews`.
- Notes: `GET /api/v2/expert/analyses/{analysis_id}/notes`, `PUT /api/v2/expert/analyses/{analysis_id}/notes`.

The analysis list accepts `status`, `confidence` (`low`, `medium`, `high`), `previous_crop`, `priority`, `salinity`, `waterlogging`, inclusive `date_from`/`date_to`, `search`, `page`, and `page_size`. The response contains `items`, `total`, `page`, `page_size`, and `total_pages`.

Review decisions are `approved`, `approved_with_changes`, `needs_more_information`, and `unsuitable`. Creating a review without a decision sets `under_review`. Score components are saved with `value`, `reason`, `rule_id`, `verified`, and `source`.

## Authentication and errors

Login verifies the single EXPERT account configured by `EXPERT_EMAIL`, `EXPERT_PASSWORD_HASH`, and `EXPERT_SESSION_SECRET`. The browser receives an eight-hour signed Secure, HttpOnly, SameSite=Strict cookie. Expert responses are marked `Cache-Control: no-store`.

Errors use `{"error":{"code":"...","message":"...","request_id":"...","details":{}}}`. Authentication, authorization, not-found, validation, and service-unavailable responses use HTTP 401, 403, 404, 422, and 503 respectively. The `X-Request-ID` header matches the envelope request ID.
