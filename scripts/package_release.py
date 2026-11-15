"""Create the shareable demo ZIP while rejecting raw data, secrets, and local state."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT.parent / "agrishift-ai-hackathon-final.zip"
BLOCKED_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache",
                ".mypy_cache", ".next", "node_modules", ".tmp-zip-review"}
BLOCKED_SUFFIXES = {".tif", ".tiff", ".nc", ".nc4", ".h5", ".hdf", ".hdf5", ".grib",
                    ".jp2", ".shp", ".shx", ".dbf", ".gpkg", ".parquet", ".joblib",
                    ".pkl", ".pt", ".pth", ".onnx", ".sqlite", ".sqlite3", ".db", ".log"}


def include(relative: Path) -> bool:
    parts = relative.parts
    name = relative.name
    if any(part in BLOCKED_DIRS for part in parts):
        return False
    if name == ".env" or (name.startswith(".env.") and name != ".env.example"):
        return False
    if Path(name).suffix.lower() in BLOCKED_SUFFIXES:
        return False
    if parts and parts[0] == "data":
        normalized = relative.as_posix()
        if normalized.startswith(("data/raw/", "data/interim/", "data/model-ready/")):
            return normalized.endswith("README.md")
        if normalized.startswith("data/processed/"):
            return normalized.endswith("README.md") or normalized == "data/processed/model-features/regional_context.json"
        if normalized.startswith("data/api-samples/"):
            return normalized.endswith("README.md") or name.endswith(".example.json")
        if normalized.startswith("data/features/"):
            return name in {"README.md", "features.example.json"}
        if normalized.startswith("data/layers/"):
            return name in {"README.md", "metadata.json", "slope.png"}
        if normalized.startswith("data/manifests/"):
            return Path(name).suffix.lower() in {".csv", ".md"}
        return name == "README.md" and normalized == "data/README.md"
    return True


def collect_files() -> list[Path]:
    return sorted(path for path in ROOT.rglob("*") if path.is_file() and include(path.relative_to(ROOT)))


def validate_package(files: list[Path]) -> None:
    required = {
        "README.md", "README_FINAL_DEMO.md", ".env.example", "requirements.lock.txt",
        "apps/api/app/main.py", "apps/web/index.html", "data/features/features.example.json",
        "data/layers/slope.png", "data/layers/metadata.json",
        "data/processed/model-features/regional_context.json",
        "data/api-samples/meteomatics/demo_sample.example.json", "scripts/start_demo.py",
    }
    names = {path.relative_to(ROOT).as_posix() for path in files}
    missing = required - names
    if missing:
        raise FileNotFoundError(f"Required demo-package assets are missing: {sorted(missing)}")
    sample = json.loads((ROOT / "data/api-samples/meteomatics/demo_sample.example.json").read_text(encoding="utf-8"))
    if "user" in sample:
        raise ValueError("The packaged Meteomatics sample still contains an account identifier")
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    for key in ("METEOMATICS_USERNAME", "METEOMATICS_PASSWORD"):
        for line in env_example.splitlines():
            if line.startswith(key + "=") and line.split("=", 1)[1].strip():
                raise ValueError(f"Credential placeholder must remain blank: {key}")


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
