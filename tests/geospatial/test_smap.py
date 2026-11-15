"""
Tests for NASA SMAP soil moisture data validation, layer distinction, and limitations.
"""

import importlib.util
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_REGIONAL_DIR = ROOT_DIR / "data" / "processed" / "regional"

# Load modules from hyphenated directory geospatial/soil-moisture
val_spec = importlib.util.spec_from_file_location(
    "validate_smap", ROOT_DIR / "geospatial" / "soil-moisture" / "validate_smap.py"
)
val_mod = importlib.util.module_from_spec(val_spec)
val_spec.loader.exec_module(val_mod)
validate_smap = val_mod.validate_smap

def test_smap_validation():
    if not val_mod.DEFAULT_SMAP_DIR.exists():
        import pytest
        pytest.skip("Raw SMAP rasters are excluded; the validated regional summary is committed.")
    val = validate_smap()
    assert val["is_valid"], f"SMAP validation failed: {val['errors']}"
    assert val["file_counts"]["surface_tifs"] == 56
    assert val["file_counts"]["rootzone_tifs"] == 56
    assert val["variable_checks"]["realistic_volumetric_range"] is True


def test_smap_summary_and_limitations():
    summary = json.loads((PROCESSED_REGIONAL_DIR / "smap_summary.json").read_text(encoding="utf-8"))
    assert "smap_surface_mean" in summary
    assert "smap_rootzone_mean" in summary

    # Physical distinction: root-zone soil moisture is typically higher than top 0-5cm surface in arid conditions
    assert summary["smap_surface_mean"] > 0.0
    assert summary["smap_rootzone_mean"] > summary["smap_surface_mean"]

    # Mandatory limitation check
    assert "Regional soil-moisture context; not an exact field measurement." in summary["smap_limitation"]

    # File output check
    json_path = PROCESSED_REGIONAL_DIR / "smap_summary.json"
    assert json_path.exists()
    with open(json_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["smap_surface_mean"] == summary["smap_surface_mean"]
