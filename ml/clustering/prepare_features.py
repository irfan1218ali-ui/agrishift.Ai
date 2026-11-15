"""Load real, complete spatial feature observations for clustering."""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "data" / "features" / "features.json"
FEATURES = ("ndvi_mean", "ndmi_mean", "bsi_mean", "surface_temp_c", "elevation_m", "slope_deg")
MINIMUM_OBSERVATIONS = 20


def load_observations(path: Path = DEFAULT_INPUT) -> tuple[list[dict], np.ndarray]:
    """Read only real features.json; never fall back to example data or fill missing values."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Real feature file is missing: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    points = payload.get("points") if isinstance(payload, dict) else None
    if not isinstance(points, list):
        raise ValueError("Feature file must contain a points list")
    accepted, matrix = [], []
    for point in points:
        if not isinstance(point, dict):
            continue
        features = point.get("features") or {}
        coordinates = (point.get("lat"), point.get("lon"))
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v)
               for v in coordinates):
            continue
        values = [features.get(name) for name in FEATURES]
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v)
               for v in values):
            continue
        accepted.append(point)
        matrix.append([float(value) for value in values])
    unique_locations = {(round(float(p["lat"]), 6), round(float(p["lon"]), 6)) for p in accepted}
    if len(accepted) < MINIMUM_OBSERVATIONS or len(unique_locations) < MINIMUM_OBSERVATIONS:
        raise ValueError(
            f"K-Means needs at least {MINIMUM_OBSERVATIONS} complete, distinct real spatial observations; "
            f"found {len(accepted)} complete rows and {len(unique_locations)} unique locations"
        )
    return accepted, np.asarray(matrix, dtype=np.float64)
