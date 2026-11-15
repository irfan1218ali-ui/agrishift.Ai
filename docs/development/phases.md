# Seven development phases

Each phase requires a reviewed rollback plan and does not authorize deployment by itself.

| Phase | Objectives and inputs | Deliverables | Tests and acceptance | Dependencies and rollback |
|---|---|---|---|---|
| 1 Foundation | Toolchain, architecture, configuration, service boundaries | Compose, DB foundation, health/readiness, CI, logging, secret handling | Unit/contract checks, migration smoke test; local stack starts, readiness reports dependencies, CI gates work | Reviewed foundation; revert image/config, preserve DB backups, forward-fix migrations |
| 2 Identity and fields | Consent, user needs, roles, geometry policy | Auth, farms/fields, PostGIS boundaries, field map/drawing | Authz/tenant isolation, geometry validity/area, accessibility; no cross-farm disclosure | Phase 1; disable feature/roll back API, restore tested backup |
| 3 Data integrations | Provider terms, auth, datasets, budgets | Prioritized NASA/satellite/climate/weather adapters | Safe-fixture contract tests, timeout/retry/rate-limit/error tests; provenance/license complete | Phase 1 contracts; disable adapter/credential, retain immutable raw data |
| 4 Geospatial processing | Accepted providers and processing specs | QA pipeline, COG, map layers, zonal summaries | CRS/mask/NoData/resolution/lineage checks; no false precision | Phase 3; pin prior pipeline and retain derived assets |
| 5 ML/DL | Reviewed labels, splits, feature definitions | Training/inference/evaluation/explainability for segmentation, suitability, risk | Leakage controls, spatial/temporal holdouts, calibration, model card/expert review; refuse out-of-domain output | Phases 3–4; revert registry pointer and inference image |
| 6 Agronomy and rotation | Verified crop knowledge, priorities, expert governance | Knowledge base, constraints, generator/ranker, explanations | Constraint tests, agronomist review, sensitivity/missing-evidence tests; no unsupported recommendation | Phases 2–5; disable ranking, return safe informational state |
| 7 Product and operations | Usability research, support, SLO/privacy decisions | Dashboard, reports, QA, production operations/monitoring | E2E/security/accessibility/performance/restore exercises; sign-off and rollback demonstrated | Phases 1–6; staged app/model/config rollback and incident response |

Rollback requirements: version APIs/schemas; deploy compatible changes; back up before destructive migrations; define retention/deletion separately. Stop queues and pause adapters safely. Never delete raw data during rollback. Roll back model and software versions independently. Name restoration authority and verify restore outside production.
