"""
Tests for scientific dataset discovery, manifest integrity, columns, and SHA-256 checksums.
"""

import csv
from pathlib import Path
import re

ROOT_DIR = Path(__file__).resolve().parents[2]
MANIFESTS_DIR = ROOT_DIR / "data" / "manifests"
CATALOG_PATH = ROOT_DIR / "data" / "catalog" / "data-status.csv"

EXPECTED_MANIFEST_FILES = [
    "landsat-files.csv",
    "terrain-files.csv",
    "gpm-files.csv",
    "smap-files.csv",
    "power-files.csv",
    "meteomatics-files.csv",
]

REQUIRED_MANIFEST_COLUMNS = [
    "file_name",
    "relative_path",
    "provider",
    "product",
    "version",
    "variable",
    "observation_datetime",
    "format",
    "crs",
    "bounds",
    "width",
    "height",
    "pixel_size",
    "unit",
    "nodata",
    "scale_factor",
    "offset",
    "minimum",
    "maximum",
    "mean",
    "valid_pixel_count",
    "sha256",
    "validation_status",
    "notes",
]


def test_data_status_catalog_exists_and_valid():
    assert CATALOG_PATH.exists(), f"Catalog not found at {CATALOG_PATH}"
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) >= 6, "Expected at least 6 catalog entries"
    source_ids = [r["dataset_id"] for r in rows]
    assert any("landsat" in s for s in source_ids)
    assert any("smap" in s for s in source_ids)
    assert any("gpm" in s for s in source_ids)
    assert any("terrain" in s or "srtm" in s for s in source_ids)
    assert any("power" in s for s in source_ids)
    assert any("meteomatics" in s for s in source_ids)

    valid_statuses = {
        "DISCOVERED",
        "VALIDATION_PENDING",
        "VALIDATED",
        "VALIDATION_FAILED",
        "VALIDATED_CONTEXT_ONLY",
        "VALIDATED_SLOPE_DERIVED",
        "SAVED_CSV_VALIDATED",
        "SAVED_SAMPLE_VALIDATED_NOT_LIVE",
        "MISSING",
        "INCOMPLETE",
        "PROCESSING_READY",
    }
    for r in rows:
        assert r["status"] in valid_statuses, f"Invalid status: {r['status']}"


def test_manifest_files_exist_and_have_required_columns():
    for m_name in EXPECTED_MANIFEST_FILES:
        m_path = MANIFESTS_DIR / m_name
        assert m_path.exists(), f"Manifest file missing: {m_path}"

        with open(m_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            rows = list(reader)

        assert headers == REQUIRED_MANIFEST_COLUMNS, f"Column mismatch in {m_name}: {headers}"
        assert len(rows) > 0, f"Manifest {m_name} is empty"

        # Check uniqueness of relative_path
        paths = [r["relative_path"] for r in rows]
        assert len(paths) == len(set(paths)), f"Duplicate relative_path found in {m_name}"

        # Check SHA-256 formatting
        sha_pattern = re.compile(r"^[0-9a-f]{64}$")
        for r in rows:
            sha = r["sha256"]
            assert sha_pattern.match(sha), f"Invalid SHA-256 checksum '{sha}' in {m_name} for file {r['file_name']}"
