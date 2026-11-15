"""
NASA POWER Climate Data Summarizer.
Aggregates 11-year daily climatology to generate monthly statistics and overall indicators.
"""

from __future__ import annotations

import csv
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from typing import Any
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from geospatial.climate.validate_power import DEFAULT_POWER_FILE

PROCESSED_CLIMATE_DIR = ROOT_DIR / "data" / "processed" / "climate"
PROCESSED_CLIMATE_DIR.mkdir(parents=True, exist_ok=True)


def parse_power_csv(file_path: Path = DEFAULT_POWER_FILE) -> pd.DataFrame:
    records = []
    columns = []
    in_data = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped == "-END HEADER-":
                in_data = True
                continue
            if not in_data or not stripped:
                continue
            if not columns:
                columns = [c.strip() for c in stripped.split(",")]
            else:
                records.append(stripped.split(","))

    df = pd.DataFrame(records, columns=columns)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Construct datetime
    def to_date(row):
        return date(int(row["YEAR"]), 1, 1) + timedelta(days=int(row["DOY"]) - 1)

    df["date"] = df.apply(to_date, axis=1)
    df["month"] = df["date"].apply(lambda d: d.month)
    df["year"] = df["date"].apply(lambda d: d.year)
    return df


def summarize_power(
    file_path: Path = DEFAULT_POWER_FILE,
    out_dir: Path = PROCESSED_CLIMATE_DIR,
) -> dict[str, Any]:
    df = parse_power_csv(file_path)

    # Filter any missing values
    for col in ["T2M", "T2M_MAX", "T2M_MIN", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN", "PRECTOTCORR"]:
        df = df[df[col] > -900]

    num_years = df["year"].nunique()

    # Monthly aggregations
    monthly_rows = []
    tmax_by_month = {}
    rain_by_month = {}
    heat_days_by_month = {}

    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
    ]

    for m in range(1, 13):
        m_df = df[df["month"] == m]
        m_name = month_names[m - 1]

        t2m_mean = round(float(m_df["T2M"].mean()), 2)
        tmax_mean = round(float(m_df["T2M_MAX"].mean()), 2)
        tmin_mean = round(float(m_df["T2M_MIN"].mean()), 2)
        rh_mean = round(float(m_df["RH2M"].mean()), 2)
        ws_mean = round(float(m_df["WS2M"].mean()), 2)
        solar_mean = round(float(m_df["ALLSKY_SFC_SW_DWN"].mean()), 2)

        # Total rainfall averaged per year for month m
        total_rain_m = float(m_df["PRECTOTCORR"].sum())
        mean_monthly_rain = round(total_rain_m / num_years, 2)

        # Heat days (T2M_MAX >= 40 C) averaged per year for month m
        heat_days_total = int((m_df["T2M_MAX"] >= 40.0).sum())
        heat_days_mean = round(heat_days_total / num_years, 1)

        monthly_rows.append({
            "month_num": m,
            "month_name": m_name,
            "t2m_mean_c": t2m_mean,
            "t2m_max_mean_c": tmax_mean,
            "t2m_min_mean_c": tmin_mean,
            "heat_days_ge_40c_mean": heat_days_mean,
            "precip_total_mean_mm": mean_monthly_rain,
            "rh2m_mean_percent": rh_mean,
            "ws2m_mean_ms": ws_mean,
            "allsky_sw_dwn_mean_mj": solar_mean,
        })

        tmax_by_month[str(m)] = tmax_mean
        rain_by_month[str(m)] = mean_monthly_rain
        heat_days_by_month[str(m)] = heat_days_mean

    # Overall multi-year means
    overall_rh = round(float(df["RH2M"].mean()), 2)
    overall_wind = round(float(df["WS2M"].mean()), 2)
    overall_solar = round(float(df["ALLSKY_SFC_SW_DWN"].mean()), 2)
    overall_t2m = round(float(df["T2M"].mean()), 2)
    annual_rain_mean = round(float(df["PRECTOTCORR"].sum()) / num_years, 2)

    # Output CSV
    csv_out = out_dir / "power_monthly_summary.csv"
    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(monthly_rows[0].keys()))
        writer.writeheader()
        writer.writerows(monthly_rows)

    # Output JSON
    summary_json = {
        "metadata": {
            "source": "NASA POWER Daily Agroclimatology",
            "model_version": "MERRA-2 / CERES SYN1deg",
            "location": {"latitude": 25.396, "longitude": 68.3578},
            "period": {"start_year": int(df["year"].min()), "end_year": int(df["year"].max()), "total_years": num_years},
            "limitation": "Regional gridded climate reanalysis; not a farm-scale meteorological station.",
        },
        "overall_means": {
            "t2m_mean_c": overall_t2m,
            "rh_mean_percent": overall_rh,
            "wind_mean_ms": overall_wind,
            "solar_radiation_mean_mj_m2_day": overall_solar,
            "annual_precipitation_mean_mm": annual_rain_mean,
        },
        "monthly_indicators": {
            "heat_days_40c_by_month": heat_days_by_month,
            "tmax_mean_by_month": tmax_by_month,
            "rain_mm_by_month": rain_by_month,
        },
        "monthly_table": monthly_rows,
    }

    json_out = out_dir / "power_summary.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2)

    print(f"POWER climate summary saved to {csv_out.relative_to(ROOT_DIR)} and {json_out.relative_to(ROOT_DIR)}")
    return summary_json


if __name__ == "__main__":
    summarize_power()
