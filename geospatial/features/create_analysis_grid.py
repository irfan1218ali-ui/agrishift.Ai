"""
Pilot Analysis Grid Generator and Feature Table Builder.
Creates regularly spaced spatial analysis points across the overlapping valid Landsat and SRTM terrain area,
computes 150m zonal summaries, attaches climate and regional context, and outputs pilot_feature_table.csv.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
import sys
from typing import Any
import numpy as np
import rasterio
from rasterio.transform import rowcol
from rasterio.warp import transform

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

PROCESSED_LANDSAT_DIR = ROOT_DIR / "data" / "processed" / "landsat"
PROCESSED_TERRAIN_DIR = ROOT_DIR / "data" / "processed" / "terrain"
PROCESSED_CLIMATE_DIR = ROOT_DIR / "data" / "processed" / "climate"
PROCESSED_REGIONAL_DIR = ROOT_DIR / "data" / "processed" / "regional"
PROCESSED_FEATURES_DIR = ROOT_DIR / "data" / "processed" / "features"
PROCESSED_FEATURES_DIR.mkdir(parents=True, exist_ok=True)

ANALYSIS_RADIUS_M = 150.0  # 150 m radius local circular summary


def create_analysis_grid(
    spacing_m: float = 2000.0,  # ~2.0 km grid spacing yields 149 points (within preferred 50-200 range)
    target_count_min: int = 20,
    target_count_max: int = 200,
) -> list[dict[str, Any]]:
    # Load regional context and climate summaries
    with open(PROCESSED_CLIMATE_DIR / "power_summary.json", "r", encoding="utf-8") as f:
        power_summary = json.load(f)

    with open(PROCESSED_REGIONAL_DIR / "smap_summary.json", "r", encoding="utf-8") as f:
        smap_summary = json.load(f)

    with open(PROCESSED_REGIONAL_DIR / "gpm_summary.json", "r", encoding="utf-8") as f:
        gpm_summary = json.load(f)

    # Open raster datasets
    ds_ndvi = rasterio.open(PROCESSED_LANDSAT_DIR / "ndvi.tif")
    ds_ndmi = rasterio.open(PROCESSED_LANDSAT_DIR / "ndmi.tif")
    ds_bsi = rasterio.open(PROCESSED_LANDSAT_DIR / "bsi.tif")
    ds_temp = rasterio.open(PROCESSED_LANDSAT_DIR / "surface_temperature_c.tif")
    ds_mask = rasterio.open(PROCESSED_LANDSAT_DIR / "cloud_free_mask.tif")

    ds_elev = rasterio.open(PROCESSED_TERRAIN_DIR / "elevation.tif")
    ds_slope = rasterio.open(PROCESSED_TERRAIN_DIR / "slope_degrees.tif")
    ds_low = rasterio.open(PROCESSED_TERRAIN_DIR / "low_lying_flag.tif")

    # Read arrays
    arr_ndvi = ds_ndvi.read(1)
    arr_ndmi = ds_ndmi.read(1)
    arr_bsi = ds_bsi.read(1)
    arr_temp = ds_temp.read(1)
    arr_mask = ds_mask.read(1)

    arr_elev = ds_elev.read(1)
    arr_slope = ds_slope.read(1)
    arr_low = ds_low.read(1)

    # Intersection bounds in UTM Zone 42N
    # Landsat bounds vs Terrain bounds
    b_landsat = ds_ndvi.bounds
    b_terrain = ds_elev.bounds

    min_x = max(b_landsat.left, b_terrain.left) + 2000.0  # Inset from edge
    max_x = min(b_landsat.right, b_terrain.right) - 2000.0
    min_y = max(b_landsat.bottom, b_terrain.bottom) + 2000.0
    max_y = min(b_landsat.top, b_terrain.top) - 2000.0

    # Western swath boundary adjustment:
    # Path 151 scene enters swath around UTM X ~ 432000 m
    # Ensure min_x starts within the valid swath
    min_x = max(min_x, 431000.0)

    x_coords = np.arange(min_x, max_x, spacing_m)
    y_coords = np.arange(min_y, max_y, spacing_m)

    pixel_radius = int(np.ceil(ANALYSIS_RADIUS_M / 30.0))  # ~5 pixels radius = 11x11 window

    valid_points = []
    point_idx = 1

    for y in y_coords:
        for x in x_coords:
            # Query Landsat raster
            r_l, c_l = rowcol(ds_ndvi.transform, x, y)
            # Query Terrain raster
            r_t, c_t = rowcol(ds_elev.transform, x, y)

            # Check bounds
            if (
                r_l - pixel_radius < 0
                or r_l + pixel_radius >= ds_ndvi.height
                or c_l - pixel_radius < 0
                or c_l + pixel_radius >= ds_ndvi.width
                or r_t - pixel_radius < 0
                or r_t + pixel_radius >= ds_elev.height
                or c_t - pixel_radius < 0
                or c_t + pixel_radius >= ds_elev.width
            ):
                continue

            # Circular mask for 150m radius
            y_indices, x_indices = np.ogrid[
                -pixel_radius : pixel_radius + 1, -pixel_radius : pixel_radius + 1
            ]
            circle_mask = (x_indices * 30.0) ** 2 + (y_indices * 30.0) ** 2 <= ANALYSIS_RADIUS_M**2

            # Extract Landsat window
            win_mask = arr_mask[
                r_l - pixel_radius : r_l + pixel_radius + 1,
                c_l - pixel_radius : c_l + pixel_radius + 1,
            ]
            valid_pixels = circle_mask & (win_mask == 1)

            total_circle_pixels = int(circle_mask.sum())
            valid_circle_pixels = int(valid_pixels.sum())
            cloud_free_frac = valid_circle_pixels / total_circle_pixels if total_circle_pixels > 0 else 0.0

            # Require at least 80% cloud-free and valid on-swath support
            if cloud_free_frac < 0.80 or valid_circle_pixels < 10:
                continue

            win_ndvi = arr_ndvi[
                r_l - pixel_radius : r_l + pixel_radius + 1,
                c_l - pixel_radius : c_l + pixel_radius + 1,
            ]
            win_ndmi = arr_ndmi[
                r_l - pixel_radius : r_l + pixel_radius + 1,
                c_l - pixel_radius : c_l + pixel_radius + 1,
            ]
            win_bsi = arr_bsi[
                r_l - pixel_radius : r_l + pixel_radius + 1,
                c_l - pixel_radius : c_l + pixel_radius + 1,
            ]
            win_temp = arr_temp[
                r_l - pixel_radius : r_l + pixel_radius + 1,
                c_l - pixel_radius : c_l + pixel_radius + 1,
            ]

            # Filter NoData (-9999)
            v_ndvi = win_ndvi[valid_pixels & (win_ndvi > -900)]
            v_ndmi = win_ndmi[valid_pixels & (win_ndmi > -900)]
            v_bsi = win_bsi[valid_pixels & (win_bsi > -900)]
            v_temp = win_temp[valid_pixels & (win_temp > -900)]

            if len(v_ndvi) == 0 or len(v_ndmi) == 0 or len(v_bsi) == 0 or len(v_temp) == 0:
                continue

            # Extract Terrain window
            win_elev = arr_elev[
                r_t - pixel_radius : r_t + pixel_radius + 1,
                c_t - pixel_radius : c_t + pixel_radius + 1,
            ]
            win_slope = arr_slope[
                r_t - pixel_radius : r_t + pixel_radius + 1,
                c_t - pixel_radius : c_t + pixel_radius + 1,
            ]
            win_low = arr_low[
                r_t - pixel_radius : r_t + pixel_radius + 1,
                c_t - pixel_radius : c_t + pixel_radius + 1,
            ]

            t_valid = circle_mask & (win_elev > -900)
            v_elev = win_elev[t_valid]
            v_slope = win_slope[t_valid & (win_slope > -900)]
            v_low = win_low[t_valid]

            if len(v_elev) == 0 or len(v_slope) == 0:
                continue

            # Calculate zonal means
            ndvi_m = round(float(v_ndvi.mean()), 4)
            ndmi_m = round(float(v_ndmi.mean()), 4)
            bsi_m = round(float(v_bsi.mean()), 4)
            temp_m = round(float(v_temp.mean()), 2)
            elev_m = round(float(v_elev.mean()), 2)
            slope_m = round(float(v_slope.mean()), 2)
            low_lying_bool = bool((v_low.sum() / len(v_low)) >= 0.5)

            # Convert point center from UTM 42N to WGS84 Lat/Lon
            lons, lats = transform(ds_ndvi.crs, "EPSG:4326", [x], [y])
            pt_lon = round(float(lons[0]), 6)
            pt_lat = round(float(lats[0]), 6)

            point_id = f"hyd_{point_idx:03d}"
            point_idx += 1

            valid_points.append({
                "id": point_id,
                "lat": pt_lat,
                "lon": pt_lon,
                "analysis_radius_m": int(ANALYSIS_RADIUS_M),
                "analysis_method": "local_zonal_summary",
                "ndvi_mean": ndvi_m,
                "ndmi_mean": ndmi_m,
                "bsi_mean": bsi_m,
                "surface_temp_c": temp_m,
                "cloud_free_fraction": round(cloud_free_frac, 4),
                "elevation_m": elev_m,
                "slope_deg": slope_m,
                "low_lying_flag": low_lying_bool,
                # Shared climate indicators
                "rh_mean": power_summary["overall_means"]["rh_mean_percent"],
                "wind_mean": power_summary["overall_means"]["wind_mean_ms"],
                "solar_radiation_mean": power_summary["overall_means"]["solar_radiation_mean_mj_m2_day"],
                # Regional context
                "smap_surface_mean": smap_summary["smap_surface_mean"],
                "smap_rootzone_mean": smap_summary["smap_rootzone_mean"],
                "gpm_total_mm": gpm_summary["gpm_total_mm"],
                "gpm_rainy_days": gpm_summary["gpm_rainy_days"],
                "gpm_max_daily_mm": gpm_summary["gpm_max_daily_mm"],
            })

    print(f"Generated {len(valid_points)} valid spatial analysis points.")
    return valid_points


def save_feature_table(points: list[dict[str, Any]], out_dir: Path = PROCESSED_FEATURES_DIR) -> Path:
    csv_path = out_dir / "pilot_feature_table.csv"
    if not points:
        raise ValueError("No valid points generated!")

    fieldnames = list(points[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(points)

    print(f"Feature table saved to {csv_path.relative_to(ROOT_DIR)}")
    return csv_path


def main():
    points = create_analysis_grid(spacing_m=2000.0)
    save_feature_table(points)


if __name__ == "__main__":
    main()
