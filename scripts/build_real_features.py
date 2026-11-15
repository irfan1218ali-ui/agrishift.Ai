"""Build complete point features from real Landsat, SRTM, POWER, SMAP and GPM assets.

This script fails closed when critical Landsat inputs are missing. It never reads
features.example.json and never writes a partial/fabricated real feature file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform, transform_bounds

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.api.app.power import summarize_csv  # noqa: E402

LANDSAT_FILES = {name: f"*_SR_B{band}.TIF" for name, band in
                 (("blue", 2), ("green", 3), ("red", 4), ("nir", 5),
                  ("swir1", 6), ("swir2", 7))}
LANDSAT_FILES.update({"temperature": "*_ST_B10.TIF", "qa_pixel": "*_QA_PIXEL.TIF"})
SR_BAND_NUMBERS = {"blue": 2, "green": 3, "red": 4, "nir": 5, "swir1": 6, "swir2": 7}
QA_EXCLUDE_BITS = sum(1 << bit for bit in range(6))  # fill, dilated cloud, cirrus, cloud, shadow, snow
PILOT = (25.1, 25.7, 68.1, 68.7)  # min lat, max lat, min lon, max lon; Hyderabad pilot.
PROCESSING_VERSION = "landsat-features-v1"
EXPECTED_LANDSAT_PRODUCT = "LC08_L2SP_151043_20250922_20250930_02_T1"


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scale_reflectance(dn: np.ndarray, multiplier: float, addend: float) -> np.ndarray:
    return np.asarray(dn, dtype=np.float64) * multiplier + addend


def scale_temperature_c(dn: np.ndarray, multiplier: float, addend: float) -> np.ndarray:
    return np.asarray(dn, dtype=np.float64) * multiplier + addend - 273.15


def qa_clear(qa: np.ndarray) -> np.ndarray:
    return (np.asarray(qa, dtype=np.uint16) & QA_EXCLUDE_BITS) == 0


def spectral_indices(blue: np.ndarray, red: np.ndarray, nir: np.ndarray,
                     swir1: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ndvi_denom = nir + red
    ndmi_denom = nir + swir1
    bsi_denom = swir1 + red + nir + blue
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = np.divide(nir - red, ndvi_denom,
                         out=np.full_like(ndvi_denom, np.nan, dtype=np.float64), where=ndvi_denom != 0)
        ndmi = np.divide(nir - swir1, ndmi_denom,
                         out=np.full_like(ndmi_denom, np.nan, dtype=np.float64), where=ndmi_denom != 0)
        bsi = np.divide((swir1 + red) - (nir + blue), bsi_denom,
                        out=np.full_like(bsi_denom, np.nan, dtype=np.float64), where=bsi_denom != 0)
    return ndvi, ndmi, bsi


def parse_mtl(path: Path) -> dict[str, str]:
    text = Path(path).read_text(encoding="utf-8", errors="strict")
    return {key: value.strip().strip('"') for key, value in re.findall(
        r"^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$", text, flags=re.MULTILINE)}


def resolve_landsat(scene_dir: Path) -> tuple[dict[str, Path], Path, dict[str, str]]:
    scene_dir = Path(scene_dir)
    if not scene_dir.is_dir():
        raise FileNotFoundError(f"Landsat scene directory is missing: {scene_dir}")
    assets: dict[str, Path] = {}
    for key, pattern in LANDSAT_FILES.items():
        matches = sorted(scene_dir.rglob(pattern))
        if len(matches) != 1:
            raise FileNotFoundError(f"Expected one Landsat {key} asset ({pattern}); discovered {len(matches)}")
        assets[key] = matches[0]
    mtls = sorted(scene_dir.rglob("*_MTL.txt"))
    if len(mtls) != 1:
        raise FileNotFoundError(f"Expected one Landsat MTL metadata file; discovered {len(mtls)}")
    return assets, mtls[0], parse_mtl(mtls[0])


def scale_parameters(mtl: dict[str, str]) -> tuple[dict[str, tuple[float, float]], tuple[float, float]]:
    reflectance = {}
    for name, band in SR_BAND_NUMBERS.items():
        mult_key, add_key = f"REFLECTANCE_MULT_BAND_{band}", f"REFLECTANCE_ADD_BAND_{band}"
        if mult_key not in mtl or add_key not in mtl:
            raise ValueError(f"MTL is missing Landsat scale/offset keys for band {band}")
        reflectance[name] = (float(mtl[mult_key]), float(mtl[add_key]))
    temp_keys = ("TEMPERATURE_MULT_BAND_ST_B10", "TEMPERATURE_ADD_BAND_ST_B10")
    if any(key not in mtl for key in temp_keys):
        raise ValueError("MTL is missing the ST_B10 scale/offset keys")
    temperature = tuple(float(mtl[key]) for key in temp_keys)
    return reflectance, temperature


def parse_power_header(path: Path) -> dict:
    header = []
    with Path(path).open(encoding="utf-8-sig") as source:
        for line in source:
            if line.strip() == "-END HEADER-":
                break
            header.append(line.strip())
    text = "\n".join(header)
    dates = re.search(r"Dates \(month/day/year\):\s*(\d{2}/\d{2}/\d{4}) through (\d{2}/\d{2}/\d{4})", text)
    location = re.search(r"Location:\s*latitude\s+(-?\d+(?:\.\d+)?)\s+longitude\s+(-?\d+(?:\.\d+)?)", text)
    if not dates or not location or "-999" not in text:
        raise ValueError("NASA POWER CSV header is missing dates, coordinates, or fill-value metadata")
    return {"date_start": dates.group(1), "date_end": dates.group(2),
            "latitude": float(location.group(1)), "longitude": float(location.group(2)),
            "missing_value": -999.0}


def assert_aligned(assets: dict[str, Path]) -> dict[str, dict]:
    reference = None
    profiles = {}
    for name, path in assets.items():
        with rasterio.open(path) as src:
            if src.count != 1 or src.crs is None:
                raise ValueError(f"Landsat asset must have one band and a CRS: {path.name}")
            signature = (src.width, src.height, src.crs, src.transform)
            if reference is None:
                reference = signature
            elif signature != reference:
                raise ValueError(f"Landsat assets do not share a grid: {path.name}")
            if name == "red" and (not src.crs.is_projected or src.crs.linear_units.lower() not in ("metre", "meter")):
                raise ValueError("Landsat source must use a projected CRS measured in metres")
            profiles[name] = {"crs": str(src.crs), "bounds": [float(v) for v in src.bounds],
                              "resolution": [float(abs(src.transform.a)), float(abs(src.transform.e))],
                              "nodata": src.nodata, "width": src.width, "height": src.height}
    return profiles


def _sample_terrain(path: Path, x: float, y: float, src_crs) -> float | None:
    with rasterio.open(path) as src:
        tx, ty = transform(src_crs, src.crs, [x], [y])
        value = next(src.sample([(tx[0], ty[0])]))[0]
        if src.nodata is not None and value == src.nodata:
            return None
        return float(value) if np.isfinite(value) else None


def _window_values(src, assets: dict[str, Path], reflectance_scales: dict,
                   temp_scale: tuple[float, float], x: float, y: float,
                   radius_m: float) -> tuple[dict, float]:
    top_left = src.index(x - radius_m, y + radius_m)
    bottom_right = src.index(x + radius_m, y - radius_m)
    r0, r1 = max(0, min(top_left[0], bottom_right[0])), min(src.height, max(top_left[0], bottom_right[0]) + 1)
    c0, c1 = max(0, min(top_left[1], bottom_right[1])), min(src.width, max(top_left[1], bottom_right[1]) + 1)
    if r1 <= r0 or c1 <= c0:
        return {}, 0.0
    slices = (slice(r0, r1), slice(c0, c1))
    qa_path = assets["qa_pixel"]
    with rasterio.open(qa_path) as dataset:
        qa = dataset.read(1)[slices]
        qa_good = qa_clear(qa)
    raw, masks = {}, []
    for name, path in assets.items():
        if name == "qa_pixel":
            continue
        with rasterio.open(path) as dataset:
            band = dataset.read(1, masked=True)[slices]
            raw[name] = np.asarray(band.data, dtype=np.float64)
            mask = np.ma.getmaskarray(band) | (band.data <= 0)
            masks.append(mask)
    common = qa_good & ~np.logical_or.reduce(masks)
    cloud_fraction = float(common.sum() / common.size) if common.size else 0.0
    if not common.any():
        return {}, cloud_fraction
    reflectance = {name: scale_reflectance(raw[name], *reflectance_scales[name])
                   for name in SR_BAND_NUMBERS}
    ndvi, ndmi, bsi = spectral_indices(reflectance["blue"], reflectance["red"],
                                       reflectance["nir"], reflectance["swir1"])
    temp_c = scale_temperature_c(raw["temperature"], *temp_scale)
    result = {}
    for name, values in (("ndvi_mean", ndvi), ("ndmi_mean", ndmi),
                         ("bsi_mean", bsi), ("surface_temp_c", temp_c)):
        valid = common & np.isfinite(values)
        if not valid.any():
            return {}, cloud_fraction
        result[name] = float(np.mean(values[valid]))
    return result, cloud_fraction


def build(scene_dir: Path, dem_path: Path | None, slope_path: Path, power_csv: Path,
          regional_context_path: Path, output_path: Path, spacing_m: int = 180,
          radius_m: int = 75, min_cloud_free: float = 0.5) -> dict:
    assets, mtl_path, mtl = resolve_landsat(scene_dir)
    if mtl.get("LANDSAT_PRODUCT_ID") != EXPECTED_LANDSAT_PRODUCT:
        raise ValueError(f"Unexpected Landsat product; expected {EXPECTED_LANDSAT_PRODUCT}")
    profiles = assert_aligned(assets)
    reflectance_scales, temp_scale = scale_parameters(mtl)
    if dem_path is None:
        dem_candidates = sorted((ROOT / "data" / "raw" / "terrain").rglob("SRTMGL1_NC.003_SRTMGL1_DEM_*.tif"))
        if len(dem_candidates) != 1:
            raise FileNotFoundError(f"Expected one real SRTM DEM; discovered {len(dem_candidates)}")
        dem_path = dem_candidates[0]
    if not Path(dem_path).is_file() or not Path(slope_path).is_file():
        raise FileNotFoundError("A real SRTM DEM and its processed slope raster are required")
    power = summarize_csv(power_csv)
    if not power:
        raise ValueError("NASA POWER CSV did not yield complete monthly climate summaries")
    power_header = parse_power_header(power_csv)
    context = json.loads(Path(regional_context_path).read_text(encoding="utf-8"))
    if context.get("validation_status") != "validated_context_only":
        raise ValueError("SMAP/GPM regional context has not passed validation")

    points = []
    with rasterio.open(assets["red"]) as src:
        if src.transform.b != 0 or src.transform.d != 0:
            raise ValueError("Rotated Landsat grids are not supported by the square-window sampler")
        min_lat, max_lat, min_lon, max_lon = PILOT
        left, bottom, right, top = transform_bounds("EPSG:4326", src.crs,
                                                    min_lon, min_lat, max_lon, max_lat, densify_pts=21)
        intersection = (max(left, src.bounds.left), max(bottom, src.bounds.bottom),
                        min(right, src.bounds.right), min(top, src.bounds.top))
        if intersection[0] >= intersection[2] or intersection[1] >= intersection[3]:
            raise ValueError("Landsat scene does not intersect the Hyderabad pilot extent")
        step = max(1, int(round(spacing_m / min(abs(src.transform.a), abs(src.transform.e)))))
        row_start, col_start = src.index(intersection[0], intersection[3])
        row_end, col_end = src.index(intersection[2], intersection[1])
        for row in range(max(0, row_start) + step // 2, min(src.height, row_end + 1), step):
            for col in range(max(0, col_start) + step // 2, min(src.width, col_end + 1), step):
                x, y = src.xy(row, col)
                values, cloud_free = _window_values(src, assets, reflectance_scales,
                                                    temp_scale, x, y, radius_m)
                if not values or cloud_free < min_cloud_free:
                    continue
                elevation = _sample_terrain(dem_path, x, y, src.crs)
                slope = _sample_terrain(slope_path, x, y, src.crs)
                if elevation is None or slope is None:
                    continue
                lon, lat = transform(src.crs, "EPSG:4326", [x], [y])
                points.append({"id": f"landsat_{row:05d}_{col:05d}", "lat": float(lat[0]),
                               "lon": float(lon[0]), "analysis_radius_m": radius_m,
                               "analysis_method": "circular-window mean; QA_PIXEL clear pixels",
                               "features": {**values, "cloud_free_fraction": cloud_free,
                                            "elevation_m": elevation, "slope_deg": slope,
                                            "tmax_mean_by_month": {str(k): v for k, v in power["tmax_mean_by_month"].items()},
                                            "heat_days_40c_by_month": {str(k): v for k, v in power["heat_days_40c_by_month"].items()},
                                            "rain_mm_by_month": {str(k): v for k, v in power.get("rain_mm_by_month", {}).items()},
                                            "tmin_mean_by_month": {str(k): v for k, v in power.get("tmin_mean_by_month", {}).items()},
                                            "rh_mean": power.get("rh_mean"), "wind_mean": power.get("wind_mean"),
                                            "solar_radiation_mean": power.get("solar_radiation_mean")}})
    if len(points) < 20:
        raise ValueError(f"Only {len(points)} valid Landsat/SRTM points; at least 20 are required")

    elevations = np.asarray([point["features"]["elevation_m"] for point in points])
    low_threshold = float(np.percentile(elevations, 10))
    for point in points:
        point["features"]["low_lying_flag"] = point["features"]["elevation_m"] <= low_threshold
        point["features"]["smap_surface_mean"] = context["sources"]["smap"]["surface_soil_moisture"]["mean"]
        point["features"]["smap_rootzone_mean"] = context["sources"]["smap"]["rootzone_soil_moisture"]["mean"]
        # This is a weekly mean daily rate. It is not a daily series or weekly total.
        point["features"]["gpm_mean_daily_rate_mm_per_day"] = context["sources"]["gpm_imerg"]["mean_daily_mm_per_day"]

    file_paths = [*assets.values(), mtl_path, Path(dem_path), Path(slope_path), Path(power_csv),
                  Path(regional_context_path)]
    meta = {
        "schema_version": "1.0", "processing_version": PROCESSING_VERSION,
        "validation_status": "validated", "temporal_alignment": "not_aligned",
        "satellite_window": f"{mtl.get('DATE_ACQUIRED', 'unknown')}/{mtl.get('DATE_ACQUIRED', 'unknown')}",
        "landsat_date": mtl.get("DATE_ACQUIRED"), "analysis_spacing_m": spacing_m,
        "analysis_radius_m": radius_m, "cloud_free_threshold": min_cloud_free,
        "pilot_bounds_wgs84": {"west": min_lon, "south": min_lat, "east": max_lon, "north": max_lat},
        "sources": {"landsat": {"product_id": mtl.get("LANDSAT_PRODUCT_ID"), "acquisition_date": mtl.get("DATE_ACQUIRED"),
                                   "collection_number": mtl.get("COLLECTION_NUMBER"), "assets": [p.name for p in assets.values()],
                                   "qa_pixel_excluded_bits": list(range(6)), "sr_scale_offset_from_mtl": reflectance_scales,
                                   "st_scale_offset_from_mtl": temp_scale, "grid": profiles["red"]},
                    "srtm": {"source": "NASA SRTMGL1 V003 DEM", "resolution_m_nominal": 30,
                             "derived_slope": "data/processed/terrain/slope_deg.tif",
                             "low_lying_flag_definition": "point elevation at or below the 10th percentile of valid analysis points; not a flood diagnostic"},
                    "nasa_power": {"source_file": Path(power_csv).name, "header": power_header,
                                   "summary": "Monthly climatology at the supplied POWER point/grid; repeated for pilot points",
                                   "solar_radiation_unit": "MJ/m^2/day"},
                    "smap": {"source": "NASA SMAP SPL4SMGP V008", "role": "regional context only"},
                    "gpm_imerg": {"source": "NASA GPM IMERG Final Run V07", "role": "regional context only",
                                  "limitation": "weekly mean daily rate; daily series, rainy days, maximum daily rainfall and total are unavailable"}},
        "source_checksums": {p.name: checksum(p) for p in file_paths},
        "limitations": ["SMAP and GPM are coarse regional context, not field values.",
                        "Source periods are not temporally aligned.",
                        "Relative low elevation is not a drainage or waterlogging diagnosis.",
                        "POWER monthly climate summaries are repeated context from one supplied point/grid.",
                        "Cloud-free fraction is based on QA_PIXEL bits 0-5 and valid source pixels."],
    }
    payload = {"meta": meta, "points": points}
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    return {"output": str(output_path), "point_count": len(points), "validation_status": meta["validation_status"],
            "landsat_date": meta["landsat_date"], "sources": list(meta["sources"])}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene-dir", type=Path, default=ROOT / "data/raw/landsat/USGS_Landsat_C2_L2_Hyderabad_2025-09-22/extracted")
    parser.add_argument("--dem", type=Path, default=None)
    parser.add_argument("--slope", type=Path, default=ROOT / "data/processed/terrain/slope_deg.tif")
    parser.add_argument("--power", type=Path, default=next(iter(sorted((ROOT / "data/api-samples/nasa-power").glob("POWER_Point_Daily_*.csv"))), ROOT / "missing-power.csv"))
    parser.add_argument("--regional-context", type=Path, default=ROOT / "data/processed/model-features/regional_context.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/features/features.json")
    parser.add_argument("--spacing-m", type=int, default=180)
    parser.add_argument("--radius-m", type=int, default=75)
    parser.add_argument("--min-cloud-free", type=float, default=0.5)
    args = parser.parse_args()
    print(json.dumps(build(args.scene_dir, args.dem, args.slope, args.power, args.regional_context,
                           args.output, args.spacing_m, args.radius_m, args.min_cloud_free), indent=2))


if __name__ == "__main__":
    main()
