"""
Tests for Meteomatics weather validation, hourly normalization, and daily summaries.
"""

import json
from pathlib import Path
import pandas as pd

from geospatial.weather.normalize_meteomatics import normalize_meteomatics
from geospatial.weather.validate_meteomatics import validate_meteomatics_file

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_WEATHER_DIR = ROOT_DIR / "data" / "processed" / "weather"


def test_meteomatics_validation():
    val = validate_meteomatics_file()
    assert val["is_valid"], f"Meteomatics validation failed: {val['errors']}"
    assert len(val["parameters"]["found"]) == 4
    for p in ["t_2m:C", "precip_1h:mm", "relative_humidity_2m:p", "wind_speed_10m:ms"]:
        assert p in val["parameters"]["found"]

    assert val["temporal_checks"]["is_strictly_hourly"] is True
    assert val["temporal_checks"]["total_hourly_steps"] == 169
    assert val["temporal_checks"]["is_expired"] is False


def test_meteomatics_normalization_and_daily():
    daily_payload = normalize_meteomatics()
    assert "daily_forecast" in daily_payload
    assert len(daily_payload["daily_forecast"]) >= 7

    # Check hourly CSV
    csv_path = PROCESSED_WEATHER_DIR / "meteomatics_hourly.csv"
    assert csv_path.exists()
    df_h = pd.read_csv(csv_path)
    assert len(df_h) == 169
    assert "timestamp_utc" in df_h.columns
    assert (df_h["temperature_c"] >= -10.0).all() and (df_h["temperature_c"] <= 55.0).all()

    # Check daily JSON
    json_path = PROCESSED_WEATHER_DIR / "meteomatics_daily.json"
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert "metadata" in d
    assert d["metadata"]["is_sample"] is False
    assert d["metadata"]["is_live"] is False
    assert "valid_until" in d["metadata"]
