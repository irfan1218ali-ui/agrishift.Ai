"""
NASA SMAP SPL4SMGP Soil Moisture Regional Summarizer.
Aggregates regional surface and root-zone volumetric soil moisture across all observation timesteps.
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

DEFAULT_SMAP_DIR = ROOT_DIR / "data" / "raw" / "smap" / "extracted"

PROCESSED_REGIONAL_DIR = ROOT_DIR / "data" / "processed" / "regional"
PROCESSED_REGIONAL_DIR.mkdir(parents=True, exist_ok=True)


def summarize_smap(
    smap_dir: Path = DEFAULT_SMAP_DIR,
    out_dir: Path = PROCESSED_REGIONAL_DIR,
) -> dict[str, Any]:
    surf_files = sorted(list(smap_dir.glob("*sm_surface*.tif")))
    root_files = sorted(list(smap_dir.glob("*sm_rootzone*.tif")))

    if not surf_files or not root_files:
        raise FileNotFoundError("SMAP GeoTIFF files missing.")

    # Read all timesteps and aggregate valid pixels
    surf_means = []
    root_means = []

    def get_valid_mean(fpath: Path) -> float:
        with rasterio.open(fpath) as ds:
            data = ds.read(1)
            nodata = ds.nodata if ds.nodata is not None else -9999.0
            valid = data[data != nodata]
            return float(valid.mean()) if len(valid) > 0 else np.nan

    for sf in surf_files:
        surf_means.append(get_valid_mean(sf))

    for rf in root_files:
        root_means.append(get_valid_mean(rf))

    overall_surf_mean = round(float(np.nanmean(surf_means)), 4)
    overall_root_mean = round(float(np.nanmean(root_means)), 4)

    def extract_dt(fpath: Path) -> str:
        parts = fpath.stem.split("_")
        for p in parts:
            if len(p) >= 15 and "T" in p:
                return f"{p[:4]}-{p[4:6]}-{p[6:8]}T{p[9:11]}:{p[11:13]}:{p[13:15]}Z"
        return "UNKNOWN"

    obs_start = extract_dt(surf_files[0])
    obs_end = extract_dt(surf_files[-1])

    summary = {
        "dataset_id": "nasa-smap-spl4smgp-v008-hyderabad",
        "provider": "NASA",
        "product": "SPL4SMGP V008",
        "smap_surface_mean": overall_surf_mean,
        "smap_rootzone_mean": overall_root_mean,
        "smap_observation_start": obs_start,
        "smap_observation_end": obs_end,
        "smap_source_resolution": "approximately 9 km (0.078 deg EASE-Grid)",
        "units": "m^3/m^3 (volumetric soil moisture fraction)",
        "timesteps_count": len(surf_files),
        "temporal_alignment_note": "SMAP dataset dates (2026-10-01 to 2026-10-07) do not match Landsat acquisition date (2025-09-30); used strictly as regional seasonal moisture context.",
        "smap_limitation": "Regional soil-moisture context; not an exact field measurement.",
    }

    out_file = out_dir / "smap_summary.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"SMAP summary saved to {out_file.relative_to(ROOT_DIR)}")
    return summary


if __name__ == "__main__":
    summarize_smap()
