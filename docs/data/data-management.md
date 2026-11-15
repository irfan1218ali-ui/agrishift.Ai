# Data management

## Four zones

- `raw/`: original provider downloads/API payloads, immutable, original names retained, SHA-256 recorded.
- `interim/`: clipped, reprojected, quality-filtered or harmonized intermediate assets reproducible from raw.
- `processed/`: validated indices, temporal summaries, terrain derivatives, map-ready rasters and tables.
- `model-ready/`: validated feature tables, training patches, labels, manifests and versioned feature schemas.

Scientific data zones are excluded from Git. Keep sanitized instructions, catalogs, manifests, schemas and small reviewed samples. Never commit credentials or sensitive API dumps.

## Naming and original files

New dataset folders use `<PROVIDER>_<PRODUCT>_<VERSION>_<AREA>_<START>_<END>/` where known. Preserve provider filenames in `original/`; extracted components go under `extracted/`; request/product metadata under `metadata/`; hashes under `checksums/`; file-level records in `manifest.csv`. This restructure does not move or rename any existing source files.

## Manifest and lineage

Record dataset/asset ID, source path/reference, original filename, size, checksum, provider/product/version, variable, observation/retrieval UTC time, CRS, transform/resolution, NoData, scale/offset, QA status, license reference and validation status. Do not fill measurements until the actual file is validated.

Lineage: raw source + checksum → script/config version → interim asset → processed indicator/checksum → model-ready dataset/feature schema → model version/metrics → prediction/explanation. Corrections create new immutable versions; never overwrite originals. API samples are sanitized and labeled by endpoint/environment.
