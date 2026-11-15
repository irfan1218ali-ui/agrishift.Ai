# Folder ownership and collaboration contract

No personal names or workloads are assigned. Ownership areas match [team boundaries](team-boundaries.md).

| Area | Owned folders | Allowed changes | Restricted changes | Inputs → outputs | Required checks | PR reviewers |
|---|---|---|---|---|---|---|
| A — Frontend | `apps/web/`, `packages/ui/`, `packages/map-components/` | UI, map, forms, charts, API client | No provider secrets, ingestion, DB migrations or GIS processing | OpenAPI/layer contracts → farmer-facing views and UX feedback | Type/lint/component/accessibility/contract checks | Backend; Data/GIS for layer semantics |
| B — Backend | `apps/api/`, `services/` | Routes, authorization, jobs, six adapters, orchestration | No raw-file rewrite, frontend layout or unreviewed migrations | Shared schemas and DB/GIS/model services → versioned API and jobs | Unit/API/adapter/authz/retry/error contract checks | Frontend; Database/DevOps; Data/GIS on source behavior |
| C — Database and DevOps | `database/`, `infrastructure/`, `docker-compose.yml`, CI workflows | Schemas, migrations, local services, backups, monitoring and CI | No raster binaries in DB, secrets, destructive migration without backup | Entity/job needs and runtime requirements → persistence and operations | Migration/restore/compose/CI checks | Backend; Data/GIS for lineage |
| D — Data, GIS and AI | `data/`, `geospatial/`, `ml/`, `scripts/data/` | Catalogs/manifests, validation, processing, features and model lifecycle | No edit of source originals, unsupported crop values, or fake labels | Source metadata/field boundary → validated assets/features/versioned predictions | Checksums/CRS/QA/NoData/lineage/spatial evaluation checks | Backend; Database/DevOps; agronomic reviewer where relevant |

## Pull request requirements

Keep PRs focused, preserve source data, document migrations and rollback, update shared schemas and catalog status only with evidence, and include boundary-specific checks. Report any data files added (normally none). No credentials, private farmer data, or raw scientific assets in PRs. Cross-area changes request an owner review from each affected area.
