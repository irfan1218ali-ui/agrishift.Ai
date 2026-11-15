"""
K-Means Inference Pipeline.
Loads serialized artifacts, applies scaling, and predicts cluster ID, neutral label,
and distance to cluster centroid for arbitrary feature observations.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any
import joblib
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ml.clustering.prepare_features import CLUSTERING_FEATURES

ARTIFACTS_DIR = ROOT_DIR / "ml" / "clustering" / "artifacts"


class ClusterPredictor:
    def __init__(self, artifacts_dir: Path = ARTIFACTS_DIR):
        self.artifacts_dir = artifacts_dir
        self.scaler = joblib.load(artifacts_dir / "scaler.joblib")
        self.kmeans = joblib.load(artifacts_dir / "kmeans.joblib")

        with open(artifacts_dir / "cluster_profile.json", "r", encoding="utf-8") as f:
            self.profiles = json.load(f)

        self.label_map = {int(k): v["cluster_label"] for k, v in self.profiles.items()}

    def predict_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        out_df = df.copy()
        X = out_df[CLUSTERING_FEATURES].values
        X_scaled = self.scaler.transform(X)

        cluster_ids = self.kmeans.predict(X_scaled)
        centers_scaled = self.kmeans.cluster_centers_

        # Euclidean distance to assigned centroid
        distances = np.linalg.norm(X_scaled - centers_scaled[cluster_ids], axis=1)

        out_df["cluster_id"] = cluster_ids
        out_df["cluster_label"] = [self.label_map[cid] for cid in cluster_ids]
        out_df["cluster_distance"] = np.round(distances, 4)
        return out_df

    def predict_single(self, features: dict[str, float]) -> dict[str, Any]:
        row = [features[f] for f in CLUSTERING_FEATURES]
        X = np.array([row])
        X_scaled = self.scaler.transform(X)

        cid = int(self.kmeans.predict(X_scaled)[0])
        dist = float(np.linalg.norm(X_scaled - self.kmeans.cluster_centers_[cid]))

        return {
            "cluster_id": cid,
            "cluster_label": self.label_map[cid],
            "cluster_distance": round(dist, 4),
        }


if __name__ == "__main__":
    predictor = ClusterPredictor()
    sample = {
        "ndvi_mean": 0.55,
        "ndmi_mean": 0.22,
        "bsi_mean": -0.12,
        "surface_temp_c": 38.0,
        "elevation_m": 20.0,
        "slope_deg": 1.5,
    }
    pred = predictor.predict_single(sample)
    print("Sample prediction:")
    print(json.dumps(pred, indent=2))
