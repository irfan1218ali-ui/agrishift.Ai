"""
Real Features.json Builder.
Transforms validated pilot observations, attaches K-Means cluster assignments,
embeds regional context and climate parameters, and writes compliant data/features/features.json.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.clustering.predict import ClusterPredictor

FEATURES_DIR = ROOT_DIR / "data" / "features"
FEATURES_DIR.mkdir(parents=True, exist_ok=True)

PROCESSED_FEATURES_DIR = ROOT_DIR / "data" / "processed" / "features"
PROCESSED_CLIMATE_DIR = ROOT_DIR / "data" / "processed" / "climate"
PROCESSED_REGIONAL_DIR = ROOT_DIR / "data" / "processed" / "regional"


def build_real_features() -> dict[str, Any]:
    # 1. Load feature table
    csv_path = PROCESSED_FEATURES_DIR / "pilot_feature_table.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Feature table not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # 2. Predict K-Means clusters and distances
    predictor = ClusterPredictor()
    enriched_df = predictor.predict_dataframe(df)

    # 3. Load climate monthly distributions
    with open(PROCESSED_CLIMATE_DIR / "power_summary.json", "r", encoding="utf-8") as f:
        power_data = json.load(f)
    monthly_ind = power_data.get("monthly_indicators", {})
    with open(PROCESSED_REGIONAL_DIR / "gpm_summary.json", "r", encoding="utf-8") as f:
        gpm_data = json.load(f)

    # 4. Construct metadata
    now_str = datetime.now(timezone.utc).isoformat()
    meta = {
        "data_mode": "real",
        "feature_schema_version": "1.0",
        "processing_version": "1.0",
        "generated_at": now_str,
        "pilot_bounds": {
            "west": 68.20,
            "south": 25.20,
            "east": 68.55,
            "north": 25.55,
            "crs": "EPSG:4326",
            "region_name": "Hyderabad, Sindh, Pakistan",
        },
        "source_dates": {
            "landsat_9": "2025-09-30",
            "srtm_dem": "2000-02-11",
            "nasa_power_climate": "2015-01-01 to 2025-12-31",
            "nasa_smap": "2026-10-01 to 2026-10-07",
            "nasa_gpm_imerg": "2025-09-01 to 2025-09-07",
            "meteomatics_weather": "2026-11-15 to 2026-11-22",
        },
        "source_resolutions": {
            "landsat_9": "30 m",
            "srtm_dem": "30 m (1 arc-second)",
            "nasa_power_climate": "0.5 x 0.625 deg (~50 km)",
            "nasa_smap": "9 km EASE-Grid",
            "nasa_gpm_imerg": "0.1 deg (~10 km)",
            "meteomatics_weather": "Hourly point location",
        },
        "temporal_alignment": {
            "landsat_vs_gpm": "Both observed late monsoon September 2025",
            "landsat_vs_smap": "Seasonal offset: 2025-09 Landsat vs 2026-10 SMAP test export",
            "landsat_vs_power": "Historical 11-year climatology baseline encompasses observation year",
            "landsat_vs_meteomatics": "Historical satellite baseline vs active 7-day weather forecast",
        },
        "limitations": [
            "SMAP soil moisture represents coarse 9 km regional context; not an exact field measurement.",
            "GPM IMERG precipitation represents 0.1 deg regional satellite estimate; not an on-farm rain gauge.",
            "NASA POWER data is regional gridded climate reanalysis; not a farm-scale weather station.",
            "Landsat 9 scene acquired 2025-09-30; cloud/shadow and off-swath pixels are strictly masked.",
            "K-Means clusters represent neutral environmental groupings; do not diagnose crop health, failure, or variety suitability.",
        ],
    }

    # 5. Build point objects
    points_list = []
    for _, row in enriched_df.iterrows():
        pt_cloud_free = float(row["cloud_free_fraction"])

        pt_obj = {
            "id": str(row["id"]),
            "lat": round(float(row["lat"]), 6),
            "lon": round(float(row["lon"]), 6),
            "analysis_radius_m": int(row["analysis_radius_m"]),
            "analysis_method": str(row["analysis_method"]),
            "cluster_id": int(row["cluster_id"]),
            "cluster_label": str(row["cluster_label"]),
            "cluster_distance": round(float(row["cluster_distance"]), 4),
            "features": {
                "ndvi_mean": round(float(row["ndvi_mean"]), 4),
                "ndmi_mean": round(float(row["ndmi_mean"]), 4),
                "bsi_mean": round(float(row["bsi_mean"]), 4),
                "surface_temp_c": round(float(row["surface_temp_c"]), 2),
                "cloud_free_fraction": round(pt_cloud_free, 4),
                "elevation_m": round(float(row["elevation_m"]), 2),
                "slope_deg": round(float(row["slope_deg"]), 2),
                "low_lying_flag": bool(row["low_lying_flag"]),
                "heat_days_40c_by_month": monthly_ind.get("heat_days_40c_by_month", {}),
                "tmax_mean_by_month": monthly_ind.get("tmax_mean_by_month", {}),
                "rain_mm_by_month": monthly_ind.get("rain_mm_by_month", {}),
                "rh_mean": round(float(row["rh_mean"]), 2),
                "wind_mean": round(float(row["wind_mean"]), 2),
                "solar_radiation_mean": round(float(row["solar_radiation_mean"]), 2),
            },
            "clustering": {
                "cluster_id": int(row["cluster_id"]),
                "cluster_label": str(row["cluster_label"]),
                "cluster_distance": round(float(row["cluster_distance"]), 4),
            },
            "regional_context": {
                "smap_surface_mean": round(float(row["smap_surface_mean"]), 4),
                "smap_rootzone_mean": round(float(row["smap_rootzone_mean"]), 4),
                "gpm_mean_daily_rate_mm_day": round(float(gpm_data["mean_daily_rate_mm_day"]), 4),
            },
            "data_quality": {
                "core_sources_valid": True,
                "cloud_free_fraction": round(pt_cloud_free, 4),
                "temporal_alignment_score": 0.8,  # 4 of 5 non-forecast evidence sources align or are static/baseline
                "warnings": [
                    "SMAP data year (2026) has 1-year offset from Landsat (2025); used as regional seasonal context."
                ],
            },
        }
        points_list.append(pt_obj)

    payload = {
        "meta": meta,
        "points": points_list,
    }

    out_file = FEATURES_DIR / "features.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Built real features.json with {len(points_list)} points at {out_file.relative_to(ROOT_DIR)}")
    return payload


if __name__ == "__main__":
    build_real_features()
