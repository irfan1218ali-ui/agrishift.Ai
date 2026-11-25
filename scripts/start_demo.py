"""Start the local AgriShift farmer MVP on loopback using real pilot data."""
from __future__ import annotations

import os
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
WEB_DIR = ROOT / "apps" / "web"
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

# Use the committed, validated pilot features by default. Demo inputs require an
# explicit DEMO_MODE=true choice and remain visibly labelled by the API/UI.
os.environ.setdefault("DEMO_MODE", "false")
os.environ.setdefault("AGRISHIFT_ROOT", str(ROOT))
if os.environ["DEMO_MODE"].lower() in ("1", "true", "yes") and not (
        os.environ.get("FEATURES_FILE") or os.environ.get("FEATURES_PATH")):
    os.environ["FEATURES_FILE"] = str(ROOT / "data" / "features" / "features.example.json")
os.environ.setdefault("METEOMATICS_SAMPLE_FILE", str(ROOT / "data" / "processed" / "weather" / "meteomatics_daily.json"))

from app import db  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.ml.clustering import load_artifacts  # noqa: E402


def validate_runtime_assets(settings) -> None:
    if not settings.crops_csv.is_file() or not (WEB_DIR / "package.json").is_file():
        raise FileNotFoundError("The crop knowledge file or Next.js frontend is missing")
    if not settings.features_path.is_file():
        raise FileNotFoundError(f"Selected feature file is missing: {settings.features_path}")
    try:
        feature_document = json.loads(settings.features_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError(f"Selected feature file is not valid JSON: {settings.features_path}") from exc
    points = feature_document.get("points") if isinstance(feature_document, dict) else None
    if not isinstance(points, list) or not points:
        raise RuntimeError("Selected feature file contains no usable analysis points")
    if not settings.demo_mode and len(points) != 149:
        raise RuntimeError(f"Real pilot features must contain 149 points; found {len(points)}")
    for layer_name in ("ndvi.png", "ndmi.png", "bsi.png", "slope.png", "metadata.json"):
        if not (settings.layers_dir / layer_name).is_file():
            raise FileNotFoundError(f"Required map layer asset is missing: {settings.layers_dir / layer_name}")
    try:
        load_artifacts((settings.root / "ml" / "clustering" / "artifacts").resolve())
    except Exception as exc:
        raise RuntimeError(f"K-Means artifacts failed integrity validation: {exc}") from exc


def main() -> None:
    settings = get_settings()
    validate_runtime_assets(settings)
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Python API dependencies are missing; run python -m pip install -r requirements.lock.txt") from exc

    host = os.environ.get("AGRISHIFT_HOST", "127.0.0.1")
    port = int(os.environ.get("AGRISHIFT_PORT", "8000"))
    frontend_port = int(os.environ.get("AGRISHIFT_FRONTEND_PORT", "3000"))
    node = shutil.which("node")
    next_bin = WEB_DIR / "node_modules" / "next" / "dist" / "bin" / "next"
    if not node or not next_bin.is_file():
        raise FileNotFoundError("Frontend dependencies are missing; run cd apps/web && npm ci")
    try:
        db.initialize()
    except Exception as exc:
        raise RuntimeError("SQLite initialization failed; check DATABASE_URL and database file access.") from exc
    api_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    frontend_url = f"http://127.0.0.1:{frontend_port}"
    api_url = f"http://{api_host}:{port}"
    os.environ.setdefault("AGRISHIFT_API_URL", api_url)
    os.environ.setdefault("NEXT_PUBLIC_AGRISHIFT_API_URL", f"http://{api_host}:{port}")
    frontend = subprocess.Popen(
        [node, str(next_bin), "dev", "--hostname", "127.0.0.1", "--port", str(frontend_port)],
        cwd=str(WEB_DIR), env=os.environ.copy(),
    )
    print(f"AgriShift farmer frontend: {frontend_url}", flush=True)
    print(f"AgriShift expert login: {frontend_url}/expert/login", flush=True)
    print(f"AgriShift API docs: {api_url}/docs", flush=True)
    if not (os.environ.get("EXPERT_EMAIL") and os.environ.get("EXPERT_PASSWORD_HASH")
            and len(os.environ.get("EXPERT_SESSION_SECRET", "")) >= 32):
        print("Expert login needs EXPERT_EMAIL, EXPERT_PASSWORD_HASH, and a 32+ character EXPERT_SESSION_SECRET.", flush=True)
    try:
        uvicorn.run("app.main:app", app_dir=str(API_DIR), host=host, port=port, reload=False)
    finally:
        if frontend.poll() is None:
            frontend.terminate()
            try:
                frontend.wait(timeout=10)
            except subprocess.TimeoutExpired:
                frontend.kill()


if __name__ == "__main__":
    main()
