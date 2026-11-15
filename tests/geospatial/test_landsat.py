"""
Tests for Landsat 9 Collection 2 Level-2 validation, spectral index formulas, scaling, and masking.
"""

from pathlib import Path
import numpy as np
import rasterio

from geospatial.landsat.process_landsat import (
    NODATA_VALUE_FLOAT,
    compute_spectral_indices,
    safe_divide,
)
from geospatial.landsat.validate_landsat import (
    DEFAULT_LANDSAT_DIR,
    validate_landsat_bundle,
)

ROOT_DIR = Path(__file__).resolve().parents[2]
PROCESSED_LANDSAT_DIR = ROOT_DIR / "data" / "processed" / "landsat"


def test_landsat_validation_bundle():
    val = validate_landsat_bundle(DEFAULT_LANDSAT_DIR)
    assert val["is_valid"], f"Landsat validation failed: {val['errors']}"
    assert len(val["missing_bands"]) == 0
    assert val["metadata"]["satellite"] in ["LANDSAT_8", "LANDSAT_9"]
    assert val["pilot_qa_summary"]["cloud_free_fraction_on_swath"] > 0.90


def test_spectral_index_formulas():
    # Synthetic test vectors
    blue = np.array([0.05, 0.10], dtype=np.float32)
    green = np.array([0.08, 0.12], dtype=np.float32)
    red = np.array([0.06, 0.15], dtype=np.float32)
    nir = np.array([0.40, 0.20], dtype=np.float32)
    swir1 = np.array([0.15, 0.25], dtype=np.float32)
    valid_mask = np.array([True, True], dtype=bool)

    indices = compute_spectral_indices(blue, green, red, nir, swir1, valid_mask)

    # Hand-calculated expected values
    expected_ndvi_0 = (0.40 - 0.06) / (0.40 + 0.06)
    expected_ndvi_1 = (0.20 - 0.15) / (0.20 + 0.15)
    np.testing.assert_allclose(indices["ndvi"], [expected_ndvi_0, expected_ndvi_1], rtol=1e-5)

    expected_ndmi_0 = (0.40 - 0.15) / (0.40 + 0.15)
    expected_ndmi_1 = (0.20 - 0.25) / (0.20 + 0.25)
    np.testing.assert_allclose(indices["ndmi"], [expected_ndmi_0, expected_ndmi_1], rtol=1e-5)

    expected_bsi_0 = ((0.15 + 0.06) - (0.40 + 0.05)) / ((0.15 + 0.06) + (0.40 + 0.05))
    expected_bsi_1 = ((0.25 + 0.15) - (0.20 + 0.10)) / ((0.25 + 0.15) + (0.20 + 0.10))
    np.testing.assert_allclose(indices["bsi"], [expected_bsi_0, expected_bsi_1], rtol=1e-5)


def test_safe_division_and_nodata_preservation():
    num = np.array([1.0, 0.0, 5.0], dtype=np.float32)
    den = np.array([0.0, 0.0, 10.0], dtype=np.float32)
    mask = np.array([True, True, True], dtype=bool)

    out = safe_divide(num, den, mask)
    assert out[0] == NODATA_VALUE_FLOAT, "Division by zero should result in NoData"
    assert out[1] == NODATA_VALUE_FLOAT, "0/0 should result in NoData"
    assert np.isclose(out[2], 0.5), "5/10 should evaluate to 0.5"


def test_processed_landsat_rasters():
    for f in ["ndvi.tif", "ndmi.tif", "bsi.tif", "surface_temperature_c.tif", "cloud_free_mask.tif"]:
        path = PROCESSED_LANDSAT_DIR / f
        assert path.exists(), f"Processed raster missing: {path}"
        with rasterio.open(path) as ds:
            assert ds.crs is not None, f"CRS missing on {f}"
            assert ds.bounds is not None, f"Bounds missing on {f}"
            arr = ds.read(1)
            assert arr.size > 0
            if f != "cloud_free_mask.tif":
                assert ds.nodata == NODATA_VALUE_FLOAT
                valid = arr[arr != NODATA_VALUE_FLOAT]
                assert len(valid) > 1000, f"Too few valid pixels in {f}"
