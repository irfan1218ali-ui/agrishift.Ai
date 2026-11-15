# Four team boundaries

These areas define ownership only; they do not assign people or workload. Shared contract changes require review from affected owners.

| Area | Owns | Inputs | Outputs | Required checks / reviewers |
|---|---|---|---|---|
| A — Frontend | `apps/web/`, `packages/ui/`, `packages/map-components/` | OpenAPI DTOs, map-layer contract, user flows | Accessible map/forms/charts and UX feedback | Type, component, contract and accessibility checks; Backend and Data/GIS review layer semantics |
| B — Backend | `apps/api/`, `services/` | Shared schemas, DB contracts, asset/processing/model outcomes | Versioned APIs, authorization, jobs and orchestration | Unit/API/adapter contract/authz checks; Frontend and Database/DevOps review; Data/GIS reviews source behavior |
| C — Database and DevOps | `database/`, `infrastructure/`, Compose, CI | Entity/API/job needs, deployment/privacy requirements | Migrations, local runtime, backup and operational controls | Migration/restore/compose/CI checks; Backend and Data/GIS review lineage |
| D — Data, GIS and AI | `data/`, `geospatial/`, `ml/`, `scripts/data/` | Source metadata, field geometry, contracts and reviewed labels | Validated catalogs/assets/features, manifests, model metadata and uncertainty | Checksum/CRS/QA/NoData/lineage/evaluation checks; Backend and Database review schemas |

Shared contracts include API/OpenAPI, provider normalized models, data manifests, map-layer schema, feature schema and crop-knowledge schema. Do not edit another area's implementation without its reviewer.
