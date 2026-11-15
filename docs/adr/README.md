# Architecture decision records

Accepted choices for the current six-source foundation:

1. [Six-source MVP scope](0016-six-source-mvp.md)
2. [Monorepo](0001-monorepo.md)
3. [Raw/interim/processed/model-ready zones](0008-data-zones.md)
4. [Regional versus field scale](0009-resolution-policy.md)
5. [Landsat imagery](0017-landsat-field-imagery.md)
6. [NASA POWER historical climate](0018-nasa-power-climate.md)
7. [Meteomatics forecasts](0019-meteomatics-weather.md)
8. [PostgreSQL/PostGIS](0004-postgresql-postgis.md)
9. [MapLibre GL JS](0006-maplibre.md)
10. [FastAPI and source adapters](0003-fastapi-backend.md), [six-source adapters](0007-provider-adapters.md)
11. [Model versioning](0010-model-registry.md)
12. [No fabricated data](0015-no-fake-data.md)

Additional accepted decisions cover Redis/Celery, UUID/UTC, API versioning, COG/tile delivery and Azure as a future production target. Superseding decisions should update this index.

Owner: Shared architecture reviewers. Inputs: reviewed technical constraints and product requirements. Outputs: accepted rationale and implementation constraints. Must not store: credentials, private farmer records, or raw scientific data.
