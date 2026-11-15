"""
Landsat Collection 2 Level-2 Scene Validator.
Parses MTL metadata, checks raster consistency, validates scaling parameters and QA flags.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
import rasterio
from rasterio.warp import transform_bounds

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_LANDSAT_DIR = ROOT_DIR / "data" / "raw" / "landsat" / "extracted"

REQUIRED_BANDS = ["SR_B2", "SR_B3", "SR_B4", "SR_B5", "SR_B6", "SR_B7", "ST_B10", "QA_PIXEL"]
PILOT_BOUNDS_WGS84 = (68.2, 25.2, 68.55, 25.55)  # west, south, east, north


def parse_mtl_metadata(mtl_path: Path) -> dict[str, Any]:
    with open(mtl_path, "r", encoding="utf-8") as f:
        mtl = json.load(f)
    meta = mtl.get("LANDSAT_METADATA_FILE", {})
    img_attr = meta.get("IMAGE_ATTRIBUTES", {})
    sr_params = meta.get("LEVEL2_SURFACE_REFLECTANCE_PARAMETERS", {})
    st_params = meta.get("LEVEL2_SURFACE_TEMPERATURE_PARAMETERS", {})
    proj_attr = meta.get("PROJECTION_ATTRIBUTES", {})

    return {
        "scene_id": img_attr.get("LANDSAT_PRODUCT_ID") or meta.get("PRODUCT_CONTENTS", {}).get("LANDSAT_PRODUCT_ID"),
        "satellite": img_attr.get("SPACECRAFT_ID"),
        "sensor": img_attr.get("SENSOR_ID"),
        "acquisition_date": img_attr.get("DATE_ACQUIRED"),
        "scene_center_time": img_attr.get("SCENE_CENTER_TIME"),
        "cloud_cover_scene": float(img_attr.get("CLOUD_COVER", -1)),
        "cloud_cover_land": float(img_attr.get("CLOUD_COVER_LAND", -1)),
        "crs": f"EPSG:326{proj_attr.get('UTM_ZONE')}" if proj_attr.get("MAP_PROJECTION") == "UTM" else "UNKNOWN",
        "pixel_size": float(proj_attr.get("GRID_CELL_SIZE_REFLECTIVE", 30.0)),
        "sr_mult": float(sr_params.get("REFLECTANCE_MULT_BAND_2", 2.75e-05)),
        "sr_add": float(sr_params.get("REFLECTANCE_ADD_BAND_2", -0.2)),
        "st_mult": float(st_params.get("TEMPERATURE_MULT_BAND_ST_B10", 0.00341802)),
        "st_add": float(st_params.get("TEMPERATURE_ADD_BAND_ST_B10", 149.0)),
    }


def find_landsat_files(landsat_dir: Path) -> dict[str, Path]:
    files = {}
    for p in landsat_dir.glob("*"):
        if p.is_dir():
            continue
        fname = p.name
        if "MTL.json" in fname:
            files["MTL"] = p
        for band in REQUIRED_BANDS:
            if f"{band}.TIF" in fname or f"{band}.tif" in fname:
                files[band] = p
    return files


def validate_landsat_bundle(landsat_dir: Path = DEFAULT_LANDSAT_DIR) -> dict[str, Any]:
    results: dict[str, Any] = {
        "is_valid": False,
        "errors": [],
        "warnings": [],
        "bands_found": {},
        "missing_bands": [],
        "metadata": {},
        "raster_attributes": {},
        "pilot_qa_summary": {},
    }

    if not landsat_dir.exists():
        results["errors"].append(f"Landsat directory not found: {landsat_dir}")
        return results

    found_files = find_landsat_files(landsat_dir)

    # Check required bands
    for band in REQUIRED_BANDS:
        if band in found_files:
            results["bands_found"][band] = found_files[band].name
        else:
            results["missing_bands"].append(band)

    if "MTL" not in found_files:
        results["errors"].append("Landsat MTL metadata JSON file missing.")
    else:
        results["metadata"] = parse_mtl_metadata(found_files["MTL"])

    if results["missing_bands"]:
        results["errors"].append(f"Missing required bands: {results['missing_bands']}")
        return results

    # Verify raster dimensions and CRS consistency
    reference_shape = None
    reference_crs = None
    reference_transform = None

    for band, path in found_files.items():
        if band == "MTL":
            continue
        with rasterio.open(path) as ds:
            if reference_shape is None:
                reference_shape = ds.shape
                reference_crs = ds.crs
                reference_transform = ds.transform
                results["raster_attributes"] = {
                    "width": ds.width,
                    "height": ds.height,
                    "crs": str(ds.crs),
                    "bounds": list(ds.bounds),
                    "pixel_size": list(ds.res),
                }
            else:
                if ds.shape != reference_shape:
                    results["errors"].append(f"Band {band} shape mismatch: {ds.shape} vs {reference_shape}")
                if ds.crs != reference_crs:
                    results["errors"].append(f"Band {band} CRS mismatch: {ds.crs} vs {reference_crs}")
                if ds.transform != reference_transform:
                    results["errors"].append(f"Band {band} transform mismatch")

    # Evaluate QA_PIXEL over pilot area
    qa_path = found_files["QA_PIXEL"]
    with rasterio.open(qa_path) as qa_ds:
        utm_bounds = transform_bounds("EPSG:4326", qa_ds.crs, *PILOT_BOUNDS_WGS84)
        win = rasterio.windows.from_bounds(*utm_bounds, transform=qa_ds.transform).round_offsets().round_lengths()
        qa_data = qa_ds.read(1, window=win)

        fill_mask = (qa_data & (1 << 0)) > 0
        dilated_mask = (qa_data & (1 << 1)) > 0
        cirrus_mask = (qa_data & (1 << 2)) > 0
        cloud_mask = (qa_data & (1 << 3)) > 0
        shadow_mask = (qa_data & (1 << 4)) > 0
        water_mask = (qa_data & (1 << 7)) > 0

        invalid_mask = fill_mask | dilated_mask | cirrus_mask | cloud_mask | shadow_mask
        on_swath_pixels = int((~fill_mask).sum())
        clear_on_swath_pixels = int(((~invalid_mask) & (~fill_mask)).sum())

        clear_frac_on_swath = clear_on_swath_pixels / on_swath_pixels if on_swath_pixels > 0 else 0.0

        results["pilot_qa_summary"] = {
            "pilot_window_shape": list(qa_data.shape),
            "total_window_pixels": int(qa_data.size),
            "fill_pixels": int(fill_mask.sum()),
            "on_swath_pixels": on_swath_pixels,
            "dilated_cloud_pixels": int(dilated_mask.sum()),
            "cirrus_pixels": int(cirrus_mask.sum()),
            "cloud_pixels": int(cloud_mask.sum()),
            "cloud_shadow_pixels": int(shadow_mask.sum()),
            "water_pixels": int(water_mask.sum()),
            "cloud_free_pixels": clear_on_swath_pixels,
            "cloud_free_fraction_on_swath": round(clear_frac_on_swath, 4),
        }

    results["is_valid"] = len(results["errors"]) == 0
    return results


if __name__ == "__main__":
    validation = validate_landsat_bundle()
    print("Landsat Validation Result:")
    print(json.dumps(validation, indent=2))
