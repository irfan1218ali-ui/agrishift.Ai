"""
K-Means Clustering Evaluator.
Evaluates k=2, 3, 4 using Silhouette score, Davies-Bouldin index, inertia, and cluster size distributions.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.clustering.prepare_features import fit_scaler, load_and_validate_features

RANDOM_STATE = 42
EVAL_K_VALUES = [2, 3, 4]


def evaluate_kmeans_models(
    X_scaled: np.ndarray,
    k_values: list[int] = EVAL_K_VALUES,
    random_state: int = RANDOM_STATE,
) -> dict[str, Any]:
    evaluation_results = {}

    for k in k_values:
        km = KMeans(n_clusters=k, random_state=random_state, n_init=10)
        labels = km.fit_predict(X_scaled)

        sil = float(silhouette_score(X_scaled, labels))
        db = float(davies_bouldin_score(X_scaled, labels))
        inertia = float(km.inertia_)

        sizes = {}
        for cluster_id in range(k):
            sizes[str(cluster_id)] = int((labels == cluster_id).sum())

        evaluation_results[str(k)] = {
            "k": k,
            "silhouette_score": round(sil, 4),
            "davies_bouldin_index": round(db, 4),
            "inertia": round(inertia, 2),
            "cluster_sizes": sizes,
            "min_cluster_size": min(sizes.values()),
        }

    return evaluation_results


if __name__ == "__main__":
    df, X, meta = load_and_validate_features()
    scaler, X_scaled = fit_scaler(X)
    evals = evaluate_kmeans_models(X_scaled)
    print("K-Means Model Evaluation (k=2, 3, 4):")
    print(json.dumps(evals, indent=2))
