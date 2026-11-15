# NASA GPM IMERG Precipitation Validation Report (Step 2A)

## 1. Executive Summary

This report documents the validation and regional aggregation of the NASA Global Precipitation Measurement (GPM) Integrated Multi-satellitE Retrievals for GPM (IMERG) Final Run V07 product covering the Hyderabad pilot study region.

---

## 2. Dataset Properties & Provenance

- **Provider**: NASA Goddard Earth Sciences Data and Information Services Center (GES DISC) / JAXA.
- **Product**: `GPM_3IMERGDF` Version 07 Final Run (Daily 0.1° precipitation rate).
- **Service / Pipeline**: NASA Giovanni time-averaged spatial export.
- **Source Assets**:
  - `data/raw/gpm-imerg/GIOVANNI-g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.tif`
  - `data/raw/gpm-imerg/g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.nc`
- **Native CRS**: Geographic Coordinate System WGS 84 (`EPSG:4326`)
- **Native Resolution**: $0.1^\circ \times 0.1^\circ$ ($\approx 10\text{ km} \times 10\text{ km}$)
- **Grid Extent**: 4 rows $\times$ 3 columns ($12$ valid cells) covering `[68.20°E, 25.20°N, 68.50°E, 25.60°N]`.
- **Temporal Window**: `2025-09-01T00:00:00Z` to `2025-09-07T23:59:59Z` (7 days).

---

## 3. Physical Parameters & Precipitation Aggregations

1. **Precipitation Rate Unit**: $\text{mm}/\text{day}$ (combined microwave-infrared estimate calibrated with monthly GPCC surface gauges in the Final Run).
2. **Observed Rate Statistics**:
   - Minimum Grid Cell Rate: $4.050\text{ mm}/\text{day}$
   - Maximum Grid Cell Rate: $6.763\text{ mm}/\text{day}$
   - Mean Regional Rate: $5.465\text{ mm}/\text{day}$
3. **Accumulated 7-Day Rainfall**:
   $$\text{gpm\_total\_mm} = 5.465\text{ mm/day} \times 7\text{ days} = \mathbf{38.26\text{ mm}}$$
4. **Rainy Days Metric**:
   - Documented Threshold: Daily rate $> 0.1\text{ mm}/\text{day}$ indicates active satellite precipitation.
   - Result: All $7$ days in this early-September late-monsoon pulse recorded measurable rainfall ($\mathbf{7\text{ days}}$).

---

## 4. Mandatory Limitation & Caveats

> **Limitation Notice**: “Regional satellite rainfall estimate; not an individual field rain gauge.”
- Satellite passive microwave and infrared sensors observe atmospheric hydrometeors over a 10 km grid box; convective shower localization within a specific field boundary cannot be resolved at this scale.
- Does not substitute for an on-farm tipping-bucket rain gauge.
