"""Assign a complete real feature file to a reviewed environmental cluster model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib

try:
    from .prepare_features import DEFAULT_INPUT, FEATURES, load_observations
    from .train_kmeans import DEFAULT_OUTPUT
except ImportError:  # Direct script execution from the repository root.
    from prepare_features import DEFAULT_INPUT, FEATURES, load_observations
    from train_kmeans import DEFAULT_OUTPUT


def predict(input_path: Path = DEFAULT_INPUT, model_dir: Path = DEFAULT_OUTPUT) -> list[dict]:
    points, matrix = load_observations(input_path)
    model_dir = Path(model_dir)
    model_path = model_dir / "kmeans.joblib"
    scaler_path = model_dir / "scaler.joblib"
    profile_path = model_dir / "cluster_profile.json"
    for path in (model_path, scaler_path, profile_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required reviewed model artifact is missing: {path}")
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if tuple(profile.get("feature_names", ())) != FEATURES:
        raise ValueError("Model feature schema does not match the current feature schema")
    labels = model.predict(scaler.transform(matrix))
    distances = model.transform(scaler.transform(matrix))
    labels_by_id = {item["cluster_id"]: item["cluster_label"] for item in profile["profiles"]}
    return [{"id": point.get("id"), "cluster_id": int(cluster_id),
             "cluster_label": labels_by_id[int(cluster_id)],
             "cluster_distance": float(distances[index, cluster_id])}
            for index, (point, cluster_id) in enumerate(zip(points, labels))]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(predict(args.input, args.model_dir), indent=2))
