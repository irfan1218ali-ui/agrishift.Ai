# Landsat source placement and provenance

The processed feature set uses Landsat 9 scene `LC09_L2SP_151043_20250930_20251001_02_T1` acquired 2025-09-30. The raw product is intentionally excluded from this repository; see `data/manifests/landsat-files.csv` and `docs/data/landsat-validation-report.md` for its validated file inventory and checksums.

The earlier Landsat 8 expectation, `LC08_L2SP_151043_20250922_20250930_02_T1`, was not found and is superseded. Do not rename the original provider files or place unrelated imagery in this folder.

- Owner: Data engineering
- Inputs: Original USGS Landsat 9 Collection 2 Level-2 product bundle.
- Outputs: Source manifest and downstream derived features/layers.
- Must not store: Credentials, edited provider originals, or unverified field measurements.
