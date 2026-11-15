"""
Tests for map overlay files, dimensions, transparency, and metadata.
"""

import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parents[2]
LAYERS_DIR = ROOT_DIR / "data" / "layers"
METADATA_JSON = LAYERS_DIR / "metadata.json"

REQUIRED_LAYERS = ["ndvi.png", "ndmi.png", "bsi.png", "slope.png"]


def test_map_layer_png_files_exist():
    assert LAYERS_DIR.exists(), f"Layers directory not found at {LAYERS_DIR}"
    for layer_file in REQUIRED_LAYERS:
        p = LAYERS_DIR / layer_file
        assert p.exists(), f"Layer file {layer_file} is missing"
        assert p.stat().st_size > 1000, f"Layer file {layer_file} is too small"


def test_map_layers_have_transparency():
    # In RGBA PNGs, NoData should be alpha=0, while valid data should have alpha > 0
    for layer_file in REQUIRED_LAYERS:
        img_path = LAYERS_DIR / layer_file
        with Image.open(img_path) as img:
            assert img.mode == "RGBA", f"Image {layer_file} is not RGBA mode"
            arr = np.array(img)
            alpha = arr[..., 3]
            # Valid data pixels must be visible
            assert (alpha > 0).any(), f"Image {layer_file} has no visible data pixels"
            # Landsat layers have off-swath NoData which must be transparent
            if any(k in layer_file for k in ["ndvi", "ndmi", "bsi"]):
                assert (alpha == 0).any(), f"Image {layer_file} must have transparent NoData for off-swath/cloud areas"


def test_map_layer_metadata():
    assert METADATA_JSON.exists(), f"metadata.json missing at {METADATA_JSON}"
    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        meta = json.load(f)

    assert "bounds" in meta
    bounds = meta["bounds"]
    assert bounds["west"] == 68.2
    assert bounds["south"] == 25.2
    assert bounds["east"] == 68.55
    assert bounds["north"] == 25.55

    assert "layers" in meta
    for k in ["ndvi", "ndmi", "bsi", "slope"]:
        assert k in meta["layers"], f"Layer key {k} missing from metadata"
        layer_meta = meta["layers"][k]
        assert layer_meta["minimum"] <= layer_meta["maximum"]
        assert layer_meta["source_resolution_m"] == 30
        assert "limitation" in layer_meta and len(layer_meta["limitation"]) > 0
