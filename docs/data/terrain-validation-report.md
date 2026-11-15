# SRTM Terrain Validation & Derivative Processing Report (Step 2A)

## 1. Source Overview & Verification

- **Product**: NASA Shuttle Radar Topography Mission (SRTM) Global 1 Arc-Second (SRTMGL1 Version 003).
- **Source File**: `SRTMGL1_NC.003_SRTMGL1_DEM_doy2000042000000_aid0001.tif`
- **Quality Scene Mask**: `SRTMGL1_NUMNC.003_SRTMGL1_NUM_doy2000042000000_aid0001.tif`
- **Native CRS**: Geographic Coordinate System WGS 84 (`EPSG:4326`)
- **Native Bounds**: `[68.199861°E, 25.199861°N, 68.550139°E, 25.550139°N]`
- **Native Grid Size**: $1,261 \times 1,261$ pixels (1 arc-second $\approx 0.00027778^\circ \approx 30\text{ m}$)
- **Pilot Coverage**: 100% complete coverage across `[68.20°E, 25.20°N, 68.55°E, 25.55°N]` with zero NoData cells inside the target bounding box.

---

## 2. Metric Gradient & Slope Processing Methodology

Calculating terrain slope directly on geographic coordinates (degrees) produces severe distortion due to latitude convergence. To ensure scientific rigor:
1. **Reprojection**: The DEM was reprojected to the local conformal projection **UTM Zone 42N (`EPSG:32642`)** using bilinear interpolation at an exact $30.0\text{ m} \times 30.0\text{ m}$ cell size.
2. **Gradient Algorithm**: Slope was computed in degrees using **Horn's 3x3 algorithm**:
   $$\frac{\partial z}{\partial x} = \frac{(c + 2f + i) - (a + 2d + g)}{8 \times \Delta x}$$
   $$\frac{\partial z}{\partial y} = \frac{(g + 2h + i) - (a + 2b + c)}{8 \times \Delta y}$$
   $$\text{Slope}_{\text{deg}} = \arctan\left(\sqrt{\left(\frac{\partial z}{\partial x}\right)^2 + \left(\frac{\partial z}{\partial y}\right)^2}\right) \times \frac{180}{\pi}$$
   where $\Delta x = 30.0\text{ m}$ and $\Delta y = 30.0\text{ m}$.
3. **NoData Handling**: Invalid cells and edge boundaries were consistently marked with `NoData = -9999.0`.

---

## 3. Relative Low-Lying Topographic Indicator

- **Scientific Principle**: Indus basin riverine floodplains feature subtle natural levees and backswamps.
- **Methodology**: Rather than claiming unverified regulatory flood hazard, a transparent relative topographic metric is employed:
  $$\text{low\_lying\_flag} = \begin{cases} 1 & \text{if } \text{Elevation} \le P_{15} \ (18.77\text{ m}) \\ 0 & \text{otherwise} \end{cases}$$
- **Disclaimers**: Strictly indicates relative topographic lowlands and drainage sinks; does not constitute a flood hazard risk model.

---

## 4. Output Raster Statistics

| Raster Output | Physical Quantity | Units | Min | Max | Mean | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `data/processed/terrain/elevation.tif` | Ground Elevation | meters ($\text{m}$) | -8.35 | 138.92 | 29.07 | 15.09 |
| `data/processed/terrain/slope_degrees.tif` | Terrain Slope | degrees ($^{\circ}$) | 0.00 | 89.70 | 2.36 | 5.10 |
| `data/processed/terrain/low_lying_flag.tif` | Relative Depression | boolean $\{0, 1\}$ | 0 | 1 | 0.1500 | 0.3571 |

---

## 5. Limitations

1. **Static Baseline**: SRTM radar reflects terrain as captured during the February 2000 Space Shuttle Endeavour mission; modern canal embankments or recent earthworks post-2000 are not reflected.
2. **Canopy & Structure Penetration**: C-band radar reflects from vegetation canopy tops and urban structures rather than bare ground in dense built-up zones.
