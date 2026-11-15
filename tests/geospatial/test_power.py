"""
Tests for NASA POWER climate data validation, parameter parsing, and monthly summaries.
"""

import json
from pathlib import Path
import pandas as pd

from geospatial.climate.summarize_power import summarize_power
from geospatial.climate.validate_power import EXPECTED_PARAMS, validate_power_data

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_CLIMATE_DIR = ROOT_DIR / "data" / "processed" / "climate"


def test_power_validation():
    report = validate_power_data()
    assert report["is_valid"], f"POWER validation failed: {report['errors']}"
    assert report["temporal_coverage"]["total_records"] == 4018
    assert report["temporal_coverage"]["is_continuous"] is True
    assert set(report["parameter_summary"]["parameters_present"]) == set(EXPECTED_PARAMS)

    # Verify zero missing values
    for p, count in report["parameter_summary"]["missing_value_counts"].items():
        assert count == 0, f"Unexpected missing values in {p}: {count}"


def test_power_summaries():
    summary = summarize_power()
    assert "overall_means" in summary
    assert "monthly_indicators" in summary

    # Verify monthly table exists
    csv_path = PROCESSED_CLIMATE_DIR / "power_monthly_summary.csv"
    assert csv_path.exists()
    df_m = pd.read_csv(csv_path)
    assert len(df_m) == 12, "Expected exactly 12 months"

    # May and June should have the highest mean temperatures and heat days
    may_row = df_m[df_m["month_num"] == 5].iloc[0]
    jan_row = df_m[df_m["month_num"] == 1].iloc[0]
    assert may_row["t2m_max_mean_c"] > jan_row["t2m_max_mean_c"]
    assert may_row["heat_days_ge_40c_mean"] > 10.0
    assert jan_row["heat_days_ge_40c_mean"] == 0.0

    # JSON summary consistency
    json_path = PROCESSED_CLIMATE_DIR / "power_summary.json"
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data["monthly_indicators"]["heat_days_40c_by_month"]) == 12
    assert len(data["monthly_indicators"]["tmax_mean_by_month"]) == 12
    assert len(data["monthly_indicators"]["rain_mm_by_month"]) == 12
