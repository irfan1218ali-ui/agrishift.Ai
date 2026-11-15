"""Load and validate the trained environmental K-Means artifacts once."""
from __future__ import annotations

import hashlib
import json
import logging
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import sklearn

logger = logging.getLogger(__name__)
FEATURE_ORDER = (
    "ndvi_mean", "ndmi_mean", "bsi_mean", "surface_temp_c", "elevation_m", "slope_deg",
)
ALLOWED_LABELS = {
    "Relatively vegetated", "Intermediate condition", "Higher bare/thermal exposure",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@lru_cache(maxsize=4)
def load_artifacts(directory: Path) -> dict:
    """Verify manifest checksums/schema, then load model objects once per path."""
    directory = Path(directory)
    manifest = json.loads((directory / "training_manifest.json").read_text(encoding="utf-8"))
    if tuple(manifest.get("features_used", ())) != FEATURE_ORDER:
        raise ValueError("K-Means artifact feature order does not match the API schema")
    expected_sklearn = str(manifest.get("library_version", "")).removeprefix("scikit-learn==")
    if expected_sklearn != sklearn.__version__ or manifest.get("joblib_version") != joblib.__version__:
        raise ValueError("K-Means artifact library versions do not match the installed environment")
    required = ("scaler", "kmeans", "cluster_profile", "metrics")
    for key in required:
        record = manifest.get("artifacts", {}).get(key) or {}
        path = directory / str(record.get("file", ""))
        if not path.is_file() or _sha256(path) != record.get("sha256"):
            raise ValueError(f"K-Means artifact checksum failed: {key}")
    profile = json.loads((directory / manifest["artifacts"]["cluster_profile"]["file"]).read_text(encoding="utf-8"))
    metrics = json.loads((directory / manifest["artifacts"]["metrics"]["file"]).read_text(encoding="utf-8"))
    labels = {int(key): value for key, value in profile.items()}
    if not labels or any(row.get("cluster_label") not in ALLOWED_LABELS for row in labels.values()):
        raise ValueError("K-Means cluster profiles contain an unknown or diagnostic label")
    scaler = joblib.load(directory / manifest["artifacts"]["scaler"]["file"])
    model = joblib.load(directory / manifest["artifacts"]["kmeans"]["file"])
    if getattr(model, "n_features_in_", None) != len(FEATURE_ORDER):
        raise ValueError("K-Means model feature count is invalid")
    if getattr(scaler, "n_features_in_", None) != len(FEATURE_ORDER):
        raise ValueError("K-Means scaler feature count is invalid")
    k = int(metrics.get("selected_k", 0))
    if getattr(model, "n_clusters", None) != k or set(labels) != set(range(k)):
        raise ValueError("K-Means model, metrics, and cluster profiles disagree")
    version = f"kmeans-k{k}-{manifest.get('library_version', 'unknown')}"
    return {"manifest": manifest, "profile": labels, "metrics": metrics,
            "scaler": scaler, "model": model, "model_version": version}


def describe_cluster(artifacts_dir: Path, point: dict, features: dict) -> dict | None:
    """Return the saved neutral cluster; recompute only to check assignment integrity."""
    try:
        artifacts = load_artifacts(Path(artifacts_dir).resolve())
        saved = point.get("clustering") or point
        saved_id = saved.get("cluster_id")
        saved_id = int(saved_id) if saved_id is not None else None
        vector = np.asarray([[float(features[name]) for name in FEATURE_ORDER]], dtype=float)
        scaled = artifacts["scaler"].transform(vector)
        predicted_id = int(artifacts["model"].predict(scaled)[0])
        if saved_id is not None and saved_id != predicted_id:
            logger.warning("Saved K-Means assignment differs for feature point %s; keeping the saved label.",
                           point.get("id"))
        cluster_id = saved_id if saved_id in artifacts["profile"] else predicted_id
        profile = artifacts["profile"][cluster_id]
        label = profile["cluster_label"]
        saved_label = saved.get("cluster_label")
        if saved_id is not None and saved_label in ALLOWED_LABELS and saved_label != label:
            logger.warning("Saved K-Means label/profile mismatch for feature point %s; using the reviewed profile.",
                           point.get("id"))
        distance = saved.get("cluster_distance")
        if distance is None:
            distance = float(artifacts["model"].transform(scaled)[0, cluster_id])
        return {
            "cluster_id": cluster_id,
            "cluster_label": label,
            "cluster_distance": round(float(distance), 4),
            "interpretation": profile.get("interpretation", "Neutral environmental grouping."),
            "model_name": artifacts["manifest"].get("model_name", "AgriShift Environmental K-Means"),
            "model_version": artifacts["model_version"],
            "diagnostic": False,
            "limitation": "Environmental clustering, not crop-health or disease diagnosis.",
        }
    except (OSError, ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError, ImportError) as exc:
        logger.warning("Environmental K-Means unavailable: %s", exc)
        return None
