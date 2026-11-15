"""
NASA SMAP SPL4SMGP V008 Validator.
Validates surface and root-zone soil moisture GeoTIFFs, dimensions, CRS, and dates.
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

DEFAULT_SMAP_DIR = ROOT_DIR / "data" / "raw" / "smap" / "extracted"


def validate_smap(smap_dir: Path = DEFAULT_SMAP_DIR) -> dict[str, Any]:
    results: dict[str, Any] = {
        "is_valid": False,
        "errors": [],
        "warnings": [],
        "file_counts": {},
        "attributes": {},
        "temporal_coverage": {},
        "variable_checks": {},
    }

    if not smap_dir.exists():
        results["errors"].append(f"SMAP directory not found: {smap_dir}")
        return results

    surf_files = sorted(list(smap_dir.glob("*sm_surface*.tif")))
    root_files = sorted(list(smap_dir.glob("*sm_rootzone*.tif")))
    geojson_files = list(smap_dir.glob("*.geojson"))

    results["file_counts"] = {
        "surface_tifs": len(surf_files),
        "rootzone_tifs": len(root_files),
        "geojson_files": len(geojson_files),
    }

    if not surf_files or not root_files:
        results["errors"].append("Missing surface or root-zone SMAP GeoTIFF files.")
        return results

    # Sample raster checks
    with rasterio.open(surf_files[0]) as ds:
        results["attributes"] = {
            "crs": str(ds.crs),
            "bounds": list(ds.bounds),
            "shape": list(ds.shape),
            "pixel_size_deg": list(ds.res),
            "nodata": ds.nodata,
            "units": "m^3/m^3",
        }

    # Date extraction
    def extract_dt(fpath: Path) -> str:
        parts = fpath.stem.split("_")
        for p in parts:
            if len(p) >= 15 and "T" in p:
                return f"{p[:4]}-{p[4:6]}-{p[6:8]}T{p[9:11]}:{p[11:13]}:{p[13:15]}Z"
        return "UNKNOWN"

    surf_start = extract_dt(surf_files[0])
    surf_end = extract_dt(surf_files[-1])
    root_start = extract_dt(root_files[0])
    root_end = extract_dt(root_files[-1])

    results["temporal_coverage"] = {
        "surface_start": surf_start,
        "surface_end": surf_end,
        "rootzone_start": root_start,
        "rootzone_end": root_end,
        "timesteps_per_variable": len(surf_files),
    }

    # Verify value ranges
    sample_surf = rasterio.open(surf_files[0]).read(1)
    sample_root = rasterio.open(root_files[0]).read(1)
    nodata = results["attributes"]["nodata"]

    v_surf = sample_surf[sample_surf != nodata]
    v_root = sample_root[sample_root != nodata]

    results["variable_checks"] = {
        "sample_surface_min": round(float(v_surf.min()), 4),
        "sample_surface_max": round(float(v_surf.max()), 4),
        "sample_rootzone_min": round(float(v_root.min()), 4),
        "sample_rootzone_max": round(float(v_root.max()), 4),
        "realistic_volumetric_range": bool(0.0 <= v_surf.min() and v_surf.max() <= 0.6),
    }

    results["is_valid"] = len(results["errors"]) == 0
    return results


if __name__ == "__main__":
    report = validate_smap()
    print("SMAP Validation Result:")
    print(json.dumps(report, indent=2))
