"""Settings (environment driven). Also puts the rotation engine on sys.path."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]            # .../agrishift


def _load_local_env() -> None:
    """Load simple KEY=VALUE settings without overriding variables supplied by the shell."""
    env_file = ROOT / ".env"
    if not env_file.is_file():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key and key not in os.environ:
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            os.environ[key] = value


_load_local_env()
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
    features_max_km: float = 2.0    # enforce the measured approximately 2 km point grid
    min_cloud_free: float = 0.5     # Landsat treated as unusable below this cloud-free fraction (unverified)
    default_satellite_window: str = "2025-09-01/2025-09-30"
    default_landsat_date: str = "2025-09-30"


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
        features = example if demo else real
    origins = [o.strip() for o in env(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000"
    ).split(",") if o.strip()]
    app_env = env("APP_ENV", "development").strip().lower()
    if app_env == "production":
        if "*" in origins:
            raise ValueError("CORS_ORIGINS must not contain '*' in production")
        if len(env("EXPERT_SESSION_SECRET", "")) < 32:
            raise ValueError("EXPERT_SESSION_SECRET must contain at least 32 characters in production")
        if not env("EXPERT_EMAIL", "").strip() or not env("EXPERT_PASSWORD_HASH", "").strip():
            raise ValueError("EXPERT_EMAIL and EXPERT_PASSWORD_HASH are required in production")
        if not env("EXPERT_PASSWORD_HASH", "").startswith("pbkdf2_sha256$"):
            raise ValueError("EXPERT_PASSWORD_HASH must be a PBKDF2-SHA256 hash in production")
    power_csv = Path(env("NASA_POWER_CSV")) if env("NASA_POWER_CSV") else None
    if power_csv is None:
        candidates = sorted((root / "data" / "api-samples" / "nasa-power").glob("POWER_Point_Daily_*.csv"))
        power_csv = candidates[0] if candidates else None
    configured_weather_sample = env("METEOMATICS_SAMPLE_FILE", "").strip()
    if configured_weather_sample:
        meteomatics_sample = Path(configured_weather_sample)
    elif demo:
        meteomatics_sample = root / "data" / "api-samples" / "meteomatics" / "demo_sample.example.json"
    else:
        meteomatics_sample = None
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
