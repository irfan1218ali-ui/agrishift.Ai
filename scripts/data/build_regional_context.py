"""Aggregate real SMAP and GPM regional context without treating it as field data."""
from __future__ import annotations

import hashlib
import json
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from netCDF4 import Dataset


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SMAP = Path.home() / "Downloads" / "smap dataset"
OUT = ROOT / "data" / "processed" / "model-features" / "regional_context.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mean_smap(files: list[Path], expected: int) -> dict:
    series = []
    dates = []
    metadata = None
    for path in files:
        match = re.search(r"_(\d{8}T\d{6})_", path.name)
        if not match:
            raise ValueError(f"Cannot extract an observation timestamp from {path.name}")
        dates.append(datetime.strptime(match.group(1), "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc))
        with rasterio.open(path) as dataset:
            values = dataset.read(1, masked=True).astype(np.float64)
            if dataset.count != 1 or dataset.crs is None or not values.count():
                raise ValueError(f"SMAP raster is missing a band, CRS, or valid cells: {path.name}")
            if metadata is None:
                metadata = {"crs": str(dataset.crs), "bounds": list(dataset.bounds),
                            "resolution_degrees": list(dataset.res), "unit": dataset.tags().get("units"),
                            "shape": [dataset.height, dataset.width], "nodata": dataset.nodata}
            series.extend(values.compressed().tolist())
    if len(files) != expected:
        raise ValueError(f"Expected {expected} SMAP snapshots; found {len(files)}")
    return {"count": len(files), "valid_pixel_observations": len(series),
            "mean": float(np.mean(series)), "minimum": float(np.min(series)),
            "maximum": float(np.max(series)), "metadata": metadata,
            "observation_start_utc": min(dates).isoformat().replace("+00:00", "Z"),
            "observation_end_utc": max(dates).isoformat().replace("+00:00", "Z"),
            "source_sha256": [{"file": p.name, "sha256": sha256(p)} for p in files]}


def build(smap_dir: Path = DEFAULT_SMAP, output_path: Path = OUT) -> dict:
    surface = sorted(Path(smap_dir).glob("*_sm_surface_*.tif"))
    rootzone = sorted(Path(smap_dir).glob("*_sm_rootzone_*.tif"))
    if len(surface) != 56 or len(rootzone) != 56:
        raise FileNotFoundError(f"Expected 56 SMAP surface and root-zone files, found {len(surface)} and {len(rootzone)}")
    smap = {"surface_soil_moisture": mean_smap(surface, 56),
            "rootzone_soil_moisture": mean_smap(rootzone, 56),
            "interpretation": "regional 7-day space-time context; not a field measurement"}

    gpm_candidates = sorted((ROOT / "data" / "raw" / "gpm-imerg").glob("**/GIOVANNI-*.tif"))
    netcdf_candidates = sorted((ROOT / "data" / "raw" / "gpm-imerg").glob("**/*.nc"))
    if len(gpm_candidates) != 1 or len(netcdf_candidates) != 1:
        raise FileNotFoundError("Expected one supplied GPM average GeoTIFF and one NetCDF source")
    gpm_path, nc_path = gpm_candidates[0], netcdf_candidates[0]
    with rasterio.open(gpm_path) as dataset:
        image = dataset.read(1, masked=True).astype(np.float64)
        gpm_bounds = list(dataset.bounds)
        gpm_res = list(dataset.res)
        unit = dataset.tags().get("GPM_3IMERGDF_07_precipitation#units")
        gpm_crs = str(dataset.crs)
        gpm_values = image.compressed()
    with Dataset(nc_path) as dataset:
        variable = dataset.variables["GPM_3IMERGDF_07_precipitation"]
        global_metadata = {key: getattr(dataset, key) for key in
                           ("start_time", "end_time", "title") if hasattr(dataset, key)}
        netcdf_unit = getattr(variable, "units", None)
        if not np.ma.allequal(np.ma.masked_invalid(variable[:]), np.ma.masked_invalid(image)):
            # The two provider encodings may differ in orientation; dimensions and units are the guard here.
            if variable.shape != image.shape:
                raise ValueError("GPM GeoTIFF and NetCDF shapes disagree")
    if not gpm_values.size or unit != netcdf_unit or unit != "mm/day":
        raise ValueError("GPM precipitation values or units failed validation")
    gpm = {
        "variable": "weekly_mean_daily_precipitation_rate",
        "mean_daily_mm_per_day": float(np.mean(gpm_values)),
        "minimum_daily_mean_mm_per_day": float(np.min(gpm_values)),
        "maximum_daily_mean_mm_per_day": float(np.max(gpm_values)),
        "valid_grid_cells": int(gpm_values.size), "unit": "mm/day",
        "source_crs": gpm_crs, "bounds": gpm_bounds, "resolution_degrees": gpm_res,
        "metadata": global_metadata,
        "limitation": "Only a 7-day time-averaged map is supplied; daily series, rainy-day count, and maximum daily rainfall are unavailable.",
        "source_sha256": {"netcdf": sha256(nc_path), "geotiff": sha256(gpm_path)},
    }
    result = {
        "schema_version": "1.0", "validation_status": "validated_context_only",
        "sources": {"smap": smap, "gpm_imerg": gpm},
        "temporal_alignment": "not_aligned",
        "limitations": [
            "SMAP and GPM are coarse regional context; neither substitutes for Landsat, SRTM, or POWER field features.",
            "SMAP covers 2026-10-01 through 2026-10-07; GPM covers 2025-09-01 through 2025-09-07.",
            "The supplied GPM asset is a weekly mean daily rate, not a daily rainfall series or weekly total.",
        ],
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smap-dir", type=Path, default=DEFAULT_SMAP)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    context = build(args.smap_dir, args.output)
    print(json.dumps({"output": str(OUT), "smap": {
        key: {k: v for k, v in value.items() if k != "source_sha256"}
        for key, value in context["sources"]["smap"].items() if key != "interpretation"
    }, "gpm": context["sources"]["gpm_imerg"], "temporal_alignment": context["temporal_alignment"]}, indent=2))
