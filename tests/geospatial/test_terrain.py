"""
Tests for SRTM DEM terrain processing, elevation bounds, and slope calculations.
"""

from pathlib import Path
import numpy as np

from geospatial.terrain.process_terrain import calculate_slope_horn
from geospatial.terrain.validate_terrain import DEFAULT_TERRAIN_DIR, validate_terrain

ROOT_DIR = Path(__file__).resolve().parents[2]
def test_terrain_validation():
    if not DEFAULT_TERRAIN_DIR.exists():
        import pytest
        pytest.skip("Raw terrain raster is excluded; derived overlay and feature summaries are committed.")
    report = validate_terrain()
    assert report["is_valid"], f"Terrain validation failed: {report['errors']}"
    assert report["coverage"]["fully_covers_pilot"] is True
    assert report["statistics"]["min_elevation_m"] >= -15.0
    assert report["statistics"]["max_elevation_m"] <= 200.0


def test_slope_calculation_algorithm():
    # Synthetic flat terrain: slope should be 0.0 degrees
    flat_dem = np.full((10, 10), 50.0, dtype=np.float32)
    flat_slope = calculate_slope_horn(flat_dem, cell_size_x=30.0, cell_size_y=30.0)
    assert np.isclose(flat_slope[2:8, 2:8], 0.0).all()

    # Synthetic 45 degree slope: rise = run = 30m over 30m
    # Ramp in x direction: z = x * 30.0
    ramp_x = np.tile(np.arange(10, dtype=np.float32) * 30.0, (10, 1))
    ramp_slope = calculate_slope_horn(ramp_x, cell_size_x=30.0, cell_size_y=30.0)
    # tan(slope) = 1.0 => slope = 45 degrees
    np.testing.assert_allclose(ramp_slope[2:8, 2:8], 45.0, rtol=1e-3)


def test_processed_terrain_rasters():
    import json
    from PIL import Image

    features = json.loads((ROOT_DIR / "data" / "features" / "features.json").read_text(encoding="utf-8"))
    assert len(features["points"]) == 149
    assert all(isinstance(point["features"].get("low_lying_flag"), bool) for point in features["points"])
    layer = ROOT_DIR / "data" / "layers" / "slope.png"
    assert layer.is_file()
    with Image.open(layer) as image:
        assert image.format == "PNG" and image.width > 0 and image.height > 0
