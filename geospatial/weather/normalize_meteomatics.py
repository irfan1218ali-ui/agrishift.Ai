"""
Meteomatics Weather Normalizer & Daily Aggregator.
Parses multi-parameter JSON responses, produces a clean hourly CSV table,
and derives daily forecast summaries with complete metadata.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from geospatial.weather.validate_meteomatics import DEFAULT_METEOMATICS_FILE

PROCESSED_WEATHER_DIR = ROOT_DIR / "data" / "processed" / "weather"
PROCESSED_WEATHER_DIR.mkdir(parents=True, exist_ok=True)


def normalize_meteomatics(
    file_path: Path = DEFAULT_METEOMATICS_FILE,
    out_dir: Path = PROCESSED_WEATHER_DIR,
) -> dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    gen_at = data.get("dateGenerated", "UNKNOWN")

    # Map parameter series
    param_series: dict[str, dict[str, float]] = {}
    lat = None
    lon = None

    for entry in data.get("data", []):
        pname = entry.get("parameter")
        coords = entry.get("coordinates", [{}])[0]
        if lat is None:
            lat = coords.get("lat")
            lon = coords.get("lon")
        dates_list = coords.get("dates", [])
        param_series[pname] = {d["date"]: float(d["value"]) for d in dates_list if d.get("value") is not None}

    # Reference timestamps from t_2m:C
    ref_timestamps = sorted(list(param_series["t_2m:C"].keys()))

    hourly_rows = []
    for ts in ref_timestamps:
        t_c = param_series["t_2m:C"].get(ts)
        precip = param_series["precip_1h:mm"].get(ts, 0.0)
        rh = param_series["relative_humidity_2m:p"].get(ts)
        wind = param_series["wind_speed_10m:ms"].get(ts)

        hourly_rows.append({
            "timestamp_utc": ts,
            "temperature_c": t_c,
            "precipitation_mm": precip,
            "relative_humidity_percent": rh,
            "wind_speed_ms": wind,
        })

    # Save hourly CSV
    hourly_csv_path = out_dir / "meteomatics_hourly.csv"
    with open(hourly_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "timestamp_utc",
            "temperature_c",
            "precipitation_mm",
            "relative_humidity_percent",
            "wind_speed_ms",
        ])
        writer.writeheader()
        writer.writerows(hourly_rows)

    # Derive daily summaries
    df = pd.DataFrame(hourly_rows)
    df["date"] = df["timestamp_utc"].apply(lambda s: s.split("T")[0])

    daily_summaries = []
    for d_str, group in df.groupby("date", sort=True):
        tmax = round(float(group["temperature_c"].max()), 2)
        tmin = round(float(group["temperature_c"].min()), 2)
        rain_tot = round(float(group["precipitation_mm"].sum()), 2)
        rh_mean = round(float(group["relative_humidity_percent"].mean()), 2)
        wind_max = round(float(group["wind_speed_ms"].max()), 2)

        daily_summaries.append({
            "date": d_str,
            "tmax_c": tmax,
            "tmin_c": tmin,
            "rain_total_mm": rain_tot,
            "rh_mean": rh_mean,
            "wind_max_ms": wind_max,
            "hours_count": int(len(group)),
        })

    first_ts = ref_timestamps[0]
    last_ts = ref_timestamps[-1]
    now_utc = datetime(2026, 11, 15, 8, 35, 51, tzinfo=timezone.utc)
    last_dt = datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    is_expired = now_utc > last_dt

    daily_json_payload = {
        "metadata": {
            "source": "Meteomatics Weather API",
            "is_sample": False,
            "is_live": False,
            "generated_at": gen_at,
            "valid_from": first_ts,
            "valid_until": last_ts,
            "expired": is_expired,
            "coordinates": {"latitude": lat, "longitude": lon},
            "location_name": "Hyderabad, Sindh, Pakistan",
            "parameters": [
                "t_2m:C",
                "precip_1h:mm",
                "relative_humidity_2m:p",
                "wind_speed_10m:ms",
            ],
        },
        "daily_forecast": daily_summaries,
    }

    daily_json_path = out_dir / "meteomatics_daily.json"
    with open(daily_json_path, "w", encoding="utf-8") as f:
        json.dump(daily_json_payload, f, indent=2)

    print(f"Meteomatics outputs saved to {hourly_csv_path.relative_to(ROOT_DIR)} and {daily_json_path.relative_to(ROOT_DIR)}")
    return daily_json_payload


if __name__ == "__main__":
    normalize_meteomatics()
