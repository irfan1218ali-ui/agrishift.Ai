# Observed source inventory and validation

Inventory date: 2026-11-15. Paths below are relative to the project except the SMAP source, which was found under `Downloads/smap dataset/`. Raw assets were read for validation and not edited in place. Checksums are recorded in `data/manifests/`.

## Summary

| Source | Assets found | Observed coverage | Validation outcome | MVP role |
|---|---:|---|---|---|
| NASA SMAP SPL4SMGP V008 | 112 GeoTIFFs: 56 surface, 56 root-zone | 2026-10-01 to 2026-10-07, every 3 hours | Metadata, CRS, valid pixels, ranges, units, and checksums recorded | 7-day regional context only |
| NASA GPM IMERG Final Run V07 | One NetCDF and one matching GeoTIFF | Time-averaged daily rate over 2025-09-01 to 2025-09-07 | Units and raster/grid compatibility checked | Regional mean-rate context only |
| Landsat 8/9 C2 L2 | Scene folder and manifest, no imagery or MTL | Expected acquisition 2025-09-22 | Required files absent; not validated | No NDVI/NDMI/BSI/ST or cloud fraction available |
| NASA SRTMGL1 V003 | DEM and NUMNC rasters | Hyderabad region, nominal 30 m | CRS, dimensions, bounds, units, NoData and checksum recorded; slope derived | Elevation and slope; no drainage diagnosis |
| NASA POWER daily point CSV | One CSV | 2015-01-01 to 2025-12-31 LST, coordinate 25.396°N, 68.3578°E | Header, required variables, units, fill values and dates parsed | Regional historical climate summary |
| Meteomatics | One saved JSON response (four parameters) | Generated 2026-11-15 07:20:04 UTC; hourly series through 2026-11-22 | Timestamp/parameter parse and hourly-to-daily logic checked | Saved forecast sample in demo only; not long-term score input |

## SMAP SPL4SMGP V008

Source was found in the user's Downloads folder, outside the project. Surface and root-zone folders each contain 56 rasters at 3-hour intervals across seven days. Each raster has 5 rows by 6 columns, EPSG:4326, bounds approximately `[68.1351, 25.1804, 68.6028, 25.5702]`, cell size approximately `0.07796°`, units `m³/m³`, NoData `-9999`, and 30 valid cells.

| Variable | Space-time mean | Minimum observed cell | Maximum observed cell | Valid pixel observations |
|---|---:|---:|---:|---:|
| Surface soil moisture | 0.072452 m³/m³ | 0.041956 | 0.097912 | 1,680 |
| Root-zone soil moisture | 0.141349 m³/m³ | 0.128759 | 0.147164 | 1,680 |

These means average valid pixels over all snapshots; they are not a point-in-time field reading and not a farmer's field moisture measurement.

## GPM IMERG Final Run V07

The supplied product is a weekly time-averaged daily precipitation-rate map, not a daily time series. Its 12 valid grid cells use EPSG:4326 at approximately `0.1°`, with bounds about `[68.2, 25.2, 68.5, 25.6]` and units `mm/day`.

| Summary | Observed value |
|---|---:|
| Mean daily rate over supplied grid | 5.4650 mm/day |
| Minimum grid-cell mean daily rate | 4.0500 mm/day |
| Maximum grid-cell mean daily rate | 6.7629 mm/day |
| Observation period | 2025-09-01 00:00 UTC through 2025-09-07 23:59 UTC |

The supplied aggregate cannot yield total rainfall, rainy-day count, or maximum daily rainfall. Those fields remain unavailable, not estimated.

## Landsat C2 Level-2

The expected scene is `LC08_L2SP_151043_20250922_20250930_02_T1`. The local scene folder contains a manifest and README instructions but no original, extracted, or metadata source files. Missing required assets are `SR_B2`–`SR_B7`, `ST_B10`, `QA_PIXEL`, and the MTL file. The validation manifest contains zero scene assets. Consequently, no Landsat index, surface temperature, cloud-free fraction, multi-point feature row, overlay, or K-Means training input was produced.

The guarded feature builder reads scale/offset coefficients from the MTL, masks QA_PIXEL bits 0–5, and writes `data/features/features.json` only after at least 20 complete Landsat/SRTM points are available. It does not use the supplied placeholder row.

## SRTM terrain

The actual DEM is `data/raw/terrain/NASA_SRTM_or_NASADEM_Hyderabad/SRTMGL1_NC.003_SRTMGL1_DEM_doy2000042000000_aid0001.tif`. It has 1,261 × 1,261 cells, EPSG:4326, approximate bounds `[68.199861, 25.199861, 68.550139, 25.550139]`, about 30 m ground spacing, elevation in metres, and NoData `-32768`. The companion NUMNC has 1,261 × 1,261 cells, NoData `0`, and values 1–204; it was not treated as terrain height.

The real DEM was reprojected to UTM zone 42N for slope derivation, then the slope raster was reprojected to the DEM grid. Local generated output has 1,582,752 valid pixels, slope range 0–28.8742°, mean 2.2768°, and display scale p02–p98 of 0.4404–6.4861°. The runtime PNG is `data/layers/slope.png`; bounds and provenance are in `data/layers/metadata.json`. Slope is not a drainage or waterlogging diagnosis. The terrain product date in metadata is decoded from the source product's day-of-year filename.

## NASA POWER

The saved CSV is `data/api-samples/nasa-power/POWER_Point_Daily_20150101_20251231_025d40N_068d36E_LST (1).csv`. Its header gives a 0.5° × 0.625° MERRA-2 region, coordinates 25.396°N, 68.3578°E, elevation context 92.45 m, and daily data from 2015-01-01 through 2025-12-31 in local solar time. The missing marker is `-999`. The parser reads T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, RH2M, WS2M, and ALLSKY_SFC_SW_DWN.

Monthly statistics below use the supplied 11-year daily series. “Heat days” is the average number of days in each calendar month with daily T2M_MAX ≥ 40°C, averaged across years. Monthly rainfall is the average month total. Solar radiation uses the source header unit MJ/m²/day.

| Month | Mean TMax °C | Mean TMin °C | Average heat days ≥40°C | Mean rainfall mm/month |
|---|---:|---:|---:|---:|
| Jan | 25.407 | 10.270 | 0.000 | 5.743 |
| Feb | 30.156 | 13.701 | 0.000 | 1.668 |
| Mar | 34.979 | 18.663 | 3.273 | 2.058 |
| Apr | 40.364 | 23.293 | 17.909 | 3.994 |
| May | 42.514 | 26.115 | 27.091 | 57.830 |
| Jun | 41.211 | 28.104 | 21.818 | 17.745 |
| Jul | 38.460 | 28.078 | 9.545 | 87.125 |
| Aug | 36.726 | 26.333 | 1.545 | 108.476 |
| Sep | 37.296 | 24.965 | 3.455 | 27.153 |
| Oct | 36.815 | 21.858 | 3.182 | 1.680 |
| Nov | 31.786 | 16.916 | 0.000 | 1.594 |
| Dec | 27.001 | 11.796 | 0.000 | 2.579 |

Whole-period means: RH2M 46.843%, WS2M 3.270 m/s, ALLSKY_SFC_SW_DWN 19.656 MJ/m²/day. These are grid context at coarse regional resolution, not field measurements.

## Meteomatics

The saved hourly sample has the four requested parameters and is explicitly identified as a sample. A sanitized distributable copy omits the account identifier. The parser calculates daily summaries, a `valid_from`/`valid_until` period, and whether the sample has expired. Real mode does not use it.

## Artifacts actually produced

- `data/manifests/{smap-files,gpm-files,terrain-files,landsat-files,power-files,meteomatics-files}.csv`
- `data/processed/model-features/regional_context.json` (ignored local artifact; API exposes only a safe summary)
- `data/processed/terrain/slope_deg.tif` (ignored local derived raster)
- `data/layers/slope.png` and `data/layers/metadata.json`
- `data/api-samples/meteomatics/demo_sample.example.json` (sanitized saved-response copy)

No `features.json`, NDVI/NDMI/BSI overlays, clustered feature JSON, joblib model, cluster profiles, or K-Means metrics exist.
