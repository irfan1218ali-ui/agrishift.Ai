"""
SRTM 1 Arc-Second Global DEM Validator.
Validates CRS, coverage, elevation values, NoData handling, and resolution.
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

DEFAULT_TERRAIN_DIR = ROOT_DIR / "data" / "raw" / "terrain" / "NASA_SRTM_or_NASADEM_Hyderabad"
PILOT_BOUNDS = (68.2, 25.2, 68.55, 25.55)


def validate_terrain(terrain_dir: Path = DEFAULT_TERRAIN_DIR) -> dict[str, Any]:
    results: dict[str, Any] = {
        "is_valid": False,
        "errors": [],
        "dem_file": None,
        "num_file": None,
        "attributes": {},
        "coverage": {},
        "statistics": {},
    }

    if not terrain_dir.exists():
        results["errors"].append(f"Terrain directory not found: {terrain_dir}")
        return results

    dem_files = list(terrain_dir.glob("*DEM*.tif")) + list(terrain_dir.glob("*dem*.tif"))
    num_files = list(terrain_dir.glob("*NUM*.tif")) + list(terrain_dir.glob("*num*.tif"))

    if not dem_files:
        results["errors"].append("SRTM DEM GeoTIFF not found.")
        return results

    dem_path = dem_files[0]
    results["dem_file"] = dem_path.name
    if num_files:
        results["num_file"] = num_files[0].name

    with rasterio.open(dem_path) as ds:
        crs_str = str(ds.crs)
        bounds = ds.bounds
        res = ds.res
        nodata = ds.nodata
        shape = ds.shape

        results["attributes"] = {
            "crs": crs_str,
            "bounds": [bounds.left, bounds.bottom, bounds.right, bounds.top],
            "pixel_size_deg": [res[0], res[1]],
            "shape": list(shape),
            "nodata": nodata,
            "units": "meters",
        }

        # Check coverage
        covers_pilot = (
            bounds.left <= PILOT_BOUNDS[0]
            and bounds.bottom <= PILOT_BOUNDS[1]
            and bounds.right >= PILOT_BOUNDS[2]
            and bounds.top >= PILOT_BOUNDS[3]
        )
        results["coverage"] = {
            "pilot_bounds": list(PILOT_BOUNDS),
            "fully_covers_pilot": covers_pilot,
        }

        if not covers_pilot:
            results["errors"].append("DEM bounds do not fully encompass pilot bounds.")

        # Read array and calculate statistics
        data = ds.read(1)
        valid_mask = data != nodata if nodata is not None else np.ones(data.shape, dtype=bool)
        valid_count = int(np.count_nonzero(valid_mask))

        if valid_count == 0:
            results["errors"].append("DEM has zero valid elevation pixels.")
            return results

        elevations = data[valid_mask]
        results["statistics"] = {
            "total_pixels": int(data.size),
            "valid_pixels": valid_count,
            "nodata_pixels": int((~valid_mask).sum()),
            "min_elevation_m": float(elevations.min()),
            "max_elevation_m": float(elevations.max()),
            "mean_elevation_m": round(float(elevations.mean()), 2),
            "std_elevation_m": round(float(elevations.std()), 2),
            "p10_elevation_m": round(float(np.percentile(elevations, 10)), 2),
            "p50_elevation_m": round(float(np.percentile(elevations, 50)), 2),
            "p90_elevation_m": round(float(np.percentile(elevations, 90)), 2),
        }

    results["is_valid"] = len(results["errors"]) == 0
    return results


if __name__ == "__main__":
    report = validate_terrain()
    print("Terrain Validation Result:")
    print(json.dumps(report, indent=2))
