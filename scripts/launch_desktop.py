"""AgriShift AI Desktop Launcher Helper.

Checks environment, initializes database, starts both the Next.js frontend and
FastAPI backend, and opens the default browser once both services respond.
"""
from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "apps" / "api"
WEB_DIR = ROOT / "apps" / "web"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

os.environ.setdefault("DEMO_MODE", "false")
os.environ.setdefault("AGRISHIFT_ROOT", str(ROOT))
if os.environ["DEMO_MODE"].lower() in ("1", "true", "yes") and not (
    os.environ.get("FEATURES_FILE") or os.environ.get("FEATURES_PATH")
):
    os.environ["FEATURES_FILE"] = str(ROOT / "data" / "features" / "features.example.json")
os.environ.setdefault("AGRISHIFT_HOST", "127.0.0.1")
os.environ.setdefault("AGRISHIFT_PORT", "8000")
os.environ.setdefault("AGRISHIFT_WEB_PORT", "3000")
os.environ.setdefault(
    "METEOMATICS_SAMPLE_FILE",
    str(ROOT / "data" / "processed" / "weather" / "meteomatics_daily.json"),
)

HOST = os.environ["AGRISHIFT_HOST"]
API_PORT = int(os.environ["AGRISHIFT_PORT"])
WEB_PORT = int(os.environ["AGRISHIFT_WEB_PORT"])
API_HOST = "127.0.0.1" if HOST in {"0.0.0.0", "::"} else HOST
API_URL = f"http://{API_HOST}:{API_PORT}/"
WEB_URL = f"http://127.0.0.1:{WEB_PORT}/"
HEALTH_URL = f"{API_URL}api/v1/health"


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Return True if a local TCP socket is accepting connections on host:port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.15)
        return s.connect_ex((host, port)) == 0


def is_http_ok(url: str, timeout: float = 1.5) -> bool:
    """Return True if url responds with HTTP 2xx."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AgriShiftLauncher/2.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 300
    except Exception:
        return False


def find_node_binary() -> str | None:
    """Locate the Node.js executable on PATH or standard Windows install paths."""
    found = shutil.which("node")
    if found:
        return found
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
        if base:
            candidate = Path(base) / "nodejs" / "node.exe"
            if candidate.is_file():
                return str(candidate)
    return None


def open_browser(url: str) -> None:
    """Open url once in the user's default browser."""
    try:
        if webbrowser.open(url):
            return
    except Exception:
        pass
    if sys.platform == "win32":
        try:
            os.startfile(url)  # type: ignore[attr-defined]
        except Exception:
            pass


def wait_and_open_browser(frontend: subprocess.Popen[bytes], timeout_s: float = 60.0) -> None:
    """Poll backend health and Next.js frontend until ready, then open the browser."""
    def _poll() -> None:
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            if frontend.poll() is not None:
                print("\n[ERROR] Frontend server exited unexpectedly during startup.")
                return
            if is_http_ok(HEALTH_URL) and is_http_ok(WEB_URL):
                print("\n======================================================================")
                print(" [SUCCESS] AgriShift AI is LIVE and READY!")
                print(f" [BROWSER] Opening {WEB_URL} in your default web browser...")
                print("======================================================================\n")
                open_browser(WEB_URL)
                return
            time.sleep(0.5)
        print(f"\n[NOTE] Startup is still finishing. Open {WEB_URL} in your browser.")

    threading.Thread(target=_poll, daemon=True).start()


def kill_process_on_port(port: int) -> None:
    """Terminate any existing listener holding the given TCP port on Windows."""
    if sys.platform != "win32":
        return
    try:
        cmd = f'cmd /c "netstat -ano | findstr :{port} | findstr LISTENING"'
        out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
        seen: set[int] = set()
        for line in out.splitlines():
            parts = line.strip().split()
            if len(parts) < 5:
                continue
            pid = int(parts[-1])
            if pid > 0 and pid != os.getpid() and pid not in seen:
                seen.add(pid)
                print(f"[*] Releasing port {port} from existing process (PID {pid})...")
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        time.sleep(0.5)
    except Exception:
        pass


def stop_process_tree(proc: subprocess.Popen[bytes]) -> None:
    """Cleanly terminate a subprocess and any Windows child workers."""
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            proc.kill()


def main() -> None:
    print("======================================================================")
    print("                     AGRISHIFT AI - DESKTOP LAUNCHER")
    print("        Real NASA Earth Observations & Agronomic Decision Support")
    print("======================================================================")
    print(f"\n  Project Directory : {ROOT}")
    print(f"  Web Application   : {WEB_URL}")
    print(f"  Interactive API   : {API_URL}docs")
    print(f"  System Health     : {HEALTH_URL}")
    print(f"  Data Mode         : {'DEMO' if os.environ.get('DEMO_MODE') == 'true' else 'REAL DATA'}")
    print("\n----------------------------------------------------------------------")

    if is_port_in_use(API_PORT) and is_port_in_use(WEB_PORT):
        if is_http_ok(HEALTH_URL) and is_http_ok(WEB_URL):
            print(f"[OK] AgriShift AI is already running on {WEB_URL}!")
            print("[OK] Opening web browser now...")
            open_browser(WEB_URL)
            return

    if is_port_in_use(API_PORT):
        kill_process_on_port(API_PORT)
    if is_port_in_use(WEB_PORT):
        kill_process_on_port(WEB_PORT)

    print("[1/4] Checking project files and runtime dependencies...")
    from app import db
    from app.config import get_settings
    settings = get_settings()

    if not settings.crops_csv.is_file() or not (WEB_DIR / "package.json").is_file():
        raise FileNotFoundError("The crop knowledge file or Next.js frontend is missing.")
    if not settings.features_path.is_file():
        raise FileNotFoundError(f"Selected feature file is missing: {settings.features_path}")

    node = find_node_binary()
    next_bin = WEB_DIR / "node_modules" / "next" / "dist" / "bin" / "next"
    if not node or not next_bin.is_file():
        raise FileNotFoundError("Install frontend dependencies first: cd apps/web && npm install")

    db.initialize()
    print("[2/4] Starting Next.js web application (http://127.0.0.1:3000)...")
    env = os.environ.copy()
    env.setdefault("NEXT_PUBLIC_AGRISHIFT_API_URL", f"http://{API_HOST}:{API_PORT}")
    frontend = subprocess.Popen(
        [node, str(next_bin), "dev", "--hostname", "127.0.0.1", "--port", str(WEB_PORT)],
        cwd=str(WEB_DIR),
        env=env,
    )

    print("[3/4] Loading satellite indices and AI models (please wait ~5-8s)...")
    print(f"[4/4] Launching API server at {API_URL} (browser opens automatically)...\n")
    wait_and_open_browser(frontend)

    import uvicorn
    try:
        uvicorn.run("app.main:app", app_dir=str(API_DIR), host=HOST, port=API_PORT, reload=False)
    except KeyboardInterrupt:
        print("\n\n>>> AgriShift AI server stopped successfully.")
        sys.exit(0)
    finally:
        stop_process_tree(frontend)


if __name__ == "__main__":
    main()
