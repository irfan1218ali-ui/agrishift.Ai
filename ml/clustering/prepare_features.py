"""
Feature Preparation Pipeline for Unsupervised Environmental Clustering.
Loads the pilot feature table, verifies variance and row counts, and prepares standardized matrices.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DEFAULT_FEATURE_TABLE = ROOT_DIR / "data" / "processed" / "features" / "pilot_feature_table.csv"

CLUSTERING_FEATURES = [
    "ndvi_mean",
    "ndmi_mean",
    "bsi_mean",
    "surface_temp_c",
    "elevation_m",
    "slope_deg",
]

MIN_SAMPLE_SIZE = 20


def load_and_validate_features(
    csv_path: Path = DEFAULT_FEATURE_TABLE,
    features: list[str] = CLUSTERING_FEATURES,
) -> tuple[pd.DataFrame, np.ndarray, dict[str, Any]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Feature table not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # Validate required columns
    missing_cols = [f for f in features if f not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required feature columns: {missing_cols}")

    # Drop any rows with NaN in features
    clean_df = df.dropna(subset=features).copy()
    valid_count = len(clean_df)

    if valid_count < MIN_SAMPLE_SIZE:
        raise ValueError(
            f"Insufficient valid points ({valid_count}) for clustering. Minimum required is {MIN_SAMPLE_SIZE}."
        )

    # Check variance
    variances = clean_df[features].var()
    low_var_features = [f for f, v in variances.items() if v < 1e-5]
    if low_var_features:
        raise ValueError(f"Features have near-zero variance: {low_var_features}")

    meta = {
        "input_points_total": int(len(df)),
        "valid_points_count": valid_count,
        "features_used": features,
        "features_excluded": [col for col in df.columns if col not in features and col not in ["id", "lat", "lon"]],
        "feature_statistics": clean_df[features].describe().to_dict(),
    }

    X = clean_df[features].values
    return clean_df, X, meta


def fit_scaler(X: np.ndarray) -> tuple[StandardScaler, np.ndarray]:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return scaler, X_scaled


if __name__ == "__main__":
    df, X, meta = load_and_validate_features()
    scaler, X_scaled = fit_scaler(X)
    print(f"Loaded {len(df)} points. Feature matrix shape: {X_scaled.shape}")
    print("Feature means in original space:")
    for f, mean in zip(CLUSTERING_FEATURES, scaler.mean_):
        print(f"  {f}: {mean:.4f}")
