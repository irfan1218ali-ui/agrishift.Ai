# USGS Landsat Collection 2 Level-2

- **Selected scene:** `LC09_L2SP_151043_20250930_20251001_02_T1`, Landsat 9 OLI-2/TIRS-2, acquired 2025-09-30, WRS-2 path 151 / row 043.
- **Bands:** SR_B2–SR_B7, ST_B10, QA_PIXEL, and scene MTL metadata.
- **Processing:** Surface reflectance and temperature scale/offsets are applied from scene metadata; QA_PIXEL masks fill, cloud, cirrus, and shadow. Outputs include NDVI, NDMI, BSI, surface temperature, and cloud-free fraction.
- **Resolution:** 30 m native grid for scene bands; local feature summaries use 150 m radius at approximately 2 km spacing.
- **Status:** 149 validated Hyderabad pilot feature points and the NDVI/NDMI/BSI overlays were produced in Step 2A. Raw scene files remain excluded from Git.
- **Superseded expectation:** the earlier LC08 scene `LC08_L2SP_151043_20250922_20250930_02_T1` was not found and is not the scene used.
- **Limitations:** One observation date is not a time series. Satellite indicators are not crop-disease or field-health diagnoses.
