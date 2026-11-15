"""
SRTM DEM Terrain Derivative Processing.
Reprojects elevation to UTM Zone 42N for accurate metric gradient calculation,
computes slope in degrees, derives relative low-lying topographic indicator,
and writes processed rasters.
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
from rasterio.warp import Resampling, calculate_default_transform, reproject

from geospatial.terrain.validate_terrain import DEFAULT_TERRAIN_DIR

PROCESSED_TERRAIN_DIR = ROOT_DIR / "data" / "processed" / "terrain"
PROCESSED_TERRAIN_DIR.mkdir(parents=True, exist_ok=True)

TARGET_PROJ_CRS = "EPSG:32642"  # WGS 84 / UTM zone 42N
NODATA_FLOAT = -9999.0
NODATA_UINT8 = 0


def calculate_slope_horn(dem: np.ndarray, cell_size_x: float, cell_size_y: float) -> np.ndarray:
    """
    Calculate topographic slope in degrees using Horn's 3x3 algorithm.
    Accurate for projected coordinate systems where x, y, and z are in meters.
    """
    slope = np.full(dem.shape, NODATA_FLOAT, dtype=np.float32)

    # Pad array for boundary handling
    padded = np.pad(dem, 1, mode="edge")

    # 3x3 window cells:
    # [a, b, c]
    # [d, e, f]
    # [g, h, i]
    a = padded[:-2, :-2]
    b = padded[:-2, 1:-1]
    c = padded[:-2, 2:]
    d = padded[1:-1, :-2]
    f = padded[1:-1, 2:]
    g = padded[2:, :-2]
    h = padded[2:, 1:-1]
    i = padded[2:, 2:]

    # Rate of change in x (east-west)
    dz_dx = ((c + 2 * f + i) - (a + 2 * d + g)) / (8 * cell_size_x)
    # Rate of change in y (north-south)
    dz_dy = ((g + 2 * h + i) - (a + 2 * b + c)) / (8 * cell_size_y)

    rise_run = np.sqrt(dz_dx**2 + dz_dy**2)
    slope_deg = np.degrees(np.arctan(rise_run))

    # Valid mask where DEM is valid
    valid = (dem != NODATA_FLOAT) & (~np.isnan(dem))
    slope[valid] = slope_deg[valid]
    return slope


def process_terrain(
    terrain_dir: Path = DEFAULT_TERRAIN_DIR,
    out_dir: Path = PROCESSED_TERRAIN_DIR,
) -> dict[str, Any]:
    dem_files = list(terrain_dir.glob("*DEM*.tif")) + list(terrain_dir.glob("*dem*.tif"))
    if not dem_files:
        raise FileNotFoundError("SRTM DEM GeoTIFF not found.")

    dem_path = dem_files[0]

    with rasterio.open(dem_path) as src:
        src_crs = src.crs
        src_nodata = src.nodata if src.nodata is not None else -32768.0

        # Calculate UTM 42N transform and shape at exact 30.0m resolution
        transform_utm, width_utm, height_utm = calculate_default_transform(
            src_crs,
            TARGET_PROJ_CRS,
            src.width,
            src.height,
            *src.bounds,
            resolution=(30.0, 30.0),
        )

        dem_utm = np.full((height_utm, width_utm), NODATA_FLOAT, dtype=np.float32)

        reproject(
            source=rasterio.band(src, 1),
            destination=dem_utm,
            src_transform=src.transform,
            src_crs=src_crs,
            src_nodata=src_nodata,
            dst_transform=transform_utm,
            dst_crs=TARGET_PROJ_CRS,
            dst_nodata=NODATA_FLOAT,
            resampling=Resampling.bilinear,
        )

    # Calculate slope in degrees on UTM grid
    slope_utm = calculate_slope_horn(dem_utm, cell_size_x=30.0, cell_size_y=30.0)

    # Derive relative low-lying indicator
    # Hyderabad Indus floodplain relative depression:
    # Documented relative threshold: elevation <= 15th percentile of valid pilot terrain
    valid_elev = dem_utm[dem_utm != NODATA_FLOAT]
    p15_threshold = float(np.percentile(valid_elev, 15))

    low_lying_utm = np.full(dem_utm.shape, NODATA_UINT8, dtype=np.uint8)
    low_lying_mask = (dem_utm != NODATA_FLOAT) & (dem_utm <= p15_threshold)
    low_lying_utm[low_lying_mask] = 1

    # Write output GeoTIFF rasters
    elev_out = out_dir / "elevation.tif"
    slope_out = out_dir / "slope_degrees.tif"
    low_lying_out = out_dir / "low_lying_flag.tif"

    profile = {
        "driver": "GTiff",
        "height": height_utm,
        "width": width_utm,
        "crs": TARGET_PROJ_CRS,
        "transform": transform_utm,
        "compress": "deflate",
    }

    # Elevation
    with rasterio.open(elev_out, "w", count=1, dtype="float32", nodata=NODATA_FLOAT, **profile) as ds:
        ds.write(dem_utm.astype(np.float32), 1)

    # Slope
    with rasterio.open(slope_out, "w", count=1, dtype="float32", nodata=NODATA_FLOAT, **profile) as ds:
        ds.write(slope_utm.astype(np.float32), 1)

    # Low-lying flag
    with rasterio.open(low_lying_out, "w", count=1, dtype="uint8", nodata=NODATA_UINT8, **profile) as ds:
        ds.write(low_lying_utm.astype(np.uint8), 1)

    # Compute statistics
    valid_slope = slope_utm[slope_utm != NODATA_FLOAT]

    summary = {
        "source_dem": dem_path.name,
        "projected_crs": TARGET_PROJ_CRS,
        "grid_resolution_m": [30.0, 30.0],
        "grid_shape": [height_utm, width_utm],
        "elevation_stats": {
            "min_m": round(float(valid_elev.min()), 2),
            "max_m": round(float(valid_elev.max()), 2),
            "mean_m": round(float(valid_elev.mean()), 2),
            "std_m": round(float(valid_elev.std()), 2),
        },
        "slope_stats": {
            "min_deg": round(float(valid_slope.min()), 2),
            "max_deg": round(float(valid_slope.max()), 2),
            "mean_deg": round(float(valid_slope.mean()), 2),
            "std_deg": round(float(valid_slope.std()), 2),
        },
        "low_lying_definition": {
            "method": "relative_percentile_threshold",
            "percentile": 15,
            "threshold_elevation_m": round(p15_threshold, 2),
            "flagged_pixel_count": int(low_lying_mask.sum()),
            "flagged_fraction": round(float(low_lying_mask.sum()) / float(len(valid_elev)), 4),
            "disclaimer": "Relative topographic depression only; does not claim regulatory flood risk.",
        },
        "outputs": {
            "elevation": str(elev_out.relative_to(ROOT_DIR)),
            "slope_degrees": str(slope_out.relative_to(ROOT_DIR)),
            "low_lying_flag": str(low_lying_out.relative_to(ROOT_DIR)),
        },
    }

    print("Terrain processing complete. Summary:")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    process_terrain()
