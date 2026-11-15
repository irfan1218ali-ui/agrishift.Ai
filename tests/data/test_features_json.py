"""
Tests for real features.json structure, non-mock values, and quality flags.
"""

import json
from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
FEATURES_JSON = ROOT_DIR / "data" / "features" / "features.json"
FEATURE_TABLE = ROOT_DIR / "data" / "processed" / "features" / "pilot_feature_table.csv"
EXAMPLE_JSON = ROOT_DIR / "data" / "features" / "features.example.json"


def test_feature_table_validity():
    assert FEATURE_TABLE.exists(), f"Feature table missing at {FEATURE_TABLE}"
    df = pd.read_csv(FEATURE_TABLE)
    assert len(df) >= 20, f"Expected at least 20 valid rows for K-Means, got {len(df)}"

    required_cols = [
        "id",
        "lat",
        "lon",
        "analysis_radius_m",
        "ndvi_mean",
        "ndmi_mean",
        "bsi_mean",
        "surface_temp_c",
        "cloud_free_fraction",
        "elevation_m",
        "slope_deg",
        "low_lying_flag",
        "rh_mean",
        "wind_mean",
        "solar_radiation_mean",
        "smap_surface_mean",
        "smap_rootzone_mean",
        "gpm_mean_daily_rate_mm_day",
    ]
    for c in required_cols:
        assert c in df.columns, f"Missing column {c} in feature table"

    # Coordinates within pilot bounds [68.20, 25.20, 68.55, 25.55]
    assert (df["lon"] >= 68.20).all() and (df["lon"] <= 68.55).all()
    assert (df["lat"] >= 25.20).all() and (df["lat"] <= 25.55).all()


def test_features_json_structure_and_no_mock_data():
    assert FEATURES_JSON.exists(), f"features.json missing at {FEATURES_JSON}"
    with open(FEATURES_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "meta" in data
    assert "points" in data
    assert data["meta"]["data_mode"] == "real"
    assert len(data["points"]) >= 20

    # Ensure no values copied from features.example.json
    if EXAMPLE_JSON.exists():
        with open(EXAMPLE_JSON, "r", encoding="utf-8") as f:
            example = json.load(f)
        example_point_ids = {p.get("id") for p in example.get("points", [])}
        for pt in data["points"]:
            # Real point IDs should be hyd_001..hyd_N, not demo mock IDs
            assert pt["id"] not in example_point_ids or pt["features"]["ndvi_mean"] != 0.65

    # Check first point schema
    p0 = data["points"][0]
    assert "id" in p0
    assert "lat" in p0
    assert "lon" in p0
    assert "features" in p0
    assert "clustering" in p0
    assert "regional_context" in p0
    assert "data_quality" in p0

    # Verify clustering outputs
    assert p0["clustering"]["cluster_id"] in {0, 1, 2}
    assert p0["clustering"]["cluster_label"] in {
        "Relatively vegetated",
        "Intermediate condition",
        "Higher bare/thermal exposure",
    }
    assert p0["clustering"]["cluster_distance"] >= 0.0

    # Verify regional context
    assert p0["regional_context"]["smap_surface_mean"] > 0.0
    assert p0["regional_context"]["gpm_mean_daily_rate_mm_day"] > 0.0
    assert "gpm_rainy_days" not in p0["regional_context"]
