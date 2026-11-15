"""Create provenance manifests from observed local files; unknown values remain blank."""
from __future__ import annotations

import csv
import hashlib
import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import rasterio


ROOT = Path(__file__).resolve().parents[2]
SMAP_DIR = Path.home() / "Downloads" / "smap dataset"
FIELDS = ["file_name", "relative_path", "provider", "product", "version", "variable",
          "observation_datetime", "format", "crs", "bounds", "resolution", "unit", "nodata",
          "minimum", "maximum", "mean", "sha256", "validation_status", "notes"]


def checksum(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def project_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        # Keep manifests relocatable and avoid embedding a developer's Windows username.
        return f"external/{path.parent.name}/{path.name}"


def raster_row(path: Path, provider: str, product: str, version: str, variable: str,
               observed: str = "") -> dict:
    with rasterio.open(path) as dataset:
        values = dataset.read(1, masked=True)
        vals = values.compressed().astype(np.float64)
        tags = dataset.tags()
        unit = tags.get("units") or next((v.split(":", 1)[1] for k, v in tags.items()
                                           if k.endswith("#units") and ":" in v), "")
        return {"file_name": path.name, "relative_path": project_path(path), "provider": provider,
                "product": product, "version": version, "variable": variable, "observation_datetime": observed,
                "format": "GeoTIFF", "crs": str(dataset.crs or ""),
                "bounds": json.dumps([float(v) for v in dataset.bounds]),
                "resolution": json.dumps([float(abs(dataset.transform.a)), float(abs(dataset.transform.e))]),
                "unit": unit, "nodata": "" if dataset.nodata is None else dataset.nodata,
                "minimum": "" if not vals.size else float(vals.min()),
                "maximum": "" if not vals.size else float(vals.max()),
                "mean": "" if not vals.size else float(vals.mean()), "sha256": checksum(path),
                "validation_status": "metadata_validated" if vals.size else "no_valid_pixels",
                "notes": "Metadata and file readability checked; scientific suitability is not implied."}


def date_from_doy(filename: str) -> str:
    match = re.search(r"doy(\d{4})(\d{3})", filename)
    return (date(int(match.group(1)), 1, 1) + timedelta(days=int(match.group(2)) - 1)).isoformat() if match else ""


def write_manifest(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def build(smap_dir: Path = SMAP_DIR) -> dict:
    manifests = ROOT / "data" / "manifests"
    counts = {}

    smap_rows = []
    for path in sorted(Path(smap_dir).glob("*.tif")):
        variable = "surface_soil_moisture" if "_sm_surface_" in path.name else (
            "rootzone_soil_moisture" if "_sm_rootzone_" in path.name else "unknown")
        match = re.search(r"_(\d{8}T\d{6})_", path.name)
        observed = match.group(1) + "Z" if match else ""
        smap_rows.append(raster_row(path, "NASA", "SMAP SPL4SMGP", "V008", variable, observed))
    counts["smap"] = len(smap_rows)
    write_manifest(manifests / "smap-files.csv", smap_rows)

    gpm_rows = []
    for path in sorted((ROOT / "data" / "raw" / "gpm-imerg").glob("**/*")):
        if path.suffix.lower() == ".tif":
            row = raster_row(path, "NASA", "GPM_3IMERGDF Final Run", "V07",
                             "time_averaged_precipitation")
            row["notes"] = "Supplied map is the weekly mean daily precipitation rate; daily totals/counts are absent."
            gpm_rows.append(row)
        elif path.suffix.lower() == ".nc":
            import netCDF4
            with netCDF4.Dataset(path) as dataset:
                variable = next((v for v in dataset.variables if "precipitation" in v.lower()), "")
                data = np.ma.masked_invalid(dataset.variables[variable][:]) if variable else np.ma.array([])
                vals = data.compressed()
                gpm_rows.append({"file_name": path.name, "relative_path": project_path(path), "provider": "NASA",
                    "product": "GPM_3IMERGDF Final Run", "version": "V07", "variable": variable,
                    "observation_datetime": f"{getattr(dataset, 'start_time', '')}/{getattr(dataset, 'end_time', '')}",
                    "format": "NetCDF", "crs": "EPSG:4326", "bounds": "", "resolution": "0.1 degree",
                    "unit": getattr(dataset.variables[variable], "units", "") if variable else "",
                    "nodata": "", "minimum": float(vals.min()) if vals.size else "",
                    "maximum": float(vals.max()) if vals.size else "", "mean": float(vals.mean()) if vals.size else "",
                    "sha256": checksum(path), "validation_status": "metadata_validated" if vals.size else "no_valid_data",
                    "notes": "Single weekly time average; no daily series."})
    counts["gpm"] = len(gpm_rows)
    write_manifest(manifests / "gpm-files.csv", gpm_rows)
    write_manifest(manifests / "gpm-imerg-files.csv", gpm_rows)

    terrain_rows = []
    for path in sorted((ROOT / "data" / "raw" / "terrain").glob("**/*.tif")):
        variable = "elevation" if "_DEM_" in path.name else "number_of_observations"
        terrain_rows.append(raster_row(path, "NASA", "SRTMGL1", "V003", variable,
                                       date_from_doy(path.name)))
    counts["terrain"] = len(terrain_rows)
    write_manifest(manifests / "terrain-files.csv", terrain_rows)

    landsat_dir = ROOT / "data" / "raw" / "landsat"
    scene_files = [p for p in landsat_dir.glob("**/*") if p.is_file() and p.suffix.lower() in
                   (".tif", ".tiff", ".txt", ".xml", ".json") and p.name.lower() != "readme.md"]
    landsat_rows = []
    for path in scene_files:
        landsat_rows.append({"file_name": path.name, "relative_path": project_path(path),
            "provider": "USGS", "product": "Landsat Collection 2 Level-2", "version": "",
            "variable": "", "observation_datetime": "", "format": path.suffix.lower(), "crs": "",
            "bounds": "", "resolution": "", "unit": "", "nodata": "", "minimum": "",
            "maximum": "", "mean": "", "sha256": checksum(path), "validation_status": "unvalidated",
            "notes": "Unexpected scene support file; manually review."})
    counts["landsat_scene_files"] = len(scene_files)
    write_manifest(manifests / "landsat-files.csv", landsat_rows)

    power_rows = []
    power_files = sorted((ROOT / "data" / "api-samples" / "nasa-power").glob("POWER_Point_Daily_*.csv"))
    power_units = {"T2M": "°C", "T2M_MAX": "°C", "T2M_MIN": "°C", "PRECTOTCORR": "mm/day",
                   "RH2M": "%", "WS2M": "m/s", "ALLSKY_SFC_SW_DWN": "MJ/m^2/day"}
    for path in power_files:
        with path.open(newline="", encoding="utf-8-sig") as source:
            for line in source:
                if line.strip() == "-END HEADER-":
                    break
            reader = csv.DictReader(source)
            rows = list(reader)
        for name, unit in power_units.items():
            values = []
            for row in rows:
                try:
                    value = float(row[name])
                    if value != -999:
                        values.append(value)
                except (KeyError, ValueError, TypeError):
                    pass
            power_rows.append({"file_name": path.name, "relative_path": project_path(path), "provider": "NASA",
                "product": "NASA POWER daily point", "version": "saved sample", "variable": name,
                "observation_datetime": "2015-01-01/2025-12-31", "format": "CSV", "crs": "EPSG:4326",
                "bounds": "25.396,68.3578", "resolution": "0.5 x 0.625 degree source region",
                "unit": unit, "nodata": "-999", "minimum": min(values) if values else "",
                "maximum": max(values) if values else "", "mean": float(np.mean(values)) if values else "",
                "sha256": checksum(path), "validation_status": "metadata_validated" if values else "no_valid_data",
                "notes": "Saved regional grid sample; not a field measurement. Provider header reports location and date coverage."})
    counts["power"] = len(power_rows)
    write_manifest(manifests / "power-files.csv", power_rows)

    meteo_rows = []
    meteo_file = ROOT / "data" / "api-samples" / "meteomatics" / "json.json"
    if meteo_file.is_file():
        payload = json.loads(meteo_file.read_text(encoding="utf-8"))
        unit_map = {"t_2m:C": "°C", "precip_1h:mm": "mm/hour", "relative_humidity_2m:p": "%",
                    "wind_speed_10m:ms": "m/s"}
        for entry in payload.get("data", []):
            name = entry.get("parameter", "")
            values = [point.get("value") for coord in entry.get("coordinates", [])
                      for point in coord.get("dates", [])
                      if isinstance(point.get("value"), (int, float)) and not isinstance(point.get("value"), bool)]
            dates = [str(point.get("date", "")) for coord in entry.get("coordinates", [])
                     for point in coord.get("dates", []) if point.get("date")]
            meteo_rows.append({"file_name": meteo_file.name, "relative_path": project_path(meteo_file),
                "provider": "Meteomatics", "product": "hourly forecast saved response", "version": "sample",
                "variable": name, "observation_datetime": f"{min(dates)}/{max(dates)}" if dates else "",
                "format": "JSON", "crs": "EPSG:4326", "bounds": "coordinates in payload",
                "resolution": "hourly", "unit": unit_map.get(name, ""), "nodata": "null",
                "minimum": min(values) if values else "", "maximum": max(values) if values else "",
                "mean": float(np.mean(values)) if values else "", "sha256": checksum(meteo_file),
                "validation_status": "metadata_validated" if values else "no_valid_data",
                "notes": f"Saved sample, generated_at={payload.get('dateGenerated')}; not live. Account metadata omitted."})
    counts["meteomatics"] = len(meteo_rows)
    write_manifest(manifests / "meteomatics-files.csv", meteo_rows)
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smap-dir", type=Path, default=SMAP_DIR)
    args = parser.parse_args()
    print(json.dumps(build(args.smap_dir), indent=2))
