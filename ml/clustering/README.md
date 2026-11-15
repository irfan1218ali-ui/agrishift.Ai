# AgriShift AI — Unsupervised Environmental Clustering Module

## 1. Overview

This module implements unsupervised K-Means clustering over real spatial observation points in the Hyderabad pilot region. The objective is to identify distinct environmental and vegetative condition clusters across the landscape without making diagnostic or agronomic claims (such as "crop disease" or "failure").

---

## 2. Feature Definitions

Clustering is trained on 6 continuous, standardized environmental features:
1. `ndvi_mean`: Normalized Difference Vegetation Index (Landsat 9 SR_B5/B4)
2. `ndmi_mean`: Normalized Difference Moisture Index (Landsat 9 SR_B5/B6)
3. `bsi_mean`: Bare Soil Index (Landsat 9 SR_B2/B4/B5/B6)
4. `surface_temp_c`: Land Surface Temperature in $^{\circ}\text{C}$ (Landsat 9 ST_B10)
5. `elevation_m`: Ground elevation in meters (SRTMGL1 DEM)
6. `slope_deg`: Topographic slope in degrees (computed via Horn's metric gradient algorithm)

Regional variables (SMAP, GPM) and macro-climate statistics (POWER) are attached as spatial context and excluded from feature-space scaling to prevent artificial zero-variance or constant-feature artifacts.

---

## 3. Standardization & Model Selection

- **Scaling**: All input features are centered and scaled using `StandardScaler` ($\mu = 0, \sigma = 1$).
- **Algorithm**: `sklearn.cluster.KMeans` with fixed `random_state=42`, `n_init=10`.
- **Model Evaluation**: Tested $k \in \{2, 3, 4\}$.
  - $k=2$: Silhouette 0.3893, Davies-Bouldin 1.0200
  - **$k=3$ (Selected)**: Silhouette **0.3546**, Davies-Bouldin **0.9780** (Optimal), Sizes: 62, 67, 20
  - $k=4$: Silhouette 0.3096, Davies-Bouldin 1.0834

---

## 4. Neutral Cluster Profiles

| Cluster ID | Neutral Label | Size | Sample Center (Original Units) |
| :--- | :--- | :--- | :--- |
| **0** | **Relatively vegetated** | 62 (41.6%) | NDVI: 0.59, NDMI: 0.27, BSI: -0.17, LST: 37.4°C, Elev: 20.9 m, Slope: 1.7° |
| **1** | **Intermediate condition** | 67 (45.0%) | NDVI: 0.34, NDMI: 0.13, BSI: -0.00, LST: 41.4°C, Elev: 21.6 m, Slope: 2.0° |
| **2** | **Higher bare/thermal exposure** | 20 (13.4%) | NDVI: 0.26, NDMI: -0.00, BSI: 0.09, LST: 43.8°C, Elev: 45.9 m, Slope: 3.0° |

---

## 5. Serialized Artifacts

All model artifacts are stored in `ml/clustering/artifacts/`:
- `scaler.joblib`: Fitted `StandardScaler` pipeline.
- `kmeans.joblib`: Fitted `KMeans` estimator ($k=3$).
- `cluster_profile.json`: Mean and standard deviation profiles per cluster in physical units.
- `metrics.json`: Comparative evaluation metrics across all evaluated $K$ values.
- `training_manifest.json`: Checksummed training metadata and reproducibility manifest.
