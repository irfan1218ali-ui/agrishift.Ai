# Coding standards

## TypeScript

Enable strict mode; use domain types and Zod at external boundaries; check DTOs against OpenAPI; avoid `any`; isolate map library types; use server components by default; handle loading, empty, partial coverage, stale, and error states. Never embed secrets in `NEXT_PUBLIC_*`.

## Python

Python 3.11+, public-function annotations, Pydantic v2 at IO boundaries, SQLAlchemy 2 patterns, Ruff, bounded async IO, injected HTTP clients, and timezone-aware UTC timestamps. Domain services avoid web/provider SDK concerns. Avoid unbounded raster loads; use windows/chunks and document CRS/NoData semantics.

## Tests

Unit tests for pure rules; schema/contract tests at boundaries; adapter tests with injected fakes; spatial fixtures with known CRS/NoData; integration tests against disposable PostGIS/Redis; browser E2E for critical flows. Never depend on live provider accounts or real farmer data.

## Logging and errors

Structured logs include request/job IDs, provider/model/processing versions and elapsed time. Redact credentials, tokens, precise coordinates, and personal data. Normalize errors to stable code, readable message, request ID, and safe details. Never leak upstream response bodies. Retry only transient idempotent work with bounded backoff/rate-limit awareness.

## API design

Prefix `/api/v1`; validate inputs; use UTC ISO-8601 instants, UUID IDs, GeoJSON interchange, cursor pagination, documented filters, and async job IDs/status. Preserve compatibility within a version and publish deprecation windows.
