# AgriShift AI — Parallel Work Record (Step 2A)

## 1. Isolation & Workspace Details

- **Original Repository Path**: `C:\Users\HP\Documents\field shift\agrishift-ai`
- **Parallel Copy Path**: `C:\Users\HP\Documents\field shift\agrishift-step2-data`
- **Active Branch**: `hackathon/step-2-data-preparation`
- **Base Commit**: `0277e349f6ab1ea56df4ef0b5a4257bbcfab5149` (`chore: base project snapshot for parallel data preparation`)
- **Isolation Rationale**:
  The primary project directory (`agrishift-ai`) was on branch `hackathon/step-1-stabilize` with zero commits (unborn HEAD). Attempting `git worktree add` forced Git into `--orphan` mode, producing an empty worktree directory lacking all project files. Furthermore, sharing `.git` with Codex's active uncommitted workspace would cause index lock contention and metadata collision. An isolated project copy `agrishift-step2-data` with its own Git repository was initialized, ensuring zero interference with Codex's ongoing Step 1 stabilization.

## 2. Strict Ownership Boundaries

### Codex-Owned Folders & Files (Untouched)
- `apps/web/`
- `apps/api/`
- `services/rotation-engine/`
- `knowledge/crops.csv`
- `.env.example`
- `requirements.txt`
- `pyproject.toml`
- `package.json`
- `docker-compose.yml`
- `infrastructure/`
- `database/`
- `README.md`
- `README_STEP1.md`

### Antigravity-Owned Folders & Files (Step 2A Only)
- `data/`
- `geospatial/`
- `ml/clustering/`
- `scripts/data/`
- `docs/data/`
- `docs/geospatial/`
- `docs/ml/`
- `tests/data/`
- `tests/geospatial/`
- `tests/ml/`
- `requirements-data-ml.txt`

### Excluded Folders & Runtime Caches
- `.venv/`
- `.pytest_cache/`
- `.ruff_cache/`
- `node_modules/`
- `__pycache__/`

## 3. Discovered Dataset Locations

1. **Landsat 8/9 Collection 2 Level-2**:
   - Location: `C:\Users\HP\Downloads\LC09_L2SP_151043_20250930_20251001_02_T1.tar`
   - Scene: `LC09_L2SP_151043_20250930_20251001_02_T1` (Landsat 9 C2 L2, Path 151 Row 043, acquired 2025-09-30). Contains SR_B1..B7, ST_B10, QA_PIXEL, MTL metadata.
   - Discrepancy Note: Scene `LC08_L2SP_151043_20250922_20250930_02_T1` was registered in `datasets.csv` as pending download, but is absent locally. The real available bundle is the 2025-09-30 Landsat 9 scene for the same WRS-2 footprint.
2. **NASA SMAP SPL4SMGP V008**:
   - Location: `C:\Users\HP\Downloads\smap dataset`
   - Content: Surface & root-zone soil moisture GeoTIFFs (2026-10-01 to 2026-10-07) and `AgriShift_SMAP_Hyderabad_Test.geojson`.
3. **NASA GPM IMERG Final Run V07**:
   - Location: `data/raw/gpm-imerg/`
   - Content: `g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.nc` and `.tif`.
4. **SRTM 1 Arc-Second Global DEM**:
   - Location: `data/raw/terrain/NASA_SRTM_or_NASADEM_Hyderabad/`
   - Content: `SRTMGL1_NC.003_SRTMGL1_DEM_doy2000042000000_aid0001.tif` (1 arc-second ~30m DEM) and NUM quality raster.
5. **NASA POWER Daily Climate**:
   - Location: `data/api-samples/nasa-power/`
   - Content: `POWER_Point_Daily_20150101_20251231_025d40N_068d36E_LST (1).csv` (2015–2025 daily climate parameters at 25.40N, 68.36E).
6. **Meteomatics Hourly Weather**:
   - Location: `data/api-samples/meteomatics/`
   - Content: `json.json` (hourly multi-parameter weather response) and `meteomatics_sample.json`.
