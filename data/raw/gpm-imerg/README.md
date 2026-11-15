# NASA GPM IMERG raw files

The original NetCDF and GeoTIFF exports retain their names and were not edited, renamed, or moved. Inspection identified the supplied product as a 7-day time-averaged daily precipitation-rate map (Final Run V07), not a daily series. See `data/manifests/gpm-files.csv` and `docs/data/source-inventory.md` for measured metadata and limitations.

Regional context only: the aggregate does not support daily totals, rainy-day counts, maximum daily precipitation, or a verified weekly sum. The original files are excluded from Git and the demo package.

## Handling

- Owner: Data engineering
- Inputs: The two user-supplied Giovanni exports named in `data/manifests/gpm-files.csv`.
- Outputs: A checksummed inventory and a regional mean-rate summary; no daily series is derived.
- Must not store: Credentials, unrelated source downloads, or unverified daily rainfall values.
