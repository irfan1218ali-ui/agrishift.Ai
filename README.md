# AgriShift AI

Farmer-centered crop-rotation decision support for NASA Space Apps Challenge “Field Shift: Adapting Farms with NASA Data.” It will let farmers compare their current rotation with alternatives and review evidence, risks, uncertainty, limitations, and local expert review requirements.

## Locked MVP sources

Only six sources are in the MVP: NASA SMAP, NASA GPM IMERG, USGS Landsat 8/9 Collection 2 Level-2, NASA SRTM/NASADEM, NASA POWER API, and Meteomatics Weather API. See [the six-source strategy](docs/architecture/six-source-strategy.md). Other candidate sources are listed as future, not MVP, in [excluded datasets](docs/future-enhancements/excluded-datasets.md).

## Current data status

- SMAP SPL4SMGP V008: located in `C:/Users/HP/Downloads/smap dataset`; validation pending.
- GPM IMERG GPM_3IMERGDF V07 Final Run: two files exist in `data/raw/gpm-imerg/`; not inspected or validated.
- Landsat scene LC08_L2SP_151043_20250922_20250930_02_T1: user reports downloaded or being organized; matching scene files were not located in the scanned project, Downloads, Desktop, or Documents folders.
- SRTM/NASADEM: not started. NASA POWER and Meteomatics API access: pending.

See [dataset catalog](data/catalog/datasets.csv), [status catalog](data/catalog/data-status.csv), and [data management](docs/data/data-management.md).

## Architecture

Next.js/TypeScript web, FastAPI/Python API, PostgreSQL/PostGIS, Redis/Celery for bounded async work, object storage for raster assets, and separate geospatial/ML modules. SMAP, GPM, Landsat and terrain adapters consume local files or later object-storage assets. NASA POWER and Meteomatics are the only active runtime external API adapters.

- `apps/web/`: map, forms, charts, API client.
- `apps/api/`: versioned REST API, services and six source adapters.
- `database/`: schema artifacts, migrations, diagrams and dictionary.
- `data/`: catalog, raw/interim/processed/model-ready zones, manifests and crop templates.
- `geospatial/`, `ml/`, `services/`: processing, model lifecycle and domain services.
- `docs/development/folder-ownership.md`: four ownership areas and PR contracts.

See the [expanded project tree](docs/architecture/repository-tree.md).

See the [expanded repository tree](docs/architecture/repository-tree.md).

## Limitations and workflow

Architecture stage only: no application feature implementation, provider calls, data processing, model training, predictions, recommendations, or migrations. Regional SMAP/GPM/POWER are context, not field measurements. Landsat needs QA_PIXEL and product scale/offset checks. Crop values require cited evidence and expert review. Keep original source data and credentials out of Git. See [team boundaries](docs/development/team-boundaries.md), [coding standards](docs/development/coding-standards.md), and [phases](docs/development/phases.md).

## Next steps

Review architecture, then allocate four ownership areas. Validate existing SMAP/GPM assets against product metadata and record only measured facts in manifests. This restructure does not reorganize original source files.
