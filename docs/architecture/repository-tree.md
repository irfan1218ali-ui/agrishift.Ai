# Final project tree

Current AgriShift AI structure. `.git` is omitted; ignored source assets remain visible but are not tracked.

```text
agrishift-ai/
├── .editorconfig
├── .env.example
├── .gitattributes
├── .gitignore
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── api/
│   │   │   │   ├── README.md
│   │   │   │   └── v1/
│   │   │   │       └── README.md
│   │   │   ├── core/
│   │   │   │   └── README.md
│   │   │   ├── db/
│   │   │   │   └── README.md
│   │   │   ├── integrations/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── contracts.py
│   │   │   │   ├── gpm_imerg/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── adapter.py
│   │   │   │   │   └── README.md
│   │   │   │   ├── landsat/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── adapter.py
│   │   │   │   │   └── README.md
│   │   │   │   ├── meteomatics/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── adapter.py
│   │   │   │   │   └── README.md
│   │   │   │   ├── nasa_power/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── adapter.py
│   │   │   │   │   └── README.md
│   │   │   │   ├── README.md
│   │   │   │   ├── smap/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── adapter.py
│   │   │   │   │   └── README.md
│   │   │   │   └── terrain/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── adapter.py
│   │   │   │       └── README.md
│   │   │   ├── main.py
│   │   │   ├── middleware/
│   │   │   │   └── README.md
│   │   │   ├── models/
│   │   │   │   └── README.md
│   │   │   ├── README.md
│   │   │   ├── repositories/
│   │   │   │   └── README.md
│   │   │   ├── schemas/
│   │   │   │   ├── __init__.py
│   │   │   │   └── README.md
│   │   │   ├── services/
│   │   │   │   └── README.md
│   │   │   └── workers/
│   │   │       └── README.md
│   │   ├── Dockerfile
│   │   ├── migrations/
│   │   │   └── README.md
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── tests/
│   │       └── README.md
│   ├── README.md
│   └── web/
│       ├── public/
│       │   └── README.md
│       ├── README.md
│       ├── src/
│       │   ├── app/
│       │   │   └── README.md
│       │   ├── components/
│       │   │   └── README.md
│       │   ├── features/
│       │   │   └── README.md
│       │   ├── hooks/
│       │   │   └── README.md
│       │   ├── lib/
│       │   │   └── README.md
│       │   ├── README.md
│       │   ├── services/
│       │   │   └── README.md
│       │   ├── stores/
│       │   │   └── README.md
│       │   ├── styles/
│       │   │   └── README.md
│       │   └── types/
│       │       └── README.md
│       └── tests/
│           └── README.md
├── CONTRIBUTING.md
├── data/
│   ├── api-samples/
│   │   ├── meteomatics/
│   │   │   └── README.md
│   │   ├── nasa-power/
│   │   │   └── README.md
│   │   └── README.md
│   ├── boundaries/
│   │   ├── demo-fields/
│   │   │   └── README.md
│   │   ├── pakistan/
│   │   │   └── README.md
│   │   ├── README.md
│   │   └── sindh/
│   │       └── README.md
│   ├── catalog/
│   │   ├── api-endpoints.csv
│   │   ├── data-status.csv
│   │   ├── datasets.csv
│   │   ├── licenses.csv
│   │   ├── README.md
│   │   └── variables.csv
│   ├── crop-knowledge/
│   │   ├── crop-calendar.csv
│   │   ├── crop-compatibility.csv
│   │   ├── crops.csv
│   │   ├── pest-families.csv
│   │   ├── README.md
│   │   ├── soil-requirements.csv
│   │   └── water-requirements.csv
│   ├── interim/
│   │   ├── climate/
│   │   │   └── README.md
│   │   ├── landsat/
│   │   │   └── README.md
│   │   ├── rainfall/
│   │   │   └── README.md
│   │   ├── README.md
│   │   ├── smap/
│   │   │   └── README.md
│   │   └── terrain/
│   │       └── README.md
│   ├── labels/
│   │   ├── agronomist-ratings/
│   │   │   └── README.md
│   │   ├── crop-labels/
│   │   │   └── README.md
│   │   ├── field-observations/
│   │   │   └── README.md
│   │   ├── README.md
│   │   └── segmentation-masks/
│   │       └── README.md
│   ├── manifests/
│   │   ├── gpm-imerg-files.csv
│   │   ├── landsat-files.csv
│   │   ├── processed-files.csv
│   │   ├── raw-files.csv
│   │   ├── README.md
│   │   ├── smap-files-template.csv
│   │   ├── smap-files.csv
│   │   ├── terrain-files.csv
│   │   └── training-dataset.csv
│   ├── model-ready/
│   │   ├── feature-schemas/
│   │   │   └── README.md
│   │   ├── feature-tables/
│   │   │   └── README.md
│   │   ├── labels/
│   │   │   └── README.md
│   │   ├── README.md
│   │   └── training-patches/
│   │       └── README.md
│   ├── processed/
│   │   ├── climate/
│   │   │   └── README.md
│   │   ├── imagery/
│   │   │   └── README.md
│   │   ├── model-features/
│   │   │   └── README.md
│   │   ├── rainfall/
│   │   │   └── README.md
│   │   ├── README.md
│   │   ├── satellite-imagery/
│   │   │   └── README.md
│   │   ├── soil-moisture/
│   │   │   └── README.md
│   │   ├── surface-temperature/
│   │   │   └── README.md
│   │   ├── terrain/
│   │   │   └── README.md
│   │   └── vegetation-indices/
│   │       └── README.md
│   ├── raw/
│   │   ├── .gitignore
│   │   ├── gpm-imerg/
│   │   │   ├── g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.nc
│   │   │   ├── GIOVANNI-g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.tif
│   │   │   ├── NASA_GPM_3IMERGDF_V07_Hyderabad_2025-09-01_2025-09-07/
│   │   │   │   ├── checksums/
│   │   │   │   │   └── README.md
│   │   │   │   ├── extracted/
│   │   │   │   │   └── README.md
│   │   │   │   ├── manifest.csv
│   │   │   │   ├── metadata/
│   │   │   │   │   └── README.md
│   │   │   │   ├── original/
│   │   │   │   │   └── README.md
│   │   │   │   └── README.md
│   │   │   └── README.md
│   │   ├── landsat/
│   │   │   ├── README.md
│   │   │   └── USGS_Landsat_C2_L2_Hyderabad_2025-09-22/
│   │   │       ├── checksums/
│   │   │       │   └── README.md
│   │   │       ├── extracted/
│   │   │       │   └── README.md
│   │   │       ├── manifest.csv
│   │   │       ├── metadata/
│   │   │       │   └── README.md
│   │   │       ├── original/
│   │   │       │   └── README.md
│   │   │       └── README.md
│   │   ├── README.md
│   │   ├── smap/
│   │   │   ├── NASA_SMAP_SPL4SMGP_V008_Hyderabad_2026-10-01_2026-10-07/
│   │   │   │   ├── checksums/
│   │   │   │   │   └── README.md
│   │   │   │   ├── extracted/
│   │   │   │   │   └── README.md
│   │   │   │   ├── manifest.csv
│   │   │   │   ├── metadata/
│   │   │   │   │   └── README.md
│   │   │   │   ├── original/
│   │   │   │   │   └── README.md
│   │   │   │   └── README.md
│   │   │   └── README.md
│   │   └── terrain/
│   │       ├── NASA_SRTM_or_NASADEM_Hyderabad/
│   │       │   ├── checksums/
│   │       │   │   └── README.md
│   │       │   ├── extracted/
│   │       │   │   └── README.md
│   │       │   ├── manifest.csv
│   │       │   ├── metadata/
│   │       │   │   └── README.md
│   │       │   ├── original/
│   │       │   │   └── README.md
│   │       │   └── README.md
│   │       └── README.md
│   ├── README.md
│   └── samples/
│       ├── api-responses/
│       │   └── README.md
│       ├── demo-field/
│       │   └── README.md
│       ├── raster/
│       │   └── README.md
│       └── README.md
├── database/
│   ├── data-dictionary/
│   │   ├── entities.md
│   │   └── README.md
│   ├── diagrams/
│   │   ├── entity-relationship.md
│   │   └── README.md
│   ├── migrations/
│   │   └── README.md
│   ├── models/
│   │   └── README.md
│   ├── README.md
│   ├── schemas/
│   │   └── README.md
│   ├── seeds/
│   │   └── README.md
│   └── views/
│       └── README.md
├── docker-compose.yml
├── docs/
│   ├── adr/
│   │   ├── 0001-monorepo.md
│   │   ├── 0002-nextjs-frontend.md
│   │   ├── 0003-fastapi-backend.md
│   │   ├── 0004-postgresql-postgis.md
│   │   ├── 0005-redis-celery.md
│   │   ├── 0006-maplibre.md
│   │   ├── 0007-provider-adapters.md
│   │   ├── 0008-data-zones.md
│   │   ├── 0009-resolution-policy.md
│   │   ├── 0010-model-registry.md
│   │   ├── 0011-uuid-utc.md
│   │   ├── 0012-api-versioning.md
│   │   ├── 0013-cog-tiles.md
│   │   ├── 0014-azure-target.md
│   │   ├── 0015-no-fake-data.md
│   │   ├── 0016-six-source-mvp.md
│   │   ├── 0017-landsat-field-imagery.md
│   │   ├── 0018-nasa-power-climate.md
│   │   ├── 0019-meteomatics-weather.md
│   │   └── README.md
│   ├── api/
│   │   ├── contracts.md
│   │   ├── endpoints.md
│   │   └── README.md
│   ├── architecture/
│   │   ├── data-flow.md
│   │   ├── deployment.md
│   │   ├── map-architecture.md
│   │   ├── README.md
│   │   ├── repository-tree.md
│   │   ├── rotation-engine.md
│   │   ├── six-source-strategy.md
│   │   └── system-overview.md
│   ├── data/
│   │   ├── data-management.md
│   │   ├── dataset-catalog.md
│   │   ├── gpm-imerg.md
│   │   ├── landsat.md
│   │   ├── meteomatics.md
│   │   ├── nasa-power.md
│   │   ├── provider-architecture.md
│   │   ├── README.md
│   │   ├── smap.md
│   │   └── terrain.md
│   ├── database/
│   │   ├── data-dictionary.md
│   │   ├── erd.md
│   │   └── README.md
│   ├── deployment/
│   │   └── README.md
│   ├── development/
│   │   ├── coding-standards.md
│   │   ├── folder-ownership.md
│   │   ├── phases.md
│   │   ├── README.md
│   │   └── team-boundaries.md
│   ├── future-enhancements/
│   │   ├── excluded-datasets.md
│   │   ├── README.md
│   │   └── scope-cleanup.md
│   ├── geospatial/
│   │   ├── indicator-specs.md
│   │   ├── README.md
│   │   └── resolution-policy.md
│   ├── ml/
│   │   ├── model-architecture.md
│   │   └── README.md
│   ├── README.md
│   ├── schemas/
│   │   ├── contracts.schema.json
│   │   ├── geospatial-config.schema.json
│   │   └── README.md
│   └── security/
│       ├── data-privacy.md
│       └── README.md
├── geospatial/
│   ├── common/
│   │   └── README.md
│   ├── harmonization/
│   │   └── README.md
│   ├── indices/
│   │   └── README.md
│   ├── landsat/
│   │   └── README.md
│   ├── preprocessing/
│   │   ├── clipping/
│   │   │   └── README.md
│   │   ├── nodata/
│   │   │   └── README.md
│   │   ├── quality_masks/
│   │   │   └── README.md
│   │   ├── raster_io/
│   │   │   └── README.md
│   │   ├── README.md
│   │   └── reprojection/
│   │       └── README.md
│   ├── quality-control/
│   │   └── README.md
│   ├── rainfall/
│   │   └── README.md
│   ├── README.md
│   ├── soil-moisture/
│   │   └── README.md
│   ├── terrain/
│   │   └── README.md
│   ├── tests/
│   │   └── README.md
│   ├── tiling/
│   │   └── README.md
│   ├── validation/
│   │   └── README.md
│   └── zonal-statistics/
│       └── README.md
├── infrastructure/
│   ├── azure/
│   │   └── README.md
│   ├── backup/
│   │   └── README.md
│   ├── docker/
│   │   └── README.md
│   ├── github-actions/
│   │   └── README.md
│   ├── monitoring/
│   │   └── README.md
│   ├── README.md
│   └── storage/
│       └── README.md
├── LICENSE
├── Makefile
├── ml/
│   ├── common/
│   │   └── README.md
│   ├── crop-suitability/
│   │   └── README.md
│   ├── datasets/
│   │   └── README.md
│   ├── explainability/
│   │   └── README.md
│   ├── features/
│   │   └── README.md
│   ├── README.md
│   ├── registry/
│   │   └── README.md
│   ├── rotation-ranking/
│   │   └── README.md
│   ├── seasonal-risk/
│   │   └── README.md
│   ├── segmentation/
│   │   ├── configs/
│   │   │   └── README.md
│   │   ├── data/
│   │   │   └── README.md
│   │   ├── evaluation/
│   │   │   └── README.md
│   │   ├── inference/
│   │   │   └── README.md
│   │   ├── models/
│   │   │   └── README.md
│   │   ├── README.md
│   │   ├── tests/
│   │   │   └── README.md
│   │   └── training/
│   │       └── README.md
│   └── tests/
│       └── README.md
├── packages/
│   ├── crop-knowledge/
│   │   └── README.md
│   ├── map-components/
│   │   └── README.md
│   ├── README.md
│   ├── shared-config/
│   │   └── README.md
│   ├── shared-types/
│   │   └── README.md
│   └── ui/
│       └── README.md
├── README.md
├── scripts/
│   ├── data/
│   │   ├── README.md
│   │   ├── sample_meteomatics.py
│   │   ├── sample_nasa_power.py
│   │   ├── validate_gpm_imerg.py
│   │   ├── validate_landsat.py
│   │   ├── validate_smap.py
│   │   └── validate_terrain.py
│   ├── database/
│   │   └── README.md
│   ├── development/
│   │   └── README.md
│   ├── README.md
│   ├── setup/
│   │   └── README.md
│   └── validation/
│       ├── README.md
│       ├── validate_foundation.py
│       └── validate_six_sources.py
├── SECURITY.md
├── services/
│   ├── model-inference/
│   │   └── README.md
│   ├── notification-service/
│   │   └── README.md
│   ├── README.md
│   ├── report-service/
│   │   └── README.md
│   └── rotation-engine/
│       └── README.md
└── tests/
    ├── contract/
    │   └── README.md
    ├── end-to-end/
    │   └── README.md
    ├── integration/
    │   └── README.md
    └── README.md
```
