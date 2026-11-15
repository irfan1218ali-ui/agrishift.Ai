"""Input validation tests for the CSV feature preparation pipeline."""
import pandas as pd

import pytest

from ml.clustering.prepare_features import CLUSTERING_FEATURES, load_and_validate_features
from ml.clustering.train_kmeans import train_clustering_pipeline


def _frame(rows):
    return pd.DataFrame(rows, columns=["id", "lat", "lon", *CLUSTERING_FEATURES])


def test_missing_real_feature_file_does_not_use_an_example(tmp_path):
    with pytest.raises(FileNotFoundError, match="Feature table not found"):
        load_and_validate_features(tmp_path / "features.csv")


def test_rejects_empty_real_feature_rows(tmp_path):
    feature_file = tmp_path / "features.csv"
    _frame([]).to_csv(feature_file, index=False)
    with pytest.raises(ValueError, match=r"Insufficient complete, finite, distinct spatial points \(0\)"):
        load_and_validate_features(feature_file)


def test_rejects_nonfinite_and_incomplete_feature_rows(tmp_path):
    feature_file = tmp_path / "features.csv"
    rows = []
    for index in range(20):
        values = {name: float(index + 1) for name in CLUSTERING_FEATURES}
        if index == 19:
            values["ndvi_mean"] = float("inf")
        if index == 18:
            values["ndmi_mean"] = float("nan")
        rows.append({"id": str(index), "lat": 25 + index * 0.001, "lon": 68.3, **values})
    _frame(rows).to_csv(feature_file, index=False)
    with pytest.raises(ValueError, match=r"distinct spatial points \(18\)"):
        load_and_validate_features(feature_file)


def test_duplicate_coordinates_do_not_count_as_distinct_observations(tmp_path):
    feature_file = tmp_path / "features.csv"
    rows = []
    for index in range(20):
        rows.append({"id": str(index), "lat": 25.3, "lon": 68.3,
                     **{name: float(index + 1) for name in CLUSTERING_FEATURES}})
    _frame(rows).to_csv(feature_file, index=False)
    with pytest.raises(ValueError, match=r"distinct spatial points \(1\)"):
        load_and_validate_features(feature_file)


def test_training_missing_input_writes_no_model_artifacts(tmp_path):
    artifact_dir = tmp_path / "artifacts"
    with pytest.raises(FileNotFoundError, match="Feature table not found"):
        train_clustering_pipeline(csv_path=tmp_path / "features.csv", artifacts_dir=artifact_dir)
    assert not artifact_dir.exists()
