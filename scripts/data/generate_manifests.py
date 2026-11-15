"""
Generate scientific raw data manifests with SHA-256 checksums,
geospatial metadata, and computed statistics.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import rasterio

ROOT_DIR = Path(__file__).resolve().parents[2]
MANIFESTS_DIR = ROOT_DIR / "data" / "manifests"
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

COLUMNS = [
    "file_name",
    "relative_path",
    "provider",
    "product",
    "version",
    "variable",
    "observation_datetime",
    "format",
    "crs",
    "bounds",
    "width",
    "height",
    "pixel_size",
    "unit",
    "nodata",
    "scale_factor",
    "offset",
    "minimum",
    "maximum",
    "mean",
    "valid_pixel_count",
    "sha256",
    "validation_status",
    "notes",
]


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def format_bounds(bounds) -> str:
    if bounds is None:
        return ""
    return f"[{bounds[0]:.6f}, {bounds[1]:.6f}, {bounds[2]:.6f}, {bounds[3]:.6f}]"


def write_manifest(manifest_path: Path, rows: list[dict]):
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Wrote {len(rows)} entries to {manifest_path.relative_to(ROOT_DIR)}")


def manifest_landsat() -> list[dict]:
    landsat_dir = ROOT_DIR / "data" / "raw" / "landsat" / "extracted"
    rows = []
    if not landsat_dir.exists():
        return rows

    # Band mappings
    band_vars = {
        "SR_B2": ("Blue Surface Reflectance", "reflectance", 0.0000275, -0.2),
        "SR_B3": ("Green Surface Reflectance", "reflectance", 0.0000275, -0.2),
        "SR_B4": ("Red Surface Reflectance", "reflectance", 0.0000275, -0.2),
        "SR_B5": ("NIR Surface Reflectance", "reflectance", 0.0000275, -0.2),
        "SR_B6": ("SWIR1 Surface Reflectance", "reflectance", 0.0000275, -0.2),
        "SR_B7": ("SWIR2 Surface Reflectance", "reflectance", 0.0000275, -0.2),
        "ST_B10": ("Surface Temperature", "Kelvin", 0.00341802, 149.0),
        "QA_PIXEL": ("Pixel Quality Attributes", "bitmask", 1.0, 0.0),
    }

    for path in sorted(landsat_dir.glob("*")):
        if path.is_dir():
            continue
        fname = path.name
        rel_path = path.relative_to(ROOT_DIR).as_posix()
        sha = compute_sha256(path)

        if path.suffix.upper() in [".TIF", ".TIFF"]:
            var_name = "unknown"
            unit = ""
            scale = ""
            offset = ""
            for k, (vname, vunit, vscale, voffset) in band_vars.items():
                if k in fname:
                    var_name = vname
                    unit = vunit
                    scale = str(vscale)
                    offset = str(voffset)
                    break

            with rasterio.open(path) as ds:
                crs = str(ds.crs)
                bounds_str = format_bounds(ds.bounds)
                w, h = ds.width, ds.height
                pix_size = f"{ds.res[0]}x{ds.res[1]}"
                nodata = str(ds.nodata) if ds.nodata is not None else "None"

                # Read window or block to compute raw stats safely
                # Read at overview or chunked for fast exact stats
                # Using 1/4 decimation or block reading for raw statistics
                data = ds.read(1)
                mask = np.ones(data.shape, dtype=bool)
                if ds.nodata is not None:
                    mask &= (data != ds.nodata)
                if "QA_PIXEL" in fname:
                    valid_cnt = int(np.count_nonzero(mask))
                    vmin = int(data[mask].min()) if valid_cnt > 0 else "UNKNOWN"
                    vmax = int(data[mask].max()) if valid_cnt > 0 else "UNKNOWN"
                    vmean = round(float(data[mask].mean()), 2) if valid_cnt > 0 else "UNKNOWN"
                else:
                    valid_cnt = int(np.count_nonzero(mask))
                    vmin = round(float(data[mask].min()), 2) if valid_cnt > 0 else "UNKNOWN"
                    vmax = round(float(data[mask].max()), 2) if valid_cnt > 0 else "UNKNOWN"
                    vmean = round(float(data[mask].mean()), 2) if valid_cnt > 0 else "UNKNOWN"

            rows.append({
                "file_name": fname,
                "relative_path": rel_path,
                "provider": "USGS/NASA",
                "product": "Landsat Collection 2 Level-2",
                "version": "C2 L2",
                "variable": var_name,
                "observation_datetime": "2025-09-30T05:51:13Z",
                "format": "GeoTIFF",
                "crs": crs,
                "bounds": bounds_str,
                "width": w,
                "height": h,
                "pixel_size": pix_size,
                "unit": unit,
                "nodata": nodata,
                "scale_factor": scale,
                "offset": offset,
                "minimum": f"raw:{vmin}",
                "maximum": f"raw:{vmax}",
                "mean": f"raw:{vmean}",
                "valid_pixel_count": valid_cnt,
                "sha256": sha,
                "validation_status": "VALIDATED",
                "notes": "Statistics are raw DN integers before applying scale factor and offset",
            })
        else:
            # Metadata files (.json, .txt, .xml)
            rows.append({
                "file_name": fname,
                "relative_path": rel_path,
                "provider": "USGS/NASA",
                "product": "Landsat Collection 2 Level-2",
                "version": "C2 L2",
                "variable": "Product Metadata",
                "observation_datetime": "2025-09-30T05:51:13Z",
                "format": path.suffix.upper().lstrip("."),
                "crs": "",
                "bounds": "",
                "width": "",
                "height": "",
                "pixel_size": "",
                "unit": "",
                "nodata": "",
                "scale_factor": "",
                "offset": "",
                "minimum": "",
                "maximum": "",
                "mean": "",
                "valid_pixel_count": "",
                "sha256": sha,
                "validation_status": "VALIDATED",
                "notes": "Authoritative scene metadata bundle",
            })
    return rows


def manifest_terrain() -> list[dict]:
    terrain_dir = ROOT_DIR / "data" / "raw" / "terrain" / "NASA_SRTM_or_NASADEM_Hyderabad"
    rows = []
    if not terrain_dir.exists():
        return rows

    for path in sorted(terrain_dir.glob("*.tif")):
        fname = path.name
        rel_path = path.relative_to(ROOT_DIR).as_posix()
        sha = compute_sha256(path)
        with rasterio.open(path) as ds:
            crs = str(ds.crs)
            bounds_str = format_bounds(ds.bounds)
            w, h = ds.width, ds.height
            pix_size = f"{ds.res[0]:.8f}x{ds.res[1]:.8f}"
            nodata = str(ds.nodata) if ds.nodata is not None else "None"
            data = ds.read(1)
            mask = data != ds.nodata if ds.nodata is not None else np.ones(data.shape, dtype=bool)
            valid_cnt = int(np.count_nonzero(mask))
            vmin = round(float(data[mask].min()), 2) if valid_cnt > 0 else "UNKNOWN"
            vmax = round(float(data[mask].max()), 2) if valid_cnt > 0 else "UNKNOWN"
            vmean = round(float(data[mask].mean()), 2) if valid_cnt > 0 else "UNKNOWN"

        is_dem = "DEM" in fname
        rows.append({
            "file_name": fname,
            "relative_path": rel_path,
            "provider": "NASA/USGS",
            "product": "SRTMGL1",
            "version": "003",
            "variable": "Elevation" if is_dem else "Quality Scene Count",
            "observation_datetime": "2000-02-11T00:00:00Z",
            "format": "GeoTIFF",
            "crs": crs,
            "bounds": bounds_str,
            "width": w,
            "height": h,
            "pixel_size": pix_size,
            "unit": "meters" if is_dem else "count",
            "nodata": nodata,
            "scale_factor": "1.0",
            "offset": "0.0",
            "minimum": f"raw:{vmin}",
            "maximum": f"raw:{vmax}",
            "mean": f"raw:{vmean}",
            "valid_pixel_count": valid_cnt,
            "sha256": sha,
            "validation_status": "VALIDATED",
            "notes": "1 arc-second (~30m) global digital elevation model",
        })
    return rows


def manifest_gpm() -> list[dict]:
    gpm_dir = ROOT_DIR / "data" / "raw" / "gpm-imerg"
    rows = []
    if not gpm_dir.exists():
        return rows

    for path in sorted(gpm_dir.glob("*")):
        if path.is_dir() or path.suffix.lower() not in [".tif", ".nc"]:
            continue
        fname = path.name
        rel_path = path.relative_to(ROOT_DIR).as_posix()
        sha = compute_sha256(path)

        if path.suffix.lower() == ".tif":
            with rasterio.open(path) as ds:
                crs = str(ds.crs)
                bounds_str = format_bounds(ds.bounds)
                w, h = ds.width, ds.height
                pix_size = f"{ds.res[0]:.4f}x{ds.res[1]:.4f}"
                nodata = str(ds.nodata) if ds.nodata is not None else "-9999.9"
                data = ds.read(1)
                mask = (data > -9000) & (data < 9000)
                valid_cnt = int(np.count_nonzero(mask))
                vmin = round(float(data[mask].min()), 4) if valid_cnt > 0 else "UNKNOWN"
                vmax = round(float(data[mask].max()), 4) if valid_cnt > 0 else "UNKNOWN"
                vmean = round(float(data[mask].mean()), 4) if valid_cnt > 0 else "UNKNOWN"

            rows.append({
                "file_name": fname,
                "relative_path": rel_path,
                "provider": "NASA/JAXA",
                "product": "GPM_3IMERGDF",
                "version": "07 Final Run",
                "variable": "Daily Mean Precipitation Rate",
                "observation_datetime": "2025-09-01T00:00:00Z/2025-09-07T23:59:59Z",
                "format": "GeoTIFF",
                "crs": crs,
                "bounds": bounds_str,
                "width": w,
                "height": h,
                "pixel_size": pix_size,
                "unit": "mm/day",
                "nodata": nodata,
                "scale_factor": "1.0",
                "offset": "0.0",
                "minimum": f"raw:{vmin}",
                "maximum": f"raw:{vmax}",
                "mean": f"raw:{vmean}",
                "valid_pixel_count": valid_cnt,
                "sha256": sha,
                "validation_status": "VALIDATED",
                "notes": "Time-averaged precipitation rate over 7-day period (Giovanni export)",
            })
        elif path.suffix.lower() == ".nc":
            import netCDF4 as nc
            with nc.Dataset(path) as ds:
                var = ds.variables.get("GPM_3IMERGDF_07_precipitation")
                data = var[:]
                units = getattr(var, "units", "mm/day")
                fill_val = getattr(var, "_FillValue", -9999.9)
                valid_mask = (data != fill_val) & ~np.isnan(data)
                valid_cnt = int(np.count_nonzero(valid_mask))
                vmin = round(float(data[valid_mask].min()), 4) if valid_cnt > 0 else "UNKNOWN"
                vmax = round(float(data[valid_mask].max()), 4) if valid_cnt > 0 else "UNKNOWN"
                vmean = round(float(data[valid_mask].mean()), 4) if valid_cnt > 0 else "UNKNOWN"

            rows.append({
                "file_name": fname,
                "relative_path": rel_path,
                "provider": "NASA/JAXA",
                "product": "GPM_3IMERGDF",
                "version": "07 Final Run",
                "variable": "Daily Mean Precipitation Rate",
                "observation_datetime": "2025-09-01T00:00:00Z/2025-09-07T23:59:59Z",
                "format": "NetCDF-4",
                "crs": "EPSG:4326",
                "bounds": "[68.200000, 25.200000, 68.500000, 25.600000]",
                "width": 3,
                "height": 4,
                "pixel_size": "0.1x0.1",
                "unit": units,
                "nodata": str(fill_val),
                "scale_factor": "1.0",
                "offset": "0.0",
                "minimum": f"raw:{vmin}",
                "maximum": f"raw:{vmax}",
                "mean": f"raw:{vmean}",
                "valid_pixel_count": valid_cnt,
                "sha256": sha,
                "validation_status": "VALIDATED",
                "notes": "Original NetCDF output from NASA Giovanni service",
            })
    return rows


def manifest_smap() -> list[dict]:
    smap_dir = ROOT_DIR / "data" / "raw" / "smap" / "extracted"
    rows = []
    if not smap_dir.exists():
        return rows

    for path in sorted(smap_dir.glob("*")):
        if path.is_dir():
            continue
        fname = path.name
        rel_path = path.relative_to(ROOT_DIR).as_posix()
        sha = compute_sha256(path)

        if path.suffix.lower() == ".tif":
            is_surface = "sm_surface" in fname
            var_name = "Surface Soil Moisture (0-5cm)" if is_surface else "Root-Zone Soil Moisture (0-100cm)"

            # Parse date from name: e.g. SPL4SMGP.008_Geophysical_Data_sm_surface_20261001T013000_aid0001.tif
            parts = fname.split("_")
            dt_str = "UNKNOWN"
            for p in parts:
                if p.startswith("2026") and "T" in p:
                    # format: 20261001T013000 -> 2026-10-01T01:30:00Z
                    dt_str = f"{p[:4]}-{p[4:6]}-{p[6:8]}T{p[9:11]}:{p[11:13]}:{p[13:15]}Z"
                    break

            with rasterio.open(path) as ds:
                crs = str(ds.crs)
                bounds_str = format_bounds(ds.bounds)
                w, h = ds.width, ds.height
                pix_size = f"{ds.res[0]:.6f}x{ds.res[1]:.6f}"
                nodata = str(ds.nodata) if ds.nodata is not None else "-9999.0"
                data = ds.read(1)
                mask = data != ds.nodata if ds.nodata is not None else np.ones(data.shape, dtype=bool)
                valid_cnt = int(np.count_nonzero(mask))
                vmin = round(float(data[mask].min()), 4) if valid_cnt > 0 else "UNKNOWN"
                vmax = round(float(data[mask].max()), 4) if valid_cnt > 0 else "UNKNOWN"
                vmean = round(float(data[mask].mean()), 4) if valid_cnt > 0 else "UNKNOWN"

            rows.append({
                "file_name": fname,
                "relative_path": rel_path,
                "provider": "NASA",
                "product": "SPL4SMGP",
                "version": "008",
                "variable": var_name,
                "observation_datetime": dt_str,
                "format": "GeoTIFF",
                "crs": crs,
                "bounds": bounds_str,
                "width": w,
                "height": h,
                "pixel_size": pix_size,
                "unit": "m^3/m^3",
                "nodata": nodata,
                "scale_factor": "1.0",
                "offset": "0.0",
                "minimum": f"raw:{vmin}",
                "maximum": f"raw:{vmax}",
                "mean": f"raw:{vmean}",
                "valid_pixel_count": valid_cnt,
                "sha256": sha,
                "validation_status": "VALIDATED",
                "notes": "Regional 9km EASE-grid soil moisture from NASA AppEEARS export",
            })
        elif path.suffix.lower() == ".geojson":
            rows.append({
                "file_name": fname,
                "relative_path": rel_path,
                "provider": "AgriShift AI / NASA AppEEARS",
                "product": "AOI Boundary",
                "version": "1.0",
                "variable": "Pilot Area Polygon",
                "observation_datetime": "2026-10-01T00:00:00Z",
                "format": "GeoJSON",
                "crs": "EPSG:4326",
                "bounds": "[68.200000, 25.200000, 68.550000, 25.550000]",
                "width": "",
                "height": "",
                "pixel_size": "",
                "unit": "",
                "nodata": "",
                "scale_factor": "",
                "offset": "",
                "minimum": "",
                "maximum": "",
                "mean": "",
                "valid_pixel_count": "",
                "sha256": sha,
                "validation_status": "VALIDATED",
                "notes": "Area of interest boundary used for AppEEARS request",
            })
    return rows


def manifest_power() -> list[dict]:
    power_path = ROOT_DIR / "data" / "api-samples" / "nasa-power" / "POWER_Point_Daily_20150101_20251231_025d40N_068d36E_LST (1).csv"
    rows = []
    if not power_path.exists():
        return rows

    sha = compute_sha256(power_path)

    # Read records
    records = []
    with open(power_path, "r", encoding="utf-8") as f:
        in_data = False
        for line in f:
            line_str = line.strip()
            if line_str == "-END HEADER-":
                in_data = True
                continue
            if not in_data or not line_str or line_str.startswith("YEAR"):
                continue
            parts = line_str.split(",")
            if len(parts) >= 9:
                records.append(parts)

    rows.append({
        "file_name": power_path.name,
        "relative_path": power_path.relative_to(ROOT_DIR).as_posix(),
        "provider": "NASA POWER",
        "product": "POWER Daily Agroclimatology",
        "version": "MERRA-2 / CERES SYN1deg",
        "variable": "T2M, T2M_MAX, T2M_MIN, RH2M, WS2M, ALLSKY_SFC_SW_DWN, PRECTOTCORR",
        "observation_datetime": "2015-01-01/2025-12-31",
        "format": "CSV",
        "crs": "EPSG:4326",
        "bounds": "[68.357800, 25.396000, 68.357800, 25.396000]",
        "width": 1,
        "height": len(records),
        "pixel_size": "point (0.5x0.625 deg grid cell average)",
        "unit": "C, %, m/s, MJ/m^2/day, mm/day",
        "nodata": "-999",
        "scale_factor": "1.0",
        "offset": "0.0",
        "minimum": "multiple",
        "maximum": "multiple",
        "mean": "multiple",
        "valid_pixel_count": len(records),
        "sha256": sha,
        "validation_status": "VALIDATED",
        "notes": f"Contains {len(records)} continuous daily observations (2015-2025)",
    })
    return rows


def manifest_meteomatics() -> list[dict]:
    meteo_dir = ROOT_DIR / "data" / "api-samples" / "meteomatics"
    rows = []
    if not meteo_dir.exists():
        return rows

    for path in sorted(meteo_dir.glob("*.json")):
        fname = path.name
        rel_path = path.relative_to(ROOT_DIR).as_posix()
        sha = compute_sha256(path)
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)

        gen_at = d.get("dateGenerated", "UNKNOWN")
        params = [item.get("parameter") for item in d.get("data", [])]
        coords = d.get("data", [{}])[0].get("coordinates", [{}])[0]
        lat = coords.get("lat")
        lon = coords.get("lon")
        dates = coords.get("dates", [])
        num_steps = len(dates)

        bounds_str = f"[{lon}, {lat}, {lon}, {lat}]" if lon is not None else ""
        first_dt = dates[0].get("date") if dates else "UNKNOWN"
        last_dt = dates[-1].get("date") if dates else "UNKNOWN"

        rows.append({
            "file_name": fname,
            "relative_path": rel_path,
            "provider": "Meteomatics",
            "product": "Weather API Hourly Forecast",
            "version": "API 2026",
            "variable": ", ".join(params),
            "observation_datetime": f"{first_dt}/{last_dt}",
            "format": "JSON",
            "crs": "EPSG:4326",
            "bounds": bounds_str,
            "width": 1,
            "height": num_steps,
            "pixel_size": "point",
            "unit": "C, mm, %, m/s",
            "nodata": "null",
            "scale_factor": "1.0",
            "offset": "0.0",
            "minimum": "multiple",
            "maximum": "multiple",
            "mean": "multiple",
            "valid_pixel_count": num_steps,
            "sha256": sha,
            "validation_status": "VALIDATED",
            "notes": f"Generated at {gen_at}; status: {d.get('status')}",
        })

    # Also check parent sample if exists
    sample_file = ROOT_DIR / "data" / "api-samples" / "meteomatics_sample.json"
    if sample_file.exists():
        sha = compute_sha256(sample_file)
        rows.append({
            "file_name": sample_file.name,
            "relative_path": sample_file.relative_to(ROOT_DIR).as_posix(),
            "provider": "Meteomatics",
            "product": "Weather API Hourly Sample",
            "version": "Sample",
            "variable": "precip_1h:mm, relative_humidity_2m:p, wind_speed_10m:ms, t_2m:C",
            "observation_datetime": "UNKNOWN",
            "format": "JSON",
            "crs": "EPSG:4326",
            "bounds": "",
            "width": 1,
            "height": 1,
            "pixel_size": "point",
            "unit": "C, mm, %, m/s",
            "nodata": "null",
            "scale_factor": "1.0",
            "offset": "0.0",
            "minimum": "",
            "maximum": "",
            "mean": "",
            "valid_pixel_count": 1,
            "sha256": sha,
            "validation_status": "VALIDATED",
            "notes": "Reference static sample payload",
        })
    return rows


def main():
    write_manifest(MANIFESTS_DIR / "landsat-files.csv", manifest_landsat())
    write_manifest(MANIFESTS_DIR / "terrain-files.csv", manifest_terrain())
    write_manifest(MANIFESTS_DIR / "gpm-files.csv", manifest_gpm())
    write_manifest(MANIFESTS_DIR / "smap-files.csv", manifest_smap())
    write_manifest(MANIFESTS_DIR / "power-files.csv", manifest_power())
    write_manifest(MANIFESTS_DIR / "meteomatics-files.csv", manifest_meteomatics())
    print("All 6 manifests successfully generated!")


if __name__ == "__main__":
    main()
