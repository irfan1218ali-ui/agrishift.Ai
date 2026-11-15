# AgriShift AI — Scientific Source Inventory (Step 2A)

This document provides a comprehensive audit of all raw datasets, API responses, and metadata discovered for the AgriShift AI pilot study over the Hyderabad region, Sindh, Pakistan.

---

## 1. Summary of Scientific Data Assets

| Source ID | Provider | Mission / Service | Product & Version | Physical Location | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `landsat-c2-l2-hyderabad` | USGS / NASA | Landsat 9 OLI-2 / TIRS-2 | Landsat Collection 2 Level-2 (`LC09_L2SP_151043_20250930_20251001_02_T1`) | `data/raw/landsat/extracted/` | **VALIDATED** |
| `landsat-c2-l2-expected-scene` | USGS / NASA | Landsat 8 OLI / TIRS | Landsat Collection 2 Level-2 (`LC08_L2SP_151043_20250922_20250930_02_T1`) | Registered in legacy catalog | **MISSING** |
| `smap-spl4smgp-v008-hyderabad` | NASA | SMAP | SPL4SMGP V008 (L4 Global 3-hourly 9 km EASE-Grid) | `data/raw/smap/extracted/` | **VALIDATED** |
| `gpm-3imergdf-v07-hyderabad` | NASA / JAXA | GPM IMERG | GPM_3IMERGDF V07 Final Run (Daily 0.1° rate) | `data/raw/gpm-imerg/` | **VALIDATED** |
| `srtm-gl1-dem-hyderabad` | NASA / USGS | SRTM 1 Arc-Second | SRTMGL1 Version 003 (~30 m DEM) | `data/raw/terrain/NASA_SRTM_or_NASADEM_Hyderabad/` | **VALIDATED** |
| `nasa-power-daily-climate` | NASA POWER | POWER Project | Daily Climate (MERRA-2 & CERES SYN1deg) | `data/api-samples/nasa-power/` | **VALIDATED** |
| `meteomatics-hourly-weather` | Meteomatics | Weather API | Multi-parameter Hourly Forecast & History | `data/api-samples/meteomatics/` | **VALIDATED** |

---

## 2. Detailed Source Profiles

### 2.1 Landsat 9 Collection 2 Level-2 (Scene `LC09_L2SP_151043_20250930_20251001_02_T1`)
- **Provider**: USGS / NASA Earth Resources Observation and Science (EROS) Center.
- **Product & Processing Level**: Landsat Collection 2 Level-2 Science Product (L2SP), Tier 1.
- **Acquisition Date**: `2025-09-30T05:51:13.2784450Z`.
- **Spatial Coverage**: WRS-2 Path 151, Row 043 (UTM Zone 42N, EPSG:32642). Covers Hyderabad pilot bounding box `[68.20°E, 25.20°N, 68.55°E, 25.55°N]`.
- **Available Files**:
  - `LC09_L2SP_151043_20250930_20251001_02_T1_SR_B2.TIF` (Blue: 482 nm)
  - `LC09_L2SP_151043_20250930_20251001_02_T1_SR_B3.TIF` (Green: 561 nm)
  - `LC09_L2SP_151043_20250930_20251001_02_T1_SR_B4.TIF` (Red: 654 nm)
  - `LC09_L2SP_151043_20250930_20251001_02_T1_SR_B5.TIF` (NIR: 865 nm)
  - `LC09_L2SP_151043_20250930_20251001_02_T1_SR_B6.TIF` (SWIR 1: 1608 nm)
  - `LC09_L2SP_151043_20250930_20251001_02_T1_SR_B7.TIF` (SWIR 2: 2200 nm)
  - `LC09_L2SP_151043_20250930_20251001_02_T1_ST_B10.TIF` (Thermal: 10.9 µm)
  - `LC09_L2SP_151043_20250930_20251001_02_T1_QA_PIXEL.TIF` (Bit-packed quality flags)
  - `LC09_L2SP_151043_20250930_20251001_02_T1_MTL.json`, `.txt`, `.xml`
- **Scaling Equations**:
  - Surface Reflectance ($SR$): $SR = \text{DN} \times 0.0000275 - 0.2$
  - Surface Temperature ($ST$): $ST = \text{DN} \times 0.00341802 + 149.0$ (Kelvin); $T_{^{\circ}\text{C}} = ST - 273.15$
- **Discrepancy Note**: The starter repository catalog listed `LC08_L2SP_151043_20250922_20250930_02_T1` with status "user reports downloaded or being organized, local files not located". Physical scan confirmed the archive downloaded on machine is Landsat 9 `LC09_L2SP_151043_20250930_20251001_02_T1.tar` (same WRS-2 footprint, acquired 8 days later on 2025-09-30). LC08 is marked MISSING, while LC09 is validated and used.

### 2.2 NASA SMAP SPL4SMGP V008 (AppEEARS Export)
- **Provider**: NASA National Snow and Ice Data Center (NSIDC) DAAC.
- **Product**: SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture (SPL4SMGP V008).
- **Date Coverage**: 2026-10-01 to 2026-10-07 (7 days, 56 timesteps per variable).
- **Variables**:
  - `sm_surface`: Surface soil moisture ($0\text{--}5\text{ cm}$ layer) in volumetric fraction ($\text{m}^3/\text{m}^3$).
  - `sm_rootzone`: Root-zone soil moisture ($0\text{--}100\text{ cm}$ layer) in volumetric fraction ($\text{m}^3/\text{m}^3$).
- **Spatial Coverage & Resolution**: EPSG:4326 grid covering `[68.14°E, 25.18°N, 68.60°E, 25.57°N]`, pixel size ~0.08° (~9 km).
- **Limitation**: Coarse regional soil moisture context. Does not represent in-situ field sensor measurements.

### 2.3 NASA GPM IMERG Final Run V07
- **Provider**: NASA Goddard Earth Sciences Data and Information Services Center (GES DISC).
- **Product**: `GPM_3IMERGDF` V07 Final Run Daily Mean Precipitation Rate.
- **Date Coverage**: 2025-09-01 through 2025-09-07 (accumulated time average over 7-day period).
- **Files**:
  - `GIOVANNI-g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.tif`
  - `g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.nc`
- **Units**: $\text{mm}/\text{day}$.
- **Resolution**: $0.1^\circ \times 0.1^\circ$ (~10 km), 4 rows $\times$ 3 columns.
- **Limitation**: Regional satellite precipitation estimate; not an individual farm rain gauge.

### 2.4 NASA SRTM 1 Arc-Second DEM
- **Provider**: NASA / USGS LP DAAC.
- **Product**: SRTMGL1 Version 003 Global 1 arc-second DEM.
- **Files**:
  - `SRTMGL1_NC.003_SRTMGL1_DEM_doy2000042000000_aid0001.tif` (Elevation in meters above sea level)
  - `SRTMGL1_NUMNC.003_SRTMGL1_NUM_doy2000042000000_aid0001.tif` (Number of source scenes/quality mask)
- **Coverage**: Bounds `[68.20°E, 25.20°N, 68.55°E, 25.55°N]`, grid shape $1261 \times 1261$ pixels, resolution ~30 m.

### 2.5 NASA POWER Daily Climate Data
- **Provider**: NASA Prediction of Worldwide Energy Resources (POWER) Project.
- **Product**: Daily Agroclimatology Point Data at $25.396^\circ\text{N}, 68.3578^\circ\text{E}$ (MERRA-2 assimilation & CERES satellite radiation).
- **File**: `POWER_Point_Daily_20150101_20251231_025d40N_068d36E_LST (1).csv`.
- **Date Coverage**: 2015-01-01 through 2025-12-31 (11 continuous years, 4,018 daily records).
- **Variables**: `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `WS2M`, `ALLSKY_SFC_SW_DWN`, `PRECTOTCORR`.

### 2.6 Meteomatics Weather API Response
- **Provider**: Meteomatics AG Weather API.
- **File**: `data/api-samples/meteomatics/json.json`.
- **Generated At**: `2026-11-15T07:20:04Z`.
- **Location**: $25.396628^\circ\text{N}, 68.357436^\circ\text{E}$.
- **Parameters**: `precip_1h:mm`, `relative_humidity_2m:p`, `wind_speed_10m:ms`, `t_2m:C`.
- **Timesteps**: 169 hourly intervals from `2026-11-15T07:00:00Z` to `2026-11-22T07:00:00Z`.
