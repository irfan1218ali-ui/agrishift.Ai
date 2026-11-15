"""
Tests for K-Means unsupervised clustering, reproducibility, neutral labels, and artifact integrity.
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from ml.clustering.predict import ClusterPredictor
from ml.clustering.prepare_features import fit_scaler, load_and_validate_features

ROOT_DIR = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = ROOT_DIR / "ml" / "clustering" / "artifacts"
FEATURE_TABLE = ROOT_DIR / "data" / "processed" / "features" / "pilot_feature_table.csv"

FORBIDDEN_LABELS = [
    "healthy",
    "diseased",
    "failed",
    "failure",
    "productive",
    "unproductive",
    "suitable",
    "unsuitable",
    "optimal",
    "bad",
    "good",
]

ALLOWED_NEUTRAL_LABELS = {
    "Relatively vegetated",
    "Intermediate condition",
    "Higher bare/thermal exposure",
}


def test_kmeans_reproducibility():
    df, X, meta = load_and_validate_features()
    scaler, X_scaled = fit_scaler(X)

    # Two runs with same random_state=42 must produce identical labels
    km1 = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels1 = km1.fit_predict(X_scaled)

    km2 = KMeans(n_clusters=3, random_state=42, n_init=10)
    labels2 = km2.fit_predict(X_scaled)

    np.testing.assert_array_equal(labels1, labels2, err_msg="K-Means must be strictly reproducible with random_state=42")


def test_artifacts_exist_and_loadable():
    expected_artifacts = [
        "scaler.joblib",
        "kmeans.joblib",
        "cluster_profile.json",
        "metrics.json",
        "training_manifest.json",
    ]
    for art in expected_artifacts:
        p = ARTIFACTS_DIR / art
        assert p.exists(), f"Artifact {art} missing from {ARTIFACTS_DIR}"

    scaler = joblib.load(ARTIFACTS_DIR / "scaler.joblib")
    kmeans = joblib.load(ARTIFACTS_DIR / "kmeans.joblib")
    assert hasattr(scaler, "mean_")
    assert kmeans.n_clusters == 3


def test_cluster_sizes_sum_to_total_valid_rows():
    with open(ARTIFACTS_DIR / "metrics.json", "r", encoding="utf-8") as f:
        metrics = json.load(f)

    sizes = metrics["selected_k_metrics"]["cluster_sizes"]
    total_samples = sum(sizes.values())

    df = pd.read_csv(FEATURE_TABLE)
    assert total_samples == len(df), f"Cluster sizes sum ({total_samples}) != feature table count ({len(df)})"

    # All clusters must have at least 15 observations (no tiny clusters)
    for cid, count in sizes.items():
        assert count >= 15, f"Cluster {cid} has only {count} observations (too small)"


def test_neutral_labels_policy():
    with open(ARTIFACTS_DIR / "cluster_profile.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)

    for cid, prof in profiles.items():
        label = prof["cluster_label"]
        assert label in ALLOWED_NEUTRAL_LABELS, f"Cluster label '{label}' not in allowed neutral labels"

        # Strictly check that no forbidden diagnostic labels are in label or interpretation
        label_lower = label.lower()
        interp_lower = prof["interpretation"].lower()
        for forbidden in FORBIDDEN_LABELS:
            assert forbidden not in label_lower, f"Forbidden diagnostic word '{forbidden}' in cluster label: {label}"
            assert forbidden not in interp_lower, f"Forbidden diagnostic word '{forbidden}' in cluster interpretation"


def test_cluster_predictor_interface():
    predictor = ClusterPredictor()
    sample = {
        "ndvi_mean": 0.60,
        "ndmi_mean": 0.25,
        "bsi_mean": -0.15,
        "surface_temp_c": 36.5,
        "elevation_m": 21.0,
        "slope_deg": 1.5,
    }
    pred = predictor.predict_single(sample)
    assert "cluster_id" in pred
    assert "cluster_label" in pred
    assert "cluster_distance" in pred
    assert pred["cluster_label"] in ALLOWED_NEUTRAL_LABELS
    assert pred["cluster_distance"] >= 0.0
