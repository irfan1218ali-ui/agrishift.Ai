"""Unit checks for the Landsat transforms; these are formula fixtures, not field data."""
import numpy as np
import pytest

from scripts.build_real_features import qa_clear, scale_reflectance, scale_temperature_c, spectral_indices


def test_landsat_scale_transforms():
    assert np.isclose(scale_reflectance(np.array([10_000]), 0.0000275, -0.2)[0], 0.075)
    assert round(scale_temperature_c(np.array([44_000]), 0.00341802, 149.0)[0], 2) == 26.24


def test_qa_pixel_masks_fill_cloud_shadow_and_snow_bits():
    flags = np.array([0, 1, 8, 16, 32, 64], dtype=np.uint16)
    assert qa_clear(flags).tolist() == [True, False, False, False, False, True]


def test_index_math_uses_expected_band_relationships():
    blue = np.array([0.1])
    red = np.array([0.2])
    nir = np.array([0.6])
    swir = np.array([0.3])
    ndvi, ndmi, bsi = spectral_indices(blue, red, nir, swir)
    assert np.isclose(ndvi[0], 0.5)
    assert np.isclose(ndmi[0], 1 / 3)
    assert np.isclose(bsi[0], -1 / 6)


def test_missing_landsat_bundle_is_reported_before_any_feature_output(tmp_path):
    from scripts.build_real_features import resolve_landsat

    with pytest.raises(FileNotFoundError, match="Landsat scene directory is missing"):
        resolve_landsat(tmp_path / "empty-scene")
