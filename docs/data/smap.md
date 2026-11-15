# NASA SMAP

- **Product:** SPL4SMGP V008 Level-4 Geophysical Data.
- **Observed source:** `Downloads/smap dataset/`; original files remain outside the repository and were not edited or copied.
- **Assets:** 56 surface and 56 root-zone GeoTIFFs, each with 5 × 6 cells, EPSG:4326, 30 valid cells, NoData -9999, units m³/m³, and roughly 0.078° cell spacing.
- **Dates:** 2026-10-01 01:30 UTC through 2026-10-07 22:30 UTC, 3-hour cadence.
- **Observed 56-snapshot spatial means:** surface moisture 0.072452 m³/m³; root-zone moisture 0.141349 m³/m³.
- **Role:** coarse regional context only, roughly 9 km; never an exact field sensor measurement and never sufficient by itself for crop scoring.
- **Validation and checksums:** `data/manifests/smap-files.csv`.
- **Limitations:** source period is not aligned with the supplied GPM window. Processing results are detailed in `docs/data/source-inventory.md`.
