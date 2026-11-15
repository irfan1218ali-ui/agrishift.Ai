"""AgriShift AI Desktop Launcher Helper.

Checks environment, initializes database, launches server, and automatically
opens the user's default browser once the health endpoint responds.
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

# Paths setup
ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

os.environ.setdefault("DEMO_MODE", "false")
os.environ.setdefault("AGRISHIFT_ROOT", str(ROOT))
os.environ.setdefault("AGRISHIFT_HOST", "127.0.0.1")
os.environ.setdefault("AGRISHIFT_PORT", "8000")
os.environ.setdefault(
    "METEOMATICS_SAMPLE_FILE",
    str(ROOT / "data" / "processed" / "weather" / "meteomatics_daily.json"),
)

PORT = int(os.environ["AGRISHIFT_PORT"])
HOST = os.environ["AGRISHIFT_HOST"]
URL = f"http://{HOST}:{PORT}/"


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Fast socket check for port availability (sub-millisecond)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.15)
        return s.connect_ex((host, port)) == 0


def is_server_healthy() -> bool:
    """Checks if AgriShift AI server is already responding on /api/v1/health."""
    try:
        health_url = f"http://{HOST}:{PORT}/api/v1/health"
        req = urllib.request.Request(health_url, headers={"User-Agent": "AgriShiftLauncher/1.0"})
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False


def open_browser(url: str):
    """Opens the URL in the system's default browser on Windows."""
    try:
        webbrowser.open(url)
    except Exception:
        pass
    if sys.platform == "win32":
        try:
            os.system(f'start "" "{url}"')
        except Exception:
            pass


def open_browser_when_ready():
    """Polls the local health endpoint in background and launches default browser upon ready."""
    def _poll():
        health_url = f"http://{HOST}:{PORT}/api/v1/health"
        for _ in range(60):  # Poll every 0.5s for up to 30 seconds
            time.sleep(0.5)
            try:
                req = urllib.request.Request(health_url, headers={"User-Agent": "AgriShiftLauncher/1.0"})
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    if resp.status == 200:
                        print(f"\n======================================================================")
                        print(f" [SUCCESS] AgriShift AI is LIVE and READY!")
                        print(f" [BROWSER] Opening {URL} in your default web browser...")
                        print(f"======================================================================\n")
                        open_browser(URL)
                        return
            except Exception:
                pass
        print(f"\n[NOTE] Server is starting up. Please open {URL} in your browser.")

    thread = threading.Thread(target=_poll, daemon=True)
    thread.start()


def kill_dead_process_on_port(port: int):
    """Frees the port if a non-responsive process is holding it on Windows."""
    if sys.platform != "win32":
        return
    try:
        # Use fast cmd netstat lookup
        cmd = f'cmd /c "netstat -ano | findstr :{port} | findstr LISTENING"'
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) >= 5:
                pid = int(parts[-1])
                if pid > 0 and pid != os.getpid():
                    print(f"[*] Releasing port {port} from old background process (PID {pid})...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
    except Exception:
        pass


def main():
    print("======================================================================")
    print("                     AGRISHIFT AI - DESKTOP LAUNCHER")
    print("        Real NASA Earth Observations & Agronomic Decision Support")
    print("======================================================================")
    print(f"\n  Project Directory : {ROOT}")
    print(f"  Web Application   : {URL}")
    print(f"  Interactive API   : {URL}docs")
    print(f"  System Health     : {URL}api/v1/health")
    print(f"  Data Mode         : {'DEMO' if os.environ.get('DEMO_MODE') == 'true' else 'REAL DATA'}")
    print("\n----------------------------------------------------------------------")

    # 1. Check if server is ALREADY healthy and running
    if is_port_in_use(PORT):
        if is_server_healthy():
            print(f"[OK] AgriShift AI is already running on {URL}!")
            print("[OK] Opening web browser now...")
            open_browser(URL)
            print("\nKeep this window open while using AgriShift AI.")
            print("Press Ctrl+C to stop.\n")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nLauncher closed.")
                sys.exit(0)
        else:
            # Port is occupied by a dead/unresponsive process -> free it
            kill_dead_process_on_port(PORT)

    print("[1/3] Initializing local database and configuration...")
    from app import db
    from app.config import get_settings
    settings = get_settings()

    if not settings.crops_csv.is_file() or not (settings.web_dir / "index.html").is_file():
        raise FileNotFoundError("The crop knowledge file or frontend entry page is missing.")
    if not settings.features_path.is_file():
        raise FileNotFoundError(f"Selected feature file is missing: {settings.features_path}")

    db.initialize()
    print("[2/3] Loading satellite indices and AI models (please wait ~5-8s)...")

    print(f"[3/3] Launching web application server at {URL}...")
    print("      (Browser will open automatically once loaded)\n")

    # Start background watcher to launch browser
    open_browser_when_ready()

    # Launch uvicorn server
    import uvicorn
    try:
        uvicorn.run("app.main:app", app_dir=str(API_DIR), host=HOST, port=PORT, reload=False)
    except KeyboardInterrupt:
        print("\n\n>>> AgriShift AI server stopped successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
