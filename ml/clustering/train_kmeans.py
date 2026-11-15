"""Train reproducible environmental-condition clusters from real spatial rows only."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score
from sklearn.preprocessing import StandardScaler

try:
    from .prepare_features import DEFAULT_INPUT, FEATURES, load_observations
except ImportError:  # Direct script execution from the repository root.
    from prepare_features import DEFAULT_INPUT, FEATURES, load_observations


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "ml" / "clustering" / "artifacts"
LABELS_BY_RANK = ("Higher bare/thermal exposure", "Intermediate condition", "Relatively vegetated")


def fit(input_path: Path = DEFAULT_INPUT, output_dir: Path = DEFAULT_OUTPUT) -> dict:
    points, matrix = load_observations(input_path)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(matrix)
    evaluations = []
    models = []
    for k in (2, 3, 4):
        if k >= len(points):
            continue
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(scaled)
        sizes = np.bincount(labels, minlength=k)
        if len(set(labels)) < 2 or len(points) <= k:
            continue
        sil = float(silhouette_score(scaled, labels))
        dbi = float(davies_bouldin_score(scaled, labels))
        evaluations.append({"k": k, "silhouette_score": sil, "davies_bouldin_index": dbi,
                            "cluster_sizes": [int(v) for v in sizes]})
        models.append((model, labels, sizes))
    if not evaluations:
        raise ValueError("No valid k=2,3,4 model could be evaluated on the real observations")
    candidate_index = max(range(len(evaluations)), key=lambda i: (
        evaluations[i]["silhouette_score"], -evaluations[i]["davies_bouldin_index"],
        -evaluations[i]["k"],
    ))
    metrics = {"training_timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "feature_names": list(FEATURES), "observation_count": len(points),
               "random_state": 42, "candidate_selection": "highest silhouette; expert interpretation required",
               "candidate_k": evaluations[candidate_index]["k"], "candidate_status": "requires_review",
               "evaluations": evaluations}
    model, labels, sizes = models[candidate_index]
    centers = scaler.inverse_transform(model.cluster_centers_)
    order = np.argsort(centers[:, FEATURES.index("ndvi_mean")])
    label_by_cluster = {}
    for rank, cluster_id in enumerate(order):
        label_rank = round(rank * (len(LABELS_BY_RANK) - 1) / max(1, len(order) - 1))
        label_by_cluster[int(cluster_id)] = LABELS_BY_RANK[label_rank]
    profiles = []
    for cluster_id, center in enumerate(centers):
        members = matrix[labels == cluster_id]
        profiles.append({"cluster_id": cluster_id, "cluster_label": label_by_cluster[cluster_id],
                         "count": int(sizes[cluster_id]),
                         "feature_means": {name: float(value) for name, value in zip(FEATURES, members.mean(axis=0))},
                         "center": {name: float(value) for name, value in zip(FEATURES, center)}})
    distances = model.transform(scaled)
    clustered = json.loads(Path(input_path).read_text(encoding="utf-8"))
    by_id = {str(point.get("id")): i for i, point in enumerate(points)}
    for point in clustered["points"]:
        index = by_id.get(str(point.get("id")))
        if index is None:
            continue
        cluster_id = int(labels[index])
        point["features"].update({"cluster_id": cluster_id,
                                 "cluster_label": label_by_cluster[cluster_id],
                                 "cluster_distance": float(distances[index, cluster_id])})
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, output_dir / "scaler.joblib")
    joblib.dump(model, output_dir / "kmeans.joblib")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (output_dir / "cluster_profile.json").write_text(json.dumps({"feature_names": list(FEATURES),
        "label_policy": "neutral environmental indicators; not health or crop suitability",
        "profiles": profiles}, indent=2), encoding="utf-8")
    output_points = ROOT / "data" / "processed" / "model-features" / "features.clustered.json"
    output_points.parent.mkdir(parents=True, exist_ok=True)
    output_points.write_text(json.dumps(clustered, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(fit(args.input, args.output), indent=2))
