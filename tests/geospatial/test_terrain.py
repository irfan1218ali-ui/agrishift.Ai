"""
Tests for SRTM DEM terrain processing, elevation bounds, and slope calculations.
"""

from pathlib import Path
import numpy as np
import rasterio

from geospatial.terrain.process_terrain import calculate_slope_horn
from geospatial.terrain.validate_terrain import validate_terrain

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_TERRAIN_DIR = ROOT_DIR / "data" / "processed" / "terrain"


def test_terrain_validation():
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
    for f in ["elevation.tif", "slope_degrees.tif", "low_lying_flag.tif"]:
        p = PROCESSED_TERRAIN_DIR / f
        assert p.exists(), f"Processed terrain file {f} missing"
        with rasterio.open(p) as ds:
            assert ds.crs is not None
            assert ds.bounds is not None
            arr = ds.read(1)
            assert arr.size > 0
            if f == "slope_degrees.tif":
                valid = arr[arr != -9999.0]
                assert (valid >= 0.0).all(), "Slope cannot be negative"
                assert (valid <= 90.0).all(), "Slope cannot exceed 90 degrees"
            elif f == "low_lying_flag.tif":
                unique_vals = set(np.unique(arr))
                assert unique_vals.issubset({0, 1})
