# K-Means Environmental Clustering Evaluation Report (Step 2A)

## 1. Executive Summary

This report documents the unsupervised machine-learning methodology, experimental evaluation, cluster profiles, and validation metrics for the environmental clustering pipeline in AgriShift AI. The model groups real spatial observation points within the Hyderabad pilot region according to their multi-spectral vegetation indices, thermal properties, and terrain characteristics.

---

## 2. Dataset & Sample Size

- **Total Spatial Candidate Points**: 149
- **Valid Observations Filtered**: **149** (0 dropped; 100% data completeness across required features)
- **Minimum Required Sample Size**: 20 observations (achieved 149 observations, well within preferred 50–200 range)
- **Spatial Resolution & Window**: 150 m radius local circular zonal summary per point
- **Bounding Coverage**: Hyderabad pilot area `[68.20°E, 25.20°N, 68.55°E, 25.55°N]`

---

## 3. Feature Selection & Preprocessing

### 3.1 Input Features Used ($d=6$)
1. `ndvi_mean`: Normalized Difference Vegetation Index (Landsat 9)
2. `ndmi_mean`: Normalized Difference Moisture Index (Landsat 9)
3. `bsi_mean`: Bare Soil Index (Landsat 9)
4. `surface_temp_c`: Land Surface Temperature in $^{\circ}\text{C}$ (Landsat 9)
5. `elevation_m`: Ground elevation in meters (SRTM)
6. `slope_deg`: Topographic slope in degrees (SRTM metric gradient)

### 3.2 Features Excluded from Clustering
- **Point Identifiers & Coordinates** (`id`, `lat`, `lon`): Excluded to prevent geographic proximity bias.
- **Regional Context Indicators** (`smap_surface_mean`, `smap_rootzone_mean`, `gpm_mean_daily_rate_mm_day`): Excluded because coarse 9–10 km satellite footprints have zero point-to-point variance across the pilot grid.
- **Macro-Climate Averages** (`rh_mean`, `wind_mean`, `solar_radiation_mean`): Excluded because reanalysis climate data is uniform across the pilot point sample.

### 3.3 Standardization
All 6 features were standardized using `sklearn.preprocessing.StandardScaler` ($\mu = 0, \sigma = 1$). Feature variance was verified to ensure no near-constant features entered the clustering pipeline.

---

## 4. Model Selection & Experimental Results

Evaluated across $k \in \{2, 3, 4\}$ with fixed `random_state=42`, `n_init=10`:

| $K$ | Silhouette Score | Davies-Bouldin Index | Inertia | Cluster Sizes | Size Distribution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$k=2$** | **0.3893** | 1.0200 | 545.98 | {0: 83, 1: 66} | 55.7% / 44.3% |
| **$k=3$ (Selected)** | 0.3546 | **0.9780** | **378.89** | {0: 62, 1: 67, 2: 20} | 41.6% / 45.0% / 13.4% |
| **$k=4$** | 0.3096 | 1.0834 | 309.91 | {0: 53, 1: 32, 2: 16, 3: 48} | 35.6% / 21.5% / 10.7% / 32.2% |

### Selection Rationale
- **Optimal Cluster Separation**: $k=3$ achieves the lowest Davies-Bouldin index (**0.9780**), indicating optimal intra-cluster compactness and inter-cluster separation.
- **Meaningful Grouping**: $k=2$ over-aggregates bare upland terrain into moderate cropland. Conversely, $k=4$ degrades the silhouette score to 0.3096 and generates a small cluster of only 16 points.
- **Robust Sizing**: In $k=3$, all three clusters have $\ge 20$ samples (62, 67, and 20), avoiding trivial or isolated clusters.

---

## 5. Physical Cluster Profiles & Neutral Interpretations

Cluster centers mapped back to original physical units ($\mu \pm \sigma$):

### Cluster 0: Relatively vegetated ($n=62$, $41.6\%$)
- `ndvi_mean`: $0.59 \pm 0.08$ (High vegetative canopy vigor)
- `ndmi_mean`: $0.27 \pm 0.07$ (High canopy water content)
- `bsi_mean`: $-0.17 \pm 0.06$ (Very low bare soil exposure)
- `surface_temp_c`: $37.36 \pm 2.68^\circ\text{C}$ (Cooler due to active vegetative evapotranspiration)
- `elevation_m`: $20.93 \pm 4.29\text{ m}$ (Lowland irrigated alluvial plain)
- `slope_deg`: $1.69 \pm 0.50^\circ$ (Flat agricultural fields)
- **Interpretation**: Actively transpiring, dense vegetative canopy within the canal-irrigated command zone.

### Cluster 1: Intermediate condition ($n=67$, $45.0\%$)
- `ndvi_mean`: $0.34 \pm 0.07$ (Moderate vegetation density)
- `ndmi_mean`: $0.13 \pm 0.05$ (Moderate moisture content)
- `bsi_mean`: $-0.00 \pm 0.05$ (Balanced vegetative and bare ground reflectance)
- `surface_temp_c`: $41.35 \pm 2.03^\circ\text{C}$ (Moderate surface temperature)
- `elevation_m`: $21.57 \pm 3.19\text{ m}$ (Alluvial plain)
- `slope_deg`: $1.95 \pm 0.53^\circ$ (Gentle slopes)
- **Interpretation**: Mixed surface condition, transitional crop growth, or partially fallow agricultural land.

### Cluster 2: Higher bare/thermal exposure ($n=20$, $13.4\%$)
- `ndvi_mean`: $0.26 \pm 0.07$ (Sparse vegetation)
- `ndmi_mean`: $-0.00 \pm 0.04$ (Low moisture / dry surface)
- `bsi_mean`: $0.09 \pm 0.03$ (High bare soil and mineral exposure)
- `surface_temp_c`: $43.75 \pm 2.21^\circ\text{C}$ (Highest thermal emission)
- `elevation_m`: $45.93 \pm 14.15\text{ m}$ (Upland gravel terraces / uncultivated ridges)
- `slope_deg`: $2.99 \pm 0.99^\circ$ (Moderate undulating slope)
- **Interpretation**: Elevated, dry, uncultivated or post-harvest fields with high bare soil fraction and high thermal radiance.

---

## 6. Scientific Integrity & Label Policy Compliance

- **Prohibited Labels**: Strictly avoided diagnostic assertions such as "healthy crop", "diseased field", "crop failure", or "guaranteed suitable".
- **Unsupervised Nature**: K-Means clusters represent multi-dimensional statistical groupings of satellite reflectance and elevation; they do **not** directly diagnose crop varieties, yields, or agronomic management quality.

---

## 7. Artifact Integrity & Checksums

| Artifact File | Description | SHA-256 Checksum |
| :--- | :--- | :--- |
| `scaler.joblib` | Scikit-learn StandardScaler pipeline | `a043e4b84f54ecca5155c9a893fc7945703bd44d985a987df685545735be5158` |
| `kmeans.joblib` | Scikit-learn KMeans ($k=3$) estimator | `00aa221753490d26dca2955853193ed7f0f6f35624726d350e3444c7e8bcc480` |
| `cluster_profile.json` | Statistical profiles in physical units | `dfc89bfd1e58f5816a85ea2d327ba8befe302f9128831623f9ddb077f0767a7e` |
| `metrics.json` | Evaluation metrics across $k=2,3,4$ | `443a09a5571fdf6b5c9cbf53ffd685265edf0786969adfed1f253c5e3c52775b` |
| `training_manifest.json` | Training manifest & audit metadata | Generated and verified |
