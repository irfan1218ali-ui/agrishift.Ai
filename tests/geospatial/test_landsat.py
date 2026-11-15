"""
Tests for Landsat 9 Collection 2 Level-2 validation, spectral index formulas, scaling, and masking.
"""

from pathlib import Path
import numpy as np

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
def test_landsat_validation_bundle():
    if not DEFAULT_LANDSAT_DIR.exists():
        import pytest
        pytest.skip("Raw Landsat scene files are excluded; validated scene evidence is committed separately.")
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
    import json
    from PIL import Image

    features = json.loads((ROOT_DIR / "data" / "features" / "features.json").read_text(encoding="utf-8"))
    assert len(features["points"]) == 149
    for name in ("ndvi", "ndmi", "bsi"):
        path = ROOT_DIR / "data" / "layers" / f"{name}.png"
        assert path.is_file(), f"Processed {name} overlay missing"
        with Image.open(path) as image:
            assert image.format == "PNG" and image.width > 0 and image.height > 0
    assert features["meta"]["source_dates"]["landsat_9"] == "2025-09-30"
