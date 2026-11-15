"""Input validation tests that do not fabricate environmental feature values."""
import json

import pytest

from ml.clustering.prepare_features import load_observations
from ml.clustering.train_kmeans import fit


def test_missing_real_feature_file_does_not_use_example(tmp_path):
    with pytest.raises(FileNotFoundError, match="Real feature file is missing"):
        load_observations(tmp_path / "features.json")


def test_rejects_empty_real_feature_rows(tmp_path):
    feature_file = tmp_path / "features.json"
    feature_file.write_text(json.dumps({"points": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="at least 20 complete, distinct real spatial observations"):
        load_observations(feature_file)


def test_rejects_nonfinite_or_incomplete_values(tmp_path):
    feature_file = tmp_path / "features.json"
    feature_file.write_text(json.dumps({"points": [
        {"id": "incomplete", "lat": 25.3, "lon": 68.3, "features": {"ndvi_mean": 0.4}},
        {"id": "nonfinite", "lat": 25.4, "lon": 68.4, "features": {
            "ndvi_mean": float("nan")}},
    ]}), encoding="utf-8")
    with pytest.raises(ValueError, match="found 0 complete rows"):
        load_observations(feature_file)


def test_training_missing_input_writes_no_model_artifacts(tmp_path):
    artifact_dir = tmp_path / "artifacts"
    with pytest.raises(FileNotFoundError, match="Real feature file is missing"):
        fit(tmp_path / "features.json", artifact_dir)
    assert not artifact_dir.exists()
