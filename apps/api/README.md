# API boundary

FastAPI service boundary for the six-source MVP. Route handlers under `/api/v1` validate and authorize requests, then delegate to services; repositories own persistence; `app/integrations/` has only SMAP, GPM IMERG, Landsat, terrain, NASA POWER and Meteomatics packages. Only POWER and Meteomatics are runtime external API adapters. Workers execute bounded jobs. Shared contracts make no network calls. Keep domain policy independent of HTTP/provider SDKs. No production endpoints are implemented yet.

Owner: Backend (Area B).
Inputs: OpenAPI contracts, database repositories, and normalized source metadata.
Outputs: versioned APIs, jobs, and normalized business outputs.
Must not store: credentials, unreviewed private farmer data, or unrelated scientific data.
