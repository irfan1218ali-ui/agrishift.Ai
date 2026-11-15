"""Settings (environment driven). Also puts the rotation engine on sys.path."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]            # .../agrishift
ENGINE_DIR = ROOT / "services" / "rotation-engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))


@dataclass(frozen=True)
class Settings:
    root: Path
    demo_mode: bool                 # DEMO_MODE=1 -> allow the EXAMPLE features file + saved weather sample
    features_path: Path
    features_example_path: Path
    crops_csv: Path
    samples_dir: Path
    cache_dir: Path
    layers_dir: Path
    web_dir: Path
    meteomatics_user: str
    meteomatics_password: str
    cors_origins: list
    power_live_enabled: bool = False
    power_csv_path: Path | None = None
    meteomatics_sample_path: Path | None = None
    # pilot area (Hyderabad, Sindh) - same box as the frontend
    min_lat: float = 25.1
    max_lat: float = 25.7
    min_lon: float = 68.1
    max_lon: float = 68.7
    features_max_km: float = 5.0    # nearest features point must be within this distance
    min_cloud_free: float = 0.5     # Landsat treated as unusable below this cloud-free fraction (unverified)
    default_satellite_window: str = "2025-09-01/2025-09-30"
    default_landsat_date: str = "2025-09-22"


def get_settings() -> Settings:
    env = os.environ.get
    root = Path(env("AGRISHIFT_ROOT", str(ROOT)))
    demo = env("DEMO_MODE", "false").lower() in ("1", "true", "yes")
    feature_override = env("FEATURES_FILE", env("FEATURES_PATH", ""))
    if feature_override:
        features = Path(feature_override)
    else:
        real = root / "data" / "features" / "features.json"
        example = Path(env("FEATURES_EXAMPLE_FILE", str(root / "data" / "features" / "features.example.json")))
        features = example if (demo and not real.exists()) else real
    origins = [o.strip() for o in env(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000"
    ).split(",") if o.strip()]
    if env("APP_ENV", "development").lower() == "production" and "*" in origins:
        raise ValueError("CORS_ORIGINS must not contain '*' in production")
    power_csv = Path(env("NASA_POWER_CSV")) if env("NASA_POWER_CSV") else None
    if power_csv is None:
        candidates = sorted((root / "data" / "api-samples" / "nasa-power").glob("POWER_Point_Daily_*.csv"))
        power_csv = candidates[0] if candidates else None
    meteomatics_sample = Path(env(
        "METEOMATICS_SAMPLE_FILE", str(root / "data" / "api-samples" / "meteomatics" / "json.json")
    ))
    return Settings(
        root=root,
        demo_mode=demo,
        features_path=features,
        features_example_path=Path(env("FEATURES_EXAMPLE_FILE", str(root / "data" / "features" / "features.example.json"))),
        crops_csv=Path(env("CROPS_CSV", str(root / "knowledge" / "crops.csv"))),
        samples_dir=root / "data" / "api-samples",
        cache_dir=Path(env("CACHE_DIR", str(root / "data" / "cache"))),
        layers_dir=Path(env("LAYER_DIRECTORY", env("LAYERS_DIR", str(root / "data" / "layers")))),
        web_dir=Path(env("WEB_DIR", str(root / "apps" / "web"))),
        meteomatics_user=env("METEOMATICS_USERNAME", env("METEOMATICS_USER", "")),
        meteomatics_password=env("METEOMATICS_PASSWORD", ""),
        cors_origins=origins,
        power_live_enabled=env("POWER_LIVE_ENABLED", "false").lower() in ("1", "true", "yes"),
        power_csv_path=power_csv,
        meteomatics_sample_path=meteomatics_sample,
    )
