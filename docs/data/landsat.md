# USGS Landsat 8/9 Collection 2 Level-2

- **Selected scene:** `LC08_L2SP_151043_20250922_20250930_02_T1`, acquisition 2025-09-22, path 151/row 043.
- **Purpose/variables:** Surface Reflectance SR_B2–SR_B7; ST_B10 surface temperature; QA_PIXEL; product metadata. Supports vegetation/water/bare-soil indices, surface temperature, field imagery and future model features.
- **Resolution:** scene/product metadata must be read from the package; do not infer actual grid properties here.
- **Access/status:** expected scene folder exists, but it contains only a manifest and instructions. No `SR_B2`–`SR_B7`, `ST_B10`, `QA_PIXEL`, or MTL asset was found. The manifest records zero scene source files.
- **Storage:** no scene assets were copied or edited. Expected local folder is `data/raw/landsat/USGS_Landsat_C2_L2_Hyderabad_2025-09-22/`.
- **Processing/quality:** a guarded feature builder is ready to read MTL scale/offset, QA_PIXEL bits 0–5, and compute indices/thermal features after the exact scene is supplied. It currently stops before writing output.
- **Limitations/model/map:** no real Landsat index, cloud-free fraction, thermal value, overlay, feature row, or model metric is available.
