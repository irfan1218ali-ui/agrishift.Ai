# Known limitations

## Release-blocking data gaps

- The expected Landsat 8 Collection 2 Level-2 scene folder has no SR_B2–SR_B7, ST_B10, QA_PIXEL, or MTL data.
- `data/features/features.json` is absent, so real analysis and real features cannot be served.
- The K-Means trainer has not run. There are no artifacts, metrics, cluster profiles, or cluster labels.

## Available-data limits

- SMAP is 5×6 coarse regional coverage, averaged across 56 snapshots per soil-moisture layer from 2026-10-01 through 2026-10-07.
- GPM is a 12-cell weekly time-averaged daily precipitation-rate map from 2025-09-01 through 2025-09-07. It does not provide daily totals, rainy-day count, maximum daily precipitation, or weekly total.
- SMAP and GPM dates do not align.
- NASA POWER represents one coarse regional point/grid from 2015 through 2025.
- SRTM slope provides terrain context only and cannot diagnose waterlogging or drainage.
- Meteomatics credentials are absent from the shared configuration; the saved response is demo-only and expires.

## Model and agronomy limits

- Crop rules are not locally verified. Unverified thresholds are soft penalties and require agronomist review.
- Environmental clustering cannot establish crop health, disease, yield, or crop suitability.
- The supplied demo feature row is placeholder data. Do not use its recommendation output for farm decisions.

## Verification limits

- Browser console and visual UI automation were not completed because the computer-use policy helper could not safely identify the browser URL. Local API and frontend HTTP smoke checks passed.
- Formula tests verify mathematical transformations but do not replace running real Landsat rasters through the pipeline.
