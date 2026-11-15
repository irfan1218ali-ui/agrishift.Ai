"""
Landsat Processing Pipeline.
Applies Surface Reflectance scaling, Surface Temperature conversion,
QA_PIXEL masking, and computes NDVI, NDMI, BSI, and Surface Temperature rasters.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import numpy as np
import rasterio
from rasterio.transform import Affine
from rasterio.warp import transform_bounds

from geospatial.landsat.validate_landsat import (
    DEFAULT_LANDSAT_DIR,
    PILOT_BOUNDS_WGS84,
    find_landsat_files,
    parse_mtl_metadata,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_LANDSAT_DIR = ROOT_DIR / "data" / "processed" / "landsat"
PROCESSED_LANDSAT_DIR.mkdir(parents=True, exist_ok=True)

NODATA_VALUE_FLOAT = -9999.0
NODATA_VALUE_UINT8 = 0


def safe_divide(numerator: np.ndarray, denominator: np.ndarray, valid_mask: np.ndarray) -> np.ndarray:
    """Safe division avoiding division by zero or NaN propagation."""
    out = np.full(numerator.shape, NODATA_VALUE_FLOAT, dtype=np.float32)
    safe = valid_mask & (~np.isnan(numerator)) & (~np.isnan(denominator)) & (np.abs(denominator) > 1e-7)
    out[safe] = np.divide(numerator[safe], denominator[safe], dtype=np.float32)
    return out


def compute_spectral_indices(
    blue: np.ndarray,
    green: np.ndarray,
    red: np.ndarray,
    nir: np.ndarray,
    swir1: np.ndarray,
    valid_mask: np.ndarray,
) -> dict[str, np.ndarray]:
    """
    Compute standard remote sensing indices:
    NDVI = (NIR - Red) / (NIR + Red)
    NDMI = (NIR - SWIR1) / (NIR + SWIR1)
    BSI  = ((SWIR1 + Red) - (NIR + Blue)) / ((SWIR1 + Red) + (NIR + Blue))
    """
    # NDVI
    ndvi_num = nir - red
    ndvi_den = nir + red
    ndvi = safe_divide(ndvi_num, ndvi_den, valid_mask)
    # Validate sensible physical bounds [-1, 1]
    invalid_ndvi = (ndvi != NODATA_VALUE_FLOAT) & ((ndvi < -1.0) | (ndvi > 1.0))
    if np.any(invalid_ndvi):
        ndvi[invalid_ndvi] = NODATA_VALUE_FLOAT

    # NDMI (Gao 1996)
    ndmi_num = nir - swir1
    ndmi_den = nir + swir1
    ndmi = safe_divide(ndmi_num, ndmi_den, valid_mask)
    invalid_ndmi = (ndmi != NODATA_VALUE_FLOAT) & ((ndmi < -1.0) | (ndmi > 1.0))
    if np.any(invalid_ndmi):
        ndmi[invalid_ndmi] = NODATA_VALUE_FLOAT

    # Bare Soil Index (BSI)
    bsi_num = (swir1 + red) - (nir + blue)
    bsi_den = (swir1 + red) + (nir + blue)
    bsi = safe_divide(bsi_num, bsi_den, valid_mask)
    invalid_bsi = (bsi != NODATA_VALUE_FLOAT) & ((bsi < -1.0) | (bsi > 1.0))
    if np.any(invalid_bsi):
        bsi[invalid_bsi] = NODATA_VALUE_FLOAT

    return {"ndvi": ndvi, "ndmi": ndmi, "bsi": bsi}


def write_geotiff(
    out_path: Path,
    data: np.ndarray,
    crs: Any,
    transform: Affine,
    nodata: float | int,
    dtype: str,
):
    profile = {
        "driver": "GTiff",
        "height": data.shape[0],
        "width": data.shape[1],
        "count": 1,
        "dtype": dtype,
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
        "compress": "deflate",
    }
    with rasterio.open(out_path, "w", **profile) as ds:
        ds.write(data.astype(dtype), 1)


def process_landsat_scene(
    landsat_dir: Path = DEFAULT_LANDSAT_DIR,
    out_dir: Path = PROCESSED_LANDSAT_DIR,
    pilot_bounds: tuple[float, float, float, float] = PILOT_BOUNDS_WGS84,
) -> dict[str, Any]:
    """Execute complete Landsat calibration, QA masking, and index generation."""
    found_files = find_landsat_files(landsat_dir)
    mtl_meta = parse_mtl_metadata(found_files["MTL"])

    # Read QA_PIXEL to determine pilot window and cloud-free mask
    with rasterio.open(found_files["QA_PIXEL"]) as qa_ds:
        utm_bounds = transform_bounds("EPSG:4326", qa_ds.crs, *pilot_bounds)
        window = rasterio.windows.from_bounds(*utm_bounds, transform=qa_ds.transform).round_offsets().round_lengths()
        window_transform = rasterio.windows.transform(window, qa_ds.transform)
        target_crs = qa_ds.crs

        qa = qa_ds.read(1, window=window)

    # QA bitmask decoding
    fill_mask = (qa & (1 << 0)) > 0
    dilated_mask = (qa & (1 << 1)) > 0
    cirrus_mask = (qa & (1 << 2)) > 0
    cloud_mask = (qa & (1 << 3)) > 0
    shadow_mask = (qa & (1 << 4)) > 0

    invalid_mask = fill_mask | dilated_mask | cirrus_mask | cloud_mask | shadow_mask
    cloud_free_mask = (~invalid_mask) & (~fill_mask)

    # Read and scale surface reflectance bands
    sr_mult = mtl_meta["sr_mult"]
    sr_add = mtl_meta["sr_add"]

    def read_scaled_sr(band_key: str) -> np.ndarray:
        with rasterio.open(found_files[band_key]) as ds:
            raw = ds.read(1, window=window)
            valid_raw = (raw > 0) & cloud_free_mask
            scaled = np.full(raw.shape, np.nan, dtype=np.float32)
            scaled[valid_raw] = raw[valid_raw] * sr_mult + sr_add
            # Physical surface reflectance should be in [0, 1]
            # Saturated/noise values slightly below 0 or above 1 are clipped to [0, 1]
            scaled[valid_raw] = np.clip(scaled[valid_raw], 0.0, 1.0)
            return scaled

    blue = read_scaled_sr("SR_B2")
    green = read_scaled_sr("SR_B3")
    red = read_scaled_sr("SR_B4")
    nir = read_scaled_sr("SR_B5")
    swir1 = read_scaled_sr("SR_B6")

    # Spectral indices
    indices = compute_spectral_indices(blue, green, red, nir, swir1, cloud_free_mask)

    # Surface Temperature in Celsius
    # Kelvin = DN * mult + add; Celsius = Kelvin - 273.15
    st_mult = mtl_meta["st_mult"]
    st_add = mtl_meta["st_add"]
    with rasterio.open(found_files["ST_B10"]) as st_ds:
        st_raw = st_ds.read(1, window=window)
        st_valid = (st_raw > 0) & cloud_free_mask
        temp_c = np.full(st_raw.shape, NODATA_VALUE_FLOAT, dtype=np.float32)
        kelvin = st_raw[st_valid] * st_mult + st_add
        temp_c[st_valid] = kelvin - 273.15
        # Validate realistic surface temperatures [-10C, 75C]
        unrealistic = (temp_c != NODATA_VALUE_FLOAT) & ((temp_c < -10.0) | (temp_c > 75.0))
        temp_c[unrealistic] = NODATA_VALUE_FLOAT

    # Save output rasters
    ndvi_path = out_dir / "ndvi.tif"
    ndmi_path = out_dir / "ndmi.tif"
    bsi_path = out_dir / "bsi.tif"
    temp_path = out_dir / "surface_temperature_c.tif"
    mask_path = out_dir / "cloud_free_mask.tif"

    write_geotiff(ndvi_path, indices["ndvi"], target_crs, window_transform, NODATA_VALUE_FLOAT, "float32")
    write_geotiff(ndmi_path, indices["ndmi"], target_crs, window_transform, NODATA_VALUE_FLOAT, "float32")
    write_geotiff(bsi_path, indices["bsi"], target_crs, window_transform, NODATA_VALUE_FLOAT, "float32")
    write_geotiff(temp_path, temp_c, target_crs, window_transform, NODATA_VALUE_FLOAT, "float32")
    write_geotiff(mask_path, cloud_free_mask.astype(np.uint8), target_crs, window_transform, NODATA_VALUE_UINT8, "uint8")

    # Compute output stats
    def get_stats(arr: np.ndarray, nodata: float) -> dict[str, Any]:
        valid = arr[arr != nodata]
        if len(valid) == 0:
            return {"count": 0, "min": None, "max": None, "mean": None, "std": None}
        return {
            "count": int(len(valid)),
            "min": round(float(valid.min()), 4),
            "max": round(float(valid.max()), 4),
            "mean": round(float(valid.mean()), 4),
            "std": round(float(valid.std()), 4),
        }

    report = {
        "scene_id": mtl_meta["scene_id"],
        "acquisition_date": mtl_meta["acquisition_date"],
        "target_crs": str(target_crs),
        "window_shape": list(qa.shape),
        "total_pixels": int(qa.size),
        "cloud_free_pixels": int(cloud_free_mask.sum()),
        "cloud_free_fraction": round(float(cloud_free_mask.sum()) / float(qa.size), 4),
        "cloud_free_fraction_on_swath": round(float(cloud_free_mask.sum()) / float((~fill_mask).sum()), 4),
        "statistics": {
            "ndvi": get_stats(indices["ndvi"], NODATA_VALUE_FLOAT),
            "ndmi": get_stats(indices["ndmi"], NODATA_VALUE_FLOAT),
            "bsi": get_stats(indices["bsi"], NODATA_VALUE_FLOAT),
            "surface_temp_c": get_stats(temp_c, NODATA_VALUE_FLOAT),
        },
        "outputs": {
            "ndvi": str(ndvi_path.relative_to(ROOT_DIR)),
            "ndmi": str(ndmi_path.relative_to(ROOT_DIR)),
            "bsi": str(bsi_path.relative_to(ROOT_DIR)),
            "surface_temperature_c": str(temp_path.relative_to(ROOT_DIR)),
            "cloud_free_mask": str(mask_path.relative_to(ROOT_DIR)),
        },
    }
    print("Landsat processing complete. Summary:")
    print(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    process_landsat_scene()
