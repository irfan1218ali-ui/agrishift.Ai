# API contract conventions

All routes are rooted at `/api/v1`. OpenAPI schemas are generated from validated boundary models; examples show shapes only and contain no farmer/environmental observations.

## Example field create request

```json
{"farm_id":"uuid","name":"string","boundary":{"type":"Polygon","coordinates":"GeoJSON positions"},"crs":"EPSG:4326"}
```

## Example asynchronous processing response

```json
{"job_id":"uuid","status":"queued","created_at":"2026-01-01T00:00:00Z","request_id":"uuid"}
```

## Error envelope

```json
{"error":{"code":"ERROR_CODE","message":"Readable message","request_id":"uuid","details":{}}}
```

Use UUID identifiers, UTC ISO-8601 instants, documented inclusive date ranges, validated GeoJSON with explicit CRS, cursor pagination (`items`, `next_cursor`), and job states `queued`, `running`, `succeeded`, `failed`, `cancelled`. Prediction responses name model/dataset versions plus confidence and limitations.
