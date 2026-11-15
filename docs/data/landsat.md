# USGS Landsat 8/9 Collection 2 Level-2

- **Selected scene:** `LC08_L2SP_151043_20250922_20250930_02_T1`, acquisition 2025-09-22, path 151/row 043.
- **Purpose/variables:** Surface Reflectance SR_B2–SR_B7; ST_B10 surface temperature; QA_PIXEL; product metadata. Supports vegetation/water/bare-soil indices, surface temperature, field imagery and future model features.
- **Resolution:** scene/product metadata must be read from the package; do not infer actual grid properties here.
- **Access/status:** USGS Landsat Collection 2 Level-2 Product Bundle; registered from user-supplied details. User reports downloaded or being organized, but matching scene files were not located in the scanned project, Downloads, Desktop or Documents folders.
- **Storage:** expected path `data/raw/landsat/USGS_Landsat_C2_L2_Hyderabad_2025-09-22/original/`; no files copied.
- **Processing/quality:** apply product scale/offset and QA_PIXEL cloud/shadow/snow/water interpretation after metadata inspection; validate CRS, NoData, acquisition, masks and checksums before indices.
- **Limitations/model/map:** cloud/revisit and pixel support constrain field interpretation. Map and model use require validated scene coverage and quality. No labels or derived values are claimed.
