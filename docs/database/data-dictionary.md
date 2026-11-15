# Database data dictionary (proposed)

| Entity | Purpose / key relationships |
|---|---|
| users | Identity, preferences, consent; membership in farms |
| farms | Tenant container, locale and ownership |
| fields | Farm-linked operational metadata |
| field_boundaries | Versioned PostGIS polygons and effective dates |
| soil_observations | Field-linked lab/field values with method, units, source, date |
| crop_profiles | Curated crop identity and evidence reference |
| crop_history | Field-season crop events and provenance |
| crop_compatibility | Evidence-backed predecessor/family constraints |
| farmer_priorities | Versioned preferences/constraints with consent |
| dataset_catalog | Product/version/variables/licenses/resolution |
| provider_status | Provider health observations and times |
| earth_observations | Normalized observation metadata |
| raster_assets | Object URI, footprint, CRS, scale, checksum, lineage |
| weather_forecasts | Provider, issue/valid times, coverage, variables |
| processing_jobs | Idempotent status, config/version, errors and times |
| model_registry | Immutable versions, schema, metrics, checksum |
| model_predictions | Inputs/data/model versions, outputs, uncertainty, explanation |
| rotation_scenarios | Field, baseline/alternative, objective, version, review |
| rotation_scores | Criteria scores, evidence IDs, weights, uncertainty |
| rotation_explanations | Reasons, benefits, risks, limitations, sources |
| expert_reviews | Reviewer qualification, disposition, comments, times |
| farmer_feedback | Consent-aware response linked to scenario/version |
| reports | Generated report metadata, access scope, object URI |
| audit_logs | Actor, action, entity, request ID, time, safe summary |

Use server-generated UUID primary keys (UUIDv7 if consistently supported; UUIDv4 interoperates). Store timezone-aware UTC instants (`timestamptz`). Store field geometry as `geometry(MultiPolygon, 4326)` for interchange; transform to suitable projected CRS for area/distance and preserve source versions. Prefer boundary history over destructive updates. Index foreign keys, tenant IDs, time lookup columns, and GiST on geometries/footprints; add composites from measured query plans.

Soft-delete user-visible records with `deleted_at` when restoration/audit is required; define hard deletion/anonymization and object cleanup for privacy requests. Immutable assets/model versions use tombstones/retention metadata. Predictions/scenarios store model, dataset, feature-schema versions, and input asset IDs. Audit access, edits, export, reviews, and admin actions; never store secrets or full sensitive geometries in audit payloads.
