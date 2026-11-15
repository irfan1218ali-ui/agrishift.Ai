# AgriShift AI — Data & ML Reproducible Environment

## 1. Runtime Specifications

- **Python Version**: CPython 3.11.9 (Windows x86_64)
- **Virtual Environment Manager**: `uv` (version 0.9.30) / standard `venv`
- **Isolation Scope**: Fully isolated environment dedicated strictly to data processing, geospatial raster analysis, feature extraction, and unsupervised K-Means clustering.

## 2. Pinned Package Versions

| Package | Version | Purpose |
| :--- | :--- | :--- |
| `numpy` | 2.4.6 | Numerical array calculations, index formulas |
| `pandas` | 3.1.1 | Tabular data analysis, aggregation, manifest management |
| `rasterio` | 1.4.4 | Geospatial raster I/O, windowing, affine transforms |
| `affine` | 3.0.1 | Affine coordinate transformations |
| `pyproj` | 3.7.2 | Cartographic projections and coordinate system transforms |
| `shapely` | 2.2.0 | Geometric spatial operations |
| `scipy` | 1.17.1 | Scientific and spatial algorithms |
| `scikit-learn` | 1.9.1 | StandardScaler, KMeans, silhouette_score, davies_bouldin_score |
| `joblib` | 1.6.0 | Serializing model pipelines and scalers |
| `Pillow` | 13.0.0 | Rendering transparent geospatial overlay PNGs |
| `netCDF4` | 1.7.5.1.post1 | Inspecting NetCDF4 satellite precipitation data |
| `cftime` | 1.6.6.1 | Time dimension handling for climate datasets |
| `pytest` | 9.2.0 | Automated verification of data rules, ML constraints, and manifests |
| `ruff` | 0.17.5 | Code linting and style verification |

## 3. Setup Commands

From the workspace root (`agrishift-step2-data`):

```powershell
# 1. Create isolated virtual environment
uv venv .venv --python 3.11

# 2. Install dependencies
uv pip install --python .venv -r requirements-data-ml.txt

# 3. Verify installation
.venv\Scripts\python.exe -c "import rasterio, sklearn, pandas, numpy; print('Environment OK')"
```

## 4. Platform & GDAL/Rasterio Compatibility Notes

- Windows 11 binaries for `rasterio` and `netCDF4` are pre-compiled with embedded GDAL and HDF5 runtime libraries, eliminating external C-compiler dependencies.
- No heavy deep learning dependencies (`torch`, `tensorflow`, `jax`) are installed.
- All geospatial reprojections leverage PROJ via `rasterio.warp` or `pyproj`.

## 5. Verification Command

```powershell
.venv\Scripts\pytest.exe -q tests/data tests/geospatial tests/ml
```
