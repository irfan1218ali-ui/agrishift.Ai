"""Summarize the supplied weekly time-averaged GPM daily precipitation rate."""

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
PROCESSED_REGIONAL_DIR = ROOT_DIR / "data" / "processed" / "regional"
PROCESSED_REGIONAL_DIR.mkdir(parents=True, exist_ok=True)


def summarize_gpm(
    gpm_dir: Path = DEFAULT_GPM_DIR,
    out_dir: Path = PROCESSED_REGIONAL_DIR,
) -> dict[str, Any]:
    tif_files = list(gpm_dir.glob("*.tif"))
    if not tif_files:
        raise FileNotFoundError("GPM GeoTIFF file missing.")

    tif_path = tif_files[0]
    with rasterio.open(tif_path) as ds:
        tags = ds.tags()
        start_time = tags.get("NC_GLOBAL#start_time", "2025-09-01T00:00:00Z")
        end_time = tags.get("NC_GLOBAL#end_time", "2025-09-07T23:59:59Z")

        data = ds.read(1)
        valid = data[(data > -9000) & (data < 9000)]

    # Giovanni timeAvgMap is one weekly mean daily rate map, not daily observations.
    mean_daily_rate = float(valid.mean())
    min_grid_daily_rate = float(valid.min())
    max_grid_daily_rate = float(valid.max())

    summary = {
        "dataset_id": "nasa-gpm-3imergdf-v07-hyderabad",
        "provider": "NASA / JAXA",
        "product": "GPM_3IMERGDF V07 Final Run",
        "gpm_observation_start": start_time,
        "gpm_observation_end": end_time,
        "gpm_source_resolution": "0.1 deg (~10 km)",
        "mean_daily_rate_mm_day": round(mean_daily_rate, 4),
        "minimum_cell_mean_daily_rate_mm_day": round(min_grid_daily_rate, 4),
        "maximum_cell_mean_daily_rate_mm_day": round(max_grid_daily_rate, 4),
        "days_in_period": 7,
        "gpm_limitation": "Regional satellite estimate, not a field rain gauge. Weekly time-averaged daily rate; daily totals, rainy-day counts, and maximum daily rainfall are unavailable.",
    }

    out_file = out_dir / "gpm_summary.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"GPM summary saved to {out_file.relative_to(ROOT_DIR)}")
    return summary


if __name__ == "__main__":
    summarize_gpm()
