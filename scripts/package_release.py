"""Create the shareable demo ZIP while rejecting raw data, secrets, and local state."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT.parent / "agrishift-ai-semester-project-final.zip"
BLOCKED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache",
                ".mypy_cache", ".next", "node_modules", ".playwright-mcp", ".tmp-zip-review",
                "secrets", "private", ".local"}
BLOCKED_SUFFIXES = {".tif", ".tiff", ".nc", ".nc4", ".h5", ".hdf", ".hdf5", ".grib",
                    ".jp2", ".shp", ".shx", ".dbf", ".gpkg", ".parquet", ".pkl", ".pt",
                    ".pth", ".onnx", ".sqlite", ".sqlite3", ".db", ".log", ".pem", ".key",
                    ".p12", ".pfx", ".crt", ".cer", ".token", ".secret", ".credentials"}
BLOCKED_NAMES = {"id_rsa", "id_ed25519", "credentials.json", "secrets.json", "service-account.json"}
RUNTIME_MODELS = {
    "ml/clustering/artifacts/scaler.joblib",
    "ml/clustering/artifacts/kmeans.joblib",
}
RUNTIME_DATA = {
    "data/features/features.json",
    "data/processed/regional/smap_summary.json",
    "data/processed/regional/gpm_summary.json",
    "data/processed/weather/meteomatics_hourly.csv",
    "data/processed/weather/meteomatics_daily.json",
}
PACKAGE_EXCLUDES = {
    "agrishift.ico",
    "README_FINAL_DEMO.md",
    "start_agrishift.bat",
    "scripts/create_desktop_shortcut.ps1",
    "scripts/launch_desktop.py",
}


def include(relative: Path) -> bool:
    parts = relative.parts
    name = relative.name
    normalized = relative.as_posix()
    if name.lower() in BLOCKED_NAMES:
        return False
    if path_contains_private_marker(name):
        return False
    if normalized in PACKAGE_EXCLUDES:
        return False
    if any(part in BLOCKED_DIRS for part in parts):
        return False
    if name.lower().endswith((".zip", ".zip.sha256", ".tar", ".tar.gz", ".tgz", ".7z", ".rar",
                              "-wal", "-shm", "-journal")):
        return False
    if name.lower() == ".env" or (name.lower().startswith(".env.") and name.lower() != ".env.example"):
        return False
    if Path(name).suffix.lower() in BLOCKED_SUFFIXES:
        return False
    if Path(name).suffix.lower() == ".joblib" and normalized not in RUNTIME_MODELS:
        return False
    if parts and parts[0] == "data":
        if normalized.startswith(("data/raw/", "data/interim/", "data/model-ready/")):
            return normalized.endswith("README.md")
        if normalized.startswith("data/processed/"):
            return normalized.endswith("README.md") or normalized in RUNTIME_DATA
        if normalized.startswith("data/api-samples/"):
            return normalized.endswith("README.md") or name.endswith(".example.json")
        if normalized.startswith("data/features/"):
            return name in {"README.md", "features.example.json", "features.json"}
        if normalized.startswith("data/layers/"):
            return name in {"README.md", "metadata.json", "ndvi.png", "ndmi.png", "bsi.png", "slope.png"}
        if normalized.startswith("data/manifests/"):
            return Path(name).suffix.lower() in {".csv", ".md"}
        return name == "README.md" and normalized == "data/README.md"
    return True


def collect_files() -> list[Path]:
    files: list[Path] = []
    for current, directories, names in os.walk(ROOT, topdown=True):
        current_path = Path(current)
        directories[:] = [name for name in directories
                          if name not in BLOCKED_DIRS and not (current_path / name).is_symlink()]
        for name in names:
            path = current_path / name
            if path.is_file() and not path.is_symlink() and include(path.relative_to(ROOT)):
                files.append(path)
    return sorted(files)


def path_contains_private_marker(name: str) -> bool:
    """Exclude common standalone credential and private-key filenames."""
    lowered = name.lower()
    return (lowered.startswith(("id_rsa", "id_ed25519", "private_key", "service_account"))
            or lowered.endswith((".env.local", ".credentials.json", ".secrets.json"))
            or any(marker in Path(lowered).stem for marker in ("credential", "secret", "token")))


def validate_package(files: list[Path]) -> None:
    required = {
        "README.md", "README_FINAL.md", ".env.example", "requirements.lock.txt",
        "apps/api/app/main.py", "apps/web/index.html", "scripts/start_demo.py",
        "data/features/features.json", "data/features/features.example.json",
        "data/layers/ndvi.png", "data/layers/ndmi.png", "data/layers/bsi.png",
        "data/layers/slope.png", "data/layers/metadata.json",
        "data/processed/regional/smap_summary.json", "data/processed/regional/gpm_summary.json",
        "data/processed/weather/meteomatics_hourly.csv", "data/processed/weather/meteomatics_daily.json",
        "ml/clustering/artifacts/scaler.joblib", "ml/clustering/artifacts/kmeans.joblib",
        "ml/clustering/artifacts/cluster_profile.json", "ml/clustering/artifacts/metrics.json",
        "ml/clustering/artifacts/training_manifest.json",
        "apps/api/app/expert_api.py", "apps/api/tests/test_expert_api.py",
        "apps/web/src/app/api/expert/[...path]/route.ts",
        "apps/web/src/app/expert/dashboard/page.tsx",
        "apps/web/src/app/expert/analysis/[id]/page.tsx",
        "scripts/hash_expert_password.py",
    }
    names = {path.relative_to(ROOT).as_posix() for path in files}
    missing = required - names
    if missing:
        raise FileNotFoundError(f"Required demo-package assets are missing: {sorted(missing)}")
    features = json.loads((ROOT / "data/features/features.json").read_text(encoding="utf-8"))
    if features.get("meta", {}).get("data_mode") != "real" or len(features.get("points", [])) != 149:
        raise ValueError("The release package requires the real 149-point feature document")
    manifest = json.loads((ROOT / "ml/clustering/artifacts/training_manifest.json").read_text(encoding="utf-8"))
    for record in manifest.get("artifacts", {}).values():
        artifact = ROOT / "ml/clustering/artifacts" / record["file"]
        if not artifact.is_file() or sha256(artifact) != record.get("sha256"):
            raise ValueError(f"K-Means artifact checksum failed during packaging: {artifact.name}")
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    for key in ("METEOMATICS_USERNAME", "METEOMATICS_PASSWORD", "EXPERT_EMAIL",
                "EXPERT_PASSWORD_HASH", "EXPERT_SESSION_SECRET"):
        for line in env_example.splitlines():
            if line.startswith(key + "=") and line.split("=", 1)[1].strip():
                raise ValueError(f"Credential placeholder must remain blank: {key}")
    names = {path.relative_to(ROOT).as_posix() for path in files}
    forbidden = [name for name in names if any(part in BLOCKED_DIRS for part in Path(name).parts)
                 or Path(name).suffix.lower() in BLOCKED_SUFFIXES
                 or Path(name).name.lower() == ".env"
                 or (Path(name).name.lower().startswith(".env.") and Path(name).name.lower() != ".env.example")
                 or Path(name).name.lower().endswith((".env.local", "-wal", "-shm", "-journal"))]
    if forbidden:
        raise ValueError(f"Release contents include blocked local or private files: {sorted(forbidden)}")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package(output: Path = DEFAULT_OUTPUT) -> dict:
    output = Path(output).resolve()
    sidecar = output.with_suffix(output.suffix + ".sha256")
    temporary = output.with_name(output.name + ".building")
    temporary_sidecar = sidecar.with_name(sidecar.name + ".building")
    if any(path.exists() for path in (output, sidecar, temporary, temporary_sidecar)):
        raise FileExistsError(f"Refusing to overwrite an existing package/checksum path: {output}")
    files = collect_files()
    validate_package(files)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with ZipFile(temporary, "x", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            for path in files:
                relative = path.relative_to(ROOT).as_posix()
                archive.write(path, f"agrishift-ai/{relative}")
        digest = sha256(temporary)
        temporary_sidecar.write_text(f"{digest}  {output.name}\n", encoding="ascii")
        temporary.replace(output)
        temporary_sidecar.replace(sidecar)
    except Exception:
        temporary.unlink(missing_ok=True)
        temporary_sidecar.unlink(missing_ok=True)
        raise
    return {"archive": str(output), "sha256": digest, "file_count": len(files),
            "size_bytes": output.stat().st_size, "checksum_file": str(sidecar)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    import json
    print(json.dumps(package(args.output), indent=2))
