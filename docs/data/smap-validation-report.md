# NASA SMAP Soil Moisture Validation Report (Step 2A)

## 1. Executive Summary

This report documents the validation and regional aggregation of NASA Soil Moisture Active Passive (SMAP) Level-4 SPL4SMGP V008 soil moisture data for the Hyderabad pilot study area.

---

## 2. Product Characteristics & Provenance

- **Provider**: NASA National Snow and Ice Data Center (NSIDC) Distributed Active Archive Center (DAAC).
- **Product**: SMAP L4 Global 3-hourly 9 km EASE-Grid Surface and Root Zone Soil Moisture (SPL4SMGP Version 008).
- **Service / Pipeline**: NASA AppEEARS export.
- **Source Files**: 112 individual GeoTIFF assets in `data/raw/smap/extracted/`:
  - 56 surface soil moisture rasters (`sm_surface`)
  - 56 root-zone soil moisture rasters (`sm_rootzone`)
  - 1 AOI definition (`AgriShift_SMAP_Hyderabad_Test.geojson`)
- **Native CRS**: Geographic Coordinate System WGS 84 (`EPSG:4326`)
- **Spatial Resolution**: $\approx 0.078^\circ$ ($\approx 9\text{ km}$ EASE-Grid 2.0 cell equivalent)
- **Temporal Interval**: 3-hourly observations from `2026-10-01T01:30:00Z` to `2026-10-07T22:30:00Z` (8 records/day $\times$ 7 days = 56 steps).

---

## 3. Physical Parameters & Vertical Soil Layers

1. **Surface Soil Moisture (`sm_surface`)**:
   - Represents the top $0\text{--}5\text{ cm}$ layer of soil.
   - Physical Unit: $\text{m}^3/\text{m}^3$ (volumetric water content fraction).
   - Valid Range: $0.0573\text{--}0.0979\text{ m}^3/\text{m}^3$.
   - **Mean Regional Value**: **$0.0725\text{ m}^3/\text{m}^3$** ($7.25\%$).
2. **Root-Zone Soil Moisture (`sm_rootzone`)**:
   - Represents the integrated $0\text{--}100\text{ cm}$ agricultural crop root zone.
   - Physical Unit: $\text{m}^3/\text{m}^3$.
   - Valid Range: $0.1304\text{--}0.1472\text{ m}^3/\text{m}^3$.
   - **Mean Regional Value**: **$0.1413\text{ m}^3/\text{m}^3$** ($14.13\%$).

---

## 4. Temporal Alignment Audit

- **Landsat Acquisition**: `2025-09-30`
- **SMAP Observation Range**: `2026-10-01` to `2026-10-07`
- **Audit Findings**:
  A temporal offset exists between the Landsat scene year (2025) and the available SMAP test export year (2026). In compliance with scientific integrity rules, SMAP data is **not** masqueraded as simultaneous ground truth; it is explicitly documented as **regional post-monsoon soil moisture context** reflecting seasonal moisture retention in the Indus irrigation command area.

---

## 5. Mandatory Limitation

> **Limitation Notice**: “Regional soil-moisture context; not an exact field measurement.”
- Coarse 9 km satellite footprint averages irrigated fields, uncultivated desert scrub, canals, and settlements.
- Must not be downscaled to individual farm boundaries without local hydrological modeling.
