# Known limitations and release status

## Data status

- The active source is Landsat 9 scene `LC09_L2SP_151043_20250930_20251001_02_T1` acquired 2025-09-30. The earlier LC08 expectation is superseded.
- Step 2A produced 149 real pilot feature points, four map overlays, and K-Means artifacts. Raw scientific inputs remain excluded from the shareable package.
- SMAP is approximately 9 km and uses 56 snapshots from 2026-10-01 through 2026-10-07; it is regional context and is offset from the Landsat date.
- GPM is a 12-cell weekly time-averaged daily rate map from 2025-09-01 through 2025-09-07. It does not provide daily totals, rainy-day counts, or maximum daily rainfall.
- NASA POWER is a coarse regional grid summary from 2015 through 2025.
- SRTM slope and relative low-lying terrain indicators do not diagnose drainage or flood risk. Local drainage and field inspection are required.
- Meteomatics data is a time-bound saved response unless a live request succeeds; a saved response is never labeled live.

## Model and agronomy limits

- K-Means describes neutral environmental groupings. It does not directly rank crops or establish crop health, disease, yield, or crop suitability.
- Crop rules are not locally verified. Unverified constraints are soft penalties and require agronomist review.
- The explicit demo feature row contains placeholder values and must not inform farm decisions.

## Verification limits

- Full browser visual/console QA was unavailable in this run because the sandbox blocked loopback socket access. Automated API/client tests and source checks are documented in `docs/integration/qa-results.md`.
