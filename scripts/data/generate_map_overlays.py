"""
Real Map Layer Overlay Generator.
Reprojects processed rasters to geographic WGS84 coordinates over the pilot bounding box,
renders RGBA PNG overlays with transparent NoData, and exports metadata.json.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any
import numpy as np
from PIL import Image
import rasterio
from rasterio.warp import Resampling, reproject

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

PROCESSED_LANDSAT_DIR = ROOT_DIR / "data" / "processed" / "landsat"
PROCESSED_TERRAIN_DIR = ROOT_DIR / "data" / "processed" / "terrain"
LAYERS_DIR = ROOT_DIR / "data" / "layers"
LAYERS_DIR.mkdir(parents=True, exist_ok=True)

PILOT_BOUNDS_WGS84 = (68.20, 25.20, 68.55, 25.55)  # west, south, east, north


def reproject_to_wgs84(src_path: Path, target_bounds: tuple[float, float, float, float]) -> tuple[np.ndarray, dict]:
    """Reproject a raster to WGS84 geographic coordinates covering target_bounds."""
    with rasterio.open(src_path) as src:
        src_crs = src.crs
        src_nodata = src.nodata if src.nodata is not None else -9999.0

        # Create output transform in EPSG:4326
        # Target 800x800 resolution for web map overlay
        out_width = 800
        out_height = 800
        w, s, e, n = target_bounds

        from rasterio.transform import from_bounds
        dst_transform = from_bounds(w, s, e, n, out_width, out_height)
        dst_crs = "EPSG:4326"

        destination = np.full((out_height, out_width), -9999.0, dtype=np.float32)

        reproject(
            source=rasterio.band(src, 1),
            destination=destination,
            src_transform=src.transform,
            src_crs=src_crs,
            src_nodata=src_nodata,
            dst_transform=dst_transform,
            dst_crs=dst_crs,
            dst_nodata=-9999.0,
            resampling=Resampling.bilinear,
        )

        return destination, {
            "bounds": {"west": w, "south": s, "east": e, "north": n},
            "shape": (out_height, out_width),
        }


def colormap_ndvi(arr: np.ndarray, nodata: float = -9999.0) -> np.ndarray:
    """Render NDVI using green-yellow-brown palette with transparent NoData."""
    rgba = np.zeros((*arr.shape, 4), dtype=np.uint8)
    valid = (arr != nodata) & (~np.isnan(arr))

    # Scale between -0.2 and 0.8
    norm = np.clip((arr - (-0.2)) / (0.8 - (-0.2)), 0.0, 1.0)

    # Low NDVI (water/bare/built): Brown/Tan [165, 120, 80]
    # Mid-low NDVI (sparse vegetation): Yellow [235, 220, 100]
    # Mid-high NDVI (moderate vegetation): Light Green [130, 200, 80]
    # High NDVI (dense vegetation): Dark Green [20, 115, 35]
    r = np.zeros_like(arr, dtype=np.float32)
    g = np.zeros_like(arr, dtype=np.float32)
    b = np.zeros_like(arr, dtype=np.float32)

    # Segment 1: 0.0 - 0.35 (Brown to Yellow)
    m1 = valid & (norm <= 0.35)
    t1 = norm[m1] / 0.35
    r[m1] = 165 + (235 - 165) * t1
    g[m1] = 120 + (220 - 120) * t1
    b[m1] = 80 + (100 - 80) * t1

    # Segment 2: 0.35 - 0.70 (Yellow to Light Green)
    m2 = valid & (norm > 0.35) & (norm <= 0.70)
    t2 = (norm[m2] - 0.35) / 0.35
    r[m2] = 235 + (130 - 235) * t2
    g[m2] = 220 + (200 - 220) * t2
    b[m2] = 100 + (80 - 100) * t2

    # Segment 3: 0.70 - 1.0 (Light Green to Dark Green)
    m3 = valid & (norm > 0.70)
    t3 = (norm[m3] - 0.70) / 0.30
    r[m3] = 130 + (20 - 130) * t3
    g[m3] = 200 + (115 - 200) * t3
    b[m3] = 80 + (35 - 80) * t3

    rgba[..., 0] = np.clip(r, 0, 255).astype(np.uint8)
    rgba[..., 1] = np.clip(g, 0, 255).astype(np.uint8)
    rgba[..., 2] = np.clip(b, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.where(valid, 210, 0).astype(np.uint8)  # 210 opacity for visible overlay, 0 for nodata
    return rgba


def colormap_ndmi(arr: np.ndarray, nodata: float = -9999.0) -> np.ndarray:
    """Render NDMI moisture index using red-amber-cyan-blue palette."""
    rgba = np.zeros((*arr.shape, 4), dtype=np.uint8)
    valid = (arr != nodata) & (~np.isnan(arr))

    norm = np.clip((arr - (-0.3)) / (0.5 - (-0.3)), 0.0, 1.0)

    # Dry: Orange/Tan [210, 140, 70] -> Cyan [120, 215, 220] -> Dark Blue [25, 75, 180]
    r = np.zeros_like(arr, dtype=np.float32)
    g = np.zeros_like(arr, dtype=np.float32)
    b = np.zeros_like(arr, dtype=np.float32)

    m1 = valid & (norm <= 0.5)
    t1 = norm[m1] / 0.5
    r[m1] = 210 + (120 - 210) * t1
    g[m1] = 140 + (215 - 140) * t1
    b[m1] = 70 + (220 - 70) * t1

    m2 = valid & (norm > 0.5)
    t2 = (norm[m2] - 0.5) / 0.5
    r[m2] = 120 + (25 - 120) * t2
    g[m2] = 215 + (75 - 215) * t2
    b[m2] = 220 + (180 - 220) * t2

    rgba[..., 0] = np.clip(r, 0, 255).astype(np.uint8)
    rgba[..., 1] = np.clip(g, 0, 255).astype(np.uint8)
    rgba[..., 2] = np.clip(b, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.where(valid, 210, 0).astype(np.uint8)
    return rgba


def colormap_bsi(arr: np.ndarray, nodata: float = -9999.0) -> np.ndarray:
    """Render Bare Soil Index using vegetated (green) to high-bare (warm brown/amber)."""
    rgba = np.zeros((*arr.shape, 4), dtype=np.uint8)
    valid = (arr != nodata) & (~np.isnan(arr))

    norm = np.clip((arr - (-0.3)) / (0.3 - (-0.3)), 0.0, 1.0)

    # Low bare (dense crop): Green [45, 140, 60] -> Neutral [225, 210, 160] -> High bare: Dark Amber [160, 85, 30]
    r = np.zeros_like(arr, dtype=np.float32)
    g = np.zeros_like(arr, dtype=np.float32)
    b = np.zeros_like(arr, dtype=np.float32)

    m1 = valid & (norm <= 0.5)
    t1 = norm[m1] / 0.5
    r[m1] = 45 + (225 - 45) * t1
    g[m1] = 140 + (210 - 140) * t1
    b[m1] = 60 + (160 - 60) * t1

    m2 = valid & (norm > 0.5)
    t2 = (norm[m2] - 0.5) / 0.5
    r[m2] = 225 + (160 - 225) * t2
    g[m2] = 210 + (85 - 210) * t2
    b[m2] = 160 + (30 - 160) * t2

    rgba[..., 0] = np.clip(r, 0, 255).astype(np.uint8)
    rgba[..., 1] = np.clip(g, 0, 255).astype(np.uint8)
    rgba[..., 2] = np.clip(b, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.where(valid, 210, 0).astype(np.uint8)
    return rgba


def colormap_slope(arr: np.ndarray, nodata: float = -9999.0) -> np.ndarray:
    """Render Terrain Slope (degrees) using beige (flat 0-2 deg) to dark orange/crimson (steep >10 deg)."""
    rgba = np.zeros((*arr.shape, 4), dtype=np.uint8)
    valid = (arr != nodata) & (~np.isnan(arr))

    norm = np.clip(arr / 12.0, 0.0, 1.0)  # Max scale at 12 degrees

    # 0 deg: Cream [245, 240, 220] -> 5 deg: Amber [230, 150, 60] -> 12+ deg: Crimson [160, 30, 30]
    r = np.zeros_like(arr, dtype=np.float32)
    g = np.zeros_like(arr, dtype=np.float32)
    b = np.zeros_like(arr, dtype=np.float32)

    m1 = valid & (norm <= 0.4)
    t1 = norm[m1] / 0.4
    r[m1] = 245 + (230 - 245) * t1
    g[m1] = 240 + (150 - 240) * t1
    b[m1] = 220 + (60 - 220) * t1

    m2 = valid & (norm > 0.4)
    t2 = (norm[m2] - 0.4) / 0.6
    r[m2] = 230 + (160 - 230) * t2
    g[m2] = 150 + (30 - 150) * t2
    b[m2] = 60 + (30 - 60) * t2

    rgba[..., 0] = np.clip(r, 0, 255).astype(np.uint8)
    rgba[..., 1] = np.clip(g, 0, 255).astype(np.uint8)
    rgba[..., 2] = np.clip(b, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.where(valid, 200, 0).astype(np.uint8)
    return rgba


def generate_overlays(out_dir: Path = LAYERS_DIR) -> dict[str, Any]:
    # 1. Reproject rasters to WGS84
    ndvi_arr, info = reproject_to_wgs84(PROCESSED_LANDSAT_DIR / "ndvi.tif", PILOT_BOUNDS_WGS84)
    ndmi_arr, _ = reproject_to_wgs84(PROCESSED_LANDSAT_DIR / "ndmi.tif", PILOT_BOUNDS_WGS84)
    bsi_arr, _ = reproject_to_wgs84(PROCESSED_LANDSAT_DIR / "bsi.tif", PILOT_BOUNDS_WGS84)
    slope_arr, _ = reproject_to_wgs84(PROCESSED_TERRAIN_DIR / "slope_degrees.tif", PILOT_BOUNDS_WGS84)

    # 2. Render RGBA PNGs
    ndvi_rgba = colormap_ndvi(ndvi_arr)
    ndmi_rgba = colormap_ndmi(ndmi_arr)
    bsi_rgba = colormap_bsi(bsi_arr)
    slope_rgba = colormap_slope(slope_arr)

    Image.fromarray(ndvi_rgba, mode="RGBA").save(out_dir / "ndvi.png", "PNG")
    Image.fromarray(ndmi_rgba, mode="RGBA").save(out_dir / "ndmi.png", "PNG")
    Image.fromarray(bsi_rgba, mode="RGBA").save(out_dir / "bsi.png", "PNG")
    Image.fromarray(slope_rgba, mode="RGBA").save(out_dir / "slope.png", "PNG")

    # 3. Calculate actual min/max of valid data
    def get_min_max(arr: np.ndarray) -> tuple[float, float]:
        v = arr[(arr != -9999.0) & (~np.isnan(arr))]
        return (round(float(v.min()), 4), round(float(v.max()), 4)) if len(v) > 0 else (0.0, 0.0)

    ndvi_min, ndvi_max = get_min_max(ndvi_arr)
    ndmi_min, ndmi_max = get_min_max(ndmi_arr)
    bsi_min, bsi_max = get_min_max(bsi_arr)
    slope_min, slope_max = get_min_max(slope_arr)

    # 4. Construct metadata.json
    metadata = {
        "bounds": info["bounds"],
        "layers": {
            "ndvi": {
                "file": "ndvi.png",
                "provider": "USGS/NASA",
                "product": "Landsat Collection 2 Level-2",
                "observation_date": "2025-09-30",
                "source_resolution_m": 30,
                "unit": "index",
                "minimum": ndvi_min,
                "maximum": ndvi_max,
                "color_scale": "Brown (-0.2, non-vegetated) -> Yellow (sparse) -> Green (dense canopy 0.8)",
                "limitation": "Cloud-masked satellite observation; off-swath and cloudy pixels rendered fully transparent.",
            },
            "ndmi": {
                "file": "ndmi.png",
                "provider": "USGS/NASA",
                "product": "Landsat Collection 2 Level-2",
                "observation_date": "2025-09-30",
                "source_resolution_m": 30,
                "unit": "index",
                "minimum": ndmi_min,
                "maximum": ndmi_max,
                "color_scale": "Orange (-0.3, moisture stress) -> Cyan (moderate) -> Blue (high moisture 0.5)",
                "limitation": "Reflects canopy water content and open water surfaces on date of overpass.",
            },
            "bsi": {
                "file": "bsi.png",
                "provider": "USGS/NASA",
                "product": "Landsat Collection 2 Level-2",
                "observation_date": "2025-09-30",
                "source_resolution_m": 30,
                "unit": "index",
                "minimum": bsi_min,
                "maximum": bsi_max,
                "color_scale": "Green (-0.3, vegetated/non-bare) -> Cream (intermediate) -> Dark Amber (0.3, exposed soil)",
                "limitation": "Identifies bare soil and fallow fields; sensitivity depends on surface soil moisture and crop residue.",
            },
            "slope": {
                "file": "slope.png",
                "provider": "NASA/USGS",
                "product": "SRTMGL1 V003",
                "observation_date": "2000-02-11",
                "source_resolution_m": 30,
                "unit": "degrees",
                "minimum": slope_min,
                "maximum": slope_max,
                "color_scale": "Cream (0-2 deg, flat alluvial plains) -> Amber (2-5 deg) -> Crimson (>10 deg, embankments)",
                "limitation": "Derived from 30m radar elevation model; micro-topography below 30m resolution is smoothed.",
            },
        },
    }

    meta_path = out_dir / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Map layers and metadata successfully generated in {out_dir.relative_to(ROOT_DIR)}")
    return metadata


if __name__ == "__main__":
    generate_overlays()
