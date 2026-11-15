# System overview

```mermaid
flowchart LR
  Farmer[Farmer / agronomist] --> Web[Next.js web and MapLibre]
  Web --> API[FastAPI /api/v1]
  API --> Domain[Application and rotation services]
  Domain --> DB[(PostgreSQL + PostGIS)]
  Domain --> Jobs[Redis and Celery jobs]
  Jobs --> Workers[Provider, GIS and inference workers]
  Workers --> Sources[SMAP / GPM / Landsat / terrain files]
  Workers --> APIs[NASA POWER / Meteomatics]
  Workers --> Storage[Object storage and COG assets]
  Workers --> Registry[Versioned model registry]
  API --> Tiles[Map tile service]
  Tiles --> Storage
```

## Runtime boundaries

Frontend owns map interaction, forms, charts, and presentation. The API validates/authorizes requests, coordinates services, and publishes stable contracts. PostgreSQL/PostGIS stores identity, field geometries, catalog/asset metadata, job/prediction/rotation records and audit events; raster binaries stay in file/object storage. Redis/Celery handles bounded asynchronous work. GIS modules validate and derive source-aligned assets. ML modules version datasets, features, models, metrics and explanations. Provider adapters are limited to the six locked MVP sources.

## Data flow

Farmer field/history → catalog and coverage lookup → local/object asset or approved API request → source QA → interim processing → validated processed indicators → model-ready features → versioned inference → agronomic hard constraints and rotation ranking → evidence and limitations → map/dashboard/report. Results retain source, observation date, quality, scale, processing version, model version and review state.

## Team boundaries

Four ownership areas cover web/map, API/services, database/infrastructure, and data/GIS/AI. Shared API, layer, dataset, feature and crop schemas are reviewed by affected owners. See `docs/development/folder-ownership.md`.
