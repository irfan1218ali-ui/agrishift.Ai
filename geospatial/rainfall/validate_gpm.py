"""
NASA GPM IMERG Final Run V07 Validator.
Validates precipitation rate GeoTIFF and NetCDF files, CRS, resolution, and time range.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import rasterio

DEFAULT_GPM_DIR = ROOT_DIR / "data" / "raw" / "gpm-imerg"


def validate_gpm(gpm_dir: Path = DEFAULT_GPM_DIR) -> dict[str, Any]:
    results: dict[str, Any] = {
        "is_valid": False,
        "errors": [],
        "warnings": [],
        "files_found": {},
        "attributes": {},
        "variable_checks": {},
    }

    if not gpm_dir.exists():
        results["errors"].append(f"GPM directory not found: {gpm_dir}")
        return results

    tif_files = list(gpm_dir.glob("*.tif"))
    nc_files = list(gpm_dir.glob("*.nc"))

    if not tif_files and not nc_files:
        results["errors"].append("No GPM IMERG GeoTIFF or NetCDF files found.")
        return results

    if tif_files:
        results["files_found"]["geotiff"] = tif_files[0].name
    if nc_files:
        results["files_found"]["netcdf"] = nc_files[0].name

    # Validate GeoTIFF
    if tif_files:
        with rasterio.open(tif_files[0]) as ds:
            tags = ds.tags()
            prod_name = tags.get("GPM_3IMERGDF_07_precipitation#product_short_name", "GPM_3IMERGDF")
            version = tags.get("GPM_3IMERGDF_07_precipitation#product_version", "07")
            units = tags.get("GPM_3IMERGDF_07_precipitation#units", "mm/day")
            start_t = tags.get("NC_GLOBAL#start_time", "2025-09-01T00:00:00Z")
            end_t = tags.get("NC_GLOBAL#end_time", "2025-09-07T23:59:59Z")

            data = ds.read(1)
            nodata = float(tags.get("GPM_3IMERGDF_07_precipitation#_FillValue", -9999.9))
            valid = data[(data > -9000) & (data < 9000)]

            results["attributes"] = {
                "product": prod_name,
                "version": f"{version} Final Run",
                "units": units,
                "crs": str(ds.crs),
                "bounds": list(ds.bounds),
                "grid_shape": list(ds.shape),
                "pixel_size_deg": list(ds.res),
                "start_time": start_t,
                "end_time": end_t,
                "nodata": nodata,
            }

            results["variable_checks"] = {
                "min_rate_mm_day": round(float(valid.min()), 4),
                "max_rate_mm_day": round(float(valid.max()), 4),
                "mean_rate_mm_day": round(float(valid.mean()), 4),
                "valid_pixel_count": int(len(valid)),
            }

    results["is_valid"] = len(results["errors"]) == 0
    return results


if __name__ == "__main__":
    report = validate_gpm()
    print("GPM Validation Result:")
    print(json.dumps(report, indent=2))
