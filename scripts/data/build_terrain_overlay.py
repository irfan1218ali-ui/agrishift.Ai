"""Build a reprojection-aware SRTM slope raster and small map overlay."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject


ROOT = Path(__file__).resolve().parents[2]
SOURCE_GLOB = "data/raw/terrain/**/SRTMGL1_NC.003_SRTMGL1_DEM_*.tif"
PROJECTED_CRS = "EPSG:32642"  # UTM zone 42N, covering Hyderabad, Sindh.
NODATA = -9999.0
PROCESSING_VERSION = "slope-v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(source_path: Path = None, output_root: Path = ROOT) -> dict:
    output_root = Path(output_root)
    candidates = [Path(p) for p in sorted(output_root.glob(SOURCE_GLOB))]
    if source_path is None:
        if len(candidates) != 1:
            raise FileNotFoundError(f"Expected one SRTM DEM, discovered {len(candidates)}")
        source_path = candidates[0]
    source_path = Path(source_path)
    terrain_dir = output_root / "data" / "processed" / "terrain"
    layer_dir = output_root / "data" / "layers"
    terrain_dir.mkdir(parents=True, exist_ok=True)
    layer_dir.mkdir(parents=True, exist_ok=True)
    projected_path = terrain_dir / "slope_projected.tif"
    slope_path = terrain_dir / "slope_deg.tif"
    png_path = layer_dir / "slope.png"

    with rasterio.open(source_path) as src:
        dem = src.read(1).astype(np.float32)
        source_nodata = src.nodata
        if source_nodata is not None:
            dem[dem == source_nodata] = np.nan
        transform, width, height = calculate_default_transform(
            src.crs, PROJECTED_CRS, src.width, src.height, *src.bounds, resolution=30
        )
        projected = np.full((height, width), np.nan, dtype=np.float32)
        reproject(
            source=dem, destination=projected, src_transform=src.transform, src_crs=src.crs,
            src_nodata=np.nan, dst_transform=transform, dst_crs=PROJECTED_CRS,
            dst_nodata=np.nan, resampling=Resampling.bilinear,
        )
        dy, dx = abs(transform.e), abs(transform.a)
        dz_dy, dz_dx = np.gradient(projected, dy, dx)
        slope_projected = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy))).astype(np.float32)
        slope_projected[~np.isfinite(projected)] = NODATA
        projected_profile = {
            "driver": "GTiff", "height": height, "width": width, "count": 1,
            "dtype": "float32", "crs": PROJECTED_CRS, "transform": transform,
            "nodata": NODATA, "compress": "deflate", "predictor": 3,
        }
        with rasterio.open(projected_path, "w", **projected_profile) as dst:
            dst.write(slope_projected, 1)
            dst.update_tags(units="degrees", method="slope_from_utm_gradient", processing_version=PROCESSING_VERSION)

        slope_geo = np.full((src.height, src.width), NODATA, dtype=np.float32)
        reproject(
            source=slope_projected, destination=slope_geo, src_transform=transform, src_crs=PROJECTED_CRS,
            src_nodata=NODATA, dst_transform=src.transform, dst_crs=src.crs,
            dst_nodata=NODATA, resampling=Resampling.bilinear,
        )
        geographic_profile = src.profile.copy()
        geographic_profile.update(driver="GTiff", dtype="float32", count=1, nodata=NODATA,
                                  compress="deflate", predictor=3)
        with rasterio.open(slope_path, "w", **geographic_profile) as dst:
            dst.write(slope_geo, 1)
            dst.update_tags(units="degrees", method="slope_from_utm_gradient", processing_version=PROCESSING_VERSION)
        bounds = [float(src.bounds.left), float(src.bounds.bottom),
                  float(src.bounds.right), float(src.bounds.top)]
        crs = str(src.crs)
        resolution = [float(abs(src.transform.a)), float(abs(src.transform.e))]

    valid = np.isfinite(slope_geo) & (slope_geo != NODATA)
    values = slope_geo[valid]
    if not values.size:
        raise ValueError("Slope output contains no valid cells")
    low, high = [float(v) for v in np.percentile(values, [2, 98])]
    if high <= low:
        high = low + 1.0
    normalized = np.clip((np.where(valid, slope_geo, low) - low) / (high - low), 0.0, 1.0)
    stops = np.array([[36, 116, 92], [231, 208, 108], [142, 68, 40]], dtype=np.float32)
    idx = np.minimum((normalized * 2).astype(np.int32), 1)
    fraction = normalized * 2 - idx
    rgb = (stops[idx] * (1 - fraction[..., None]) + stops[idx + 1] * fraction[..., None]).astype(np.uint8)
    rgba = np.dstack((rgb, np.where(valid, 220, 0).astype(np.uint8)))
    Image.fromarray(rgba, mode="RGBA").save(png_path, optimize=True)

    metadata_path = layer_dir / "metadata.json"
    metadata = {"schema_version": "1.0", "processing_version": PROCESSING_VERSION,
                "layers": {}}
    if metadata_path.is_file():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata.setdefault("layers", {})
    metadata["layers"]["slope"] = {
        "image": "slope.png", "bounds": {"west": bounds[0], "south": bounds[1],
                                            "east": bounds[2], "north": bounds[3]},
        "source": "NASA SRTMGL1 V003 DEM", "observation_date": "2000-02-11",
        "resolution_degrees": resolution, "source_crs": crs, "unit": "degrees",
        "color_scale_degrees_p02_p98": [low, high], "nodata": "transparent",
        "processing_version": PROCESSING_VERSION,
        "limitations": ["Slope is derived terrain context; it is not a drainage or waterlogging diagnosis."],
        "source_sha256": sha256(source_path),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {"source": str(source_path), "slope_raster": str(slope_path), "overlay": str(png_path),
            "metadata": str(metadata_path), "valid_pixels": int(values.size),
            "minimum_degrees": float(values.min()), "maximum_degrees": float(values.max()),
            "mean_degrees": float(values.mean()), "scale_p02_p98": [low, high],
            "source_sha256": sha256(source_path)}


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
