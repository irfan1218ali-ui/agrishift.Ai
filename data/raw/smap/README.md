# NASA SMAP raw placement

The inspected source files remain in the user's `Downloads/smap dataset/` folder; they were not moved, renamed, edited, or copied here. The manifest stores relocatable external names and checksums. Validation found 56 surface and 56 root-zone SPL4SMGP V008 GeoTIFF snapshots for 2026-10-01 through 2026-10-07. Measured regional summaries and their limitations are in `docs/data/source-inventory.md`.

Do not move or edit the original files as part of ordinary application setup. The derived summary is stored locally under ignored `data/processed/model-features/` and is context-only, not field moisture.

## Handling

- Owner: Data engineering
- Inputs: User-supplied SPL4SMGP GeoTIFF snapshots listed in `data/manifests/smap-files.csv`.
- Outputs: Checksummed source inventory and regional context summary.
- Must not store: Modified originals, credentials, or field-level claims from coarse regional cells.
