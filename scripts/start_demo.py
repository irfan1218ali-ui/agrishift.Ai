"""Start the local AgriShift farmer MVP on loopback using real pilot data."""
from __future__ import annotations

import os
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


def main() -> None:
    settings = get_settings()
    if not settings.crops_csv.is_file() or not (WEB_DIR / "package.json").is_file():
        raise FileNotFoundError("The crop knowledge file or Next.js frontend is missing")
    if not settings.features_path.is_file():
        raise FileNotFoundError(f"Selected feature file is missing: {settings.features_path}")
    db.initialize()
    import uvicorn

    host = os.environ.get("AGRISHIFT_HOST", "127.0.0.1")
    port = int(os.environ.get("AGRISHIFT_PORT", "8000"))
    node = shutil.which("node")
    next_bin = WEB_DIR / "node_modules" / "next" / "dist" / "bin" / "next"
    if not node or not next_bin.is_file():
        raise FileNotFoundError("Install the frontend dependencies first: cd apps/web && npm install")
    api_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    os.environ.setdefault("NEXT_PUBLIC_AGRISHIFT_API_URL", f"http://{api_host}:{port}")
    frontend = subprocess.Popen(
        [node, str(next_bin), "dev", "--hostname", "127.0.0.1", "--port", "3000"],
        cwd=str(WEB_DIR), env=os.environ.copy(),
    )
    print("AgriShift farmer frontend: http://127.0.0.1:3000", flush=True)
    print(f"AgriShift API: http://{api_host}:{port}/api/v1/health", flush=True)
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
