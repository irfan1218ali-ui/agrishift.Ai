"""
Tests for NASA GPM IMERG rainfall validation, precipitation totals, and limitations.
"""

import json
from pathlib import Path

from geospatial.rainfall.summarize_gpm import summarize_gpm
from geospatial.rainfall.validate_gpm import validate_gpm

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_REGIONAL_DIR = ROOT_DIR / "data" / "processed" / "regional"


def test_gpm_validation():
    val = validate_gpm()
    assert val["is_valid"], f"GPM validation failed: {val['errors']}"
    assert val["attributes"]["units"] == "mm/day"
    assert val["attributes"]["product"] == "GPM_3IMERGDF"
    assert "Final Run" in val["attributes"]["version"]
    assert val["variable_checks"]["mean_rate_mm_day"] > 0.0


def test_gpm_weekly_mean_rate_and_limitations():
    summary = summarize_gpm()
    assert summary["mean_daily_rate_mm_day"] > 0.0
    assert summary["minimum_cell_mean_daily_rate_mm_day"] <= summary["mean_daily_rate_mm_day"]
    assert summary["maximum_cell_mean_daily_rate_mm_day"] >= summary["mean_daily_rate_mm_day"]
    assert "gpm_total_mm" not in summary
    assert "gpm_rainy_days" not in summary
    assert "gpm_max_daily_mm" not in summary

    # Mandatory limitation check
    assert "not a field rain gauge" in summary["gpm_limitation"]
    assert "daily totals" in summary["gpm_limitation"]

    # File output check
    json_path = PROCESSED_REGIONAL_DIR / "gpm_summary.json"
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["mean_daily_rate_mm_day"] == summary["mean_daily_rate_mm_day"]
