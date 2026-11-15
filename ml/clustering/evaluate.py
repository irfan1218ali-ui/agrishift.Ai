"""Display saved K-Means evaluation metrics without inventing an evaluation run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .train_kmeans import DEFAULT_OUTPUT
except ImportError:  # Direct script execution from the repository root.
    from train_kmeans import DEFAULT_OUTPUT


def read_metrics(model_dir: Path = DEFAULT_OUTPUT) -> dict:
    metrics_path = Path(model_dir) / "metrics.json"
    if not metrics_path.is_file():
        raise FileNotFoundError(f"No trained-model metrics exist: {metrics_path}")
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    if not payload.get("evaluations"):
        raise ValueError("The saved metrics file has no evaluated K-Means configurations")
    return payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(read_metrics(args.model_dir), indent=2))
