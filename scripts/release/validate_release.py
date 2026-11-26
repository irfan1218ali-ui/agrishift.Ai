"""Validate the tagged AgriShift semester release and required runtime assets."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE_COMMIT = "122da198b9353e71e3738146f1cc6947597c4b9a"
BRANCH = "phase/03-final-release"
TAG = "v2.0.0-semester-project"
REQUIRED = (
    "README_FINAL.md", "apps/api/app/main.py", "apps/api/app/db.py",
    "apps/web/package.json", "services/rotation-engine/rotation_engine/engine.py",
    "knowledge/crops.csv", "data/features/features.json", "data/layers/metadata.json",
    "data/layers/ndvi.png", "data/layers/ndmi.png", "data/layers/bsi.png",
    "data/layers/slope.png", "data/processed/weather/meteomatics_daily.json",
    "ml/clustering/artifacts/scaler.joblib", "ml/clustering/artifacts/kmeans.joblib",
    "ml/clustering/artifacts/cluster_profile.json", "ml/clustering/artifacts/metrics.json",
    "ml/clustering/artifacts/training_manifest.json", "scripts/start_demo.py",
    "tests", "docs",
)
IGNORE_RULES = (
    ".env", ".env.*", "!.env.example", ".venv/", "node_modules/", ".next/",
    "__pycache__/", ".pytest_cache/", "*.log", "*.db-journal", "*.db-wal",
    "*.db-shm", "/data/raw/**", "/data/interim/**", "*.zip", "*.tar", "*.gz", "backups/",
)


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            errors.append(f"required path missing: {relative}")

    if git("cat-file", "-t", RELEASE_COMMIT) != "commit":
        errors.append("expected release commit is missing")
    branch_exists = subprocess.run(["git", "show-ref", "--verify", "--quiet", f"refs/heads/{BRANCH}"], cwd=ROOT).returncode == 0
    if not branch_exists:
        errors.append(f"release branch is missing: {BRANCH}")
    tag_target = git("rev-parse", f"{TAG}^{{}}")
    if tag_target != RELEASE_COMMIT:
        errors.append(f"release tag does not point to expected commit: {TAG}")
    if branch_exists:
        ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", RELEASE_COMMIT, f"refs/heads/{BRANCH}"], cwd=ROOT)
        if ancestor.returncode != 0:
            errors.append("release branch does not contain the tagged release commit")

    features_path = ROOT / "data/features/features.json"
    if features_path.is_file():
        try:
            features = json.loads(features_path.read_text(encoding="utf-8"))
            if features.get("meta", {}).get("data_mode") != "real" or len(features.get("points", [])) != 149:
                errors.append("real feature set is not the validated 149-point document")
        except (OSError, ValueError, AttributeError):
            errors.append("feature document is unreadable or invalid JSON")

    artifact_dir = ROOT / "ml/clustering/artifacts"
    manifest_path = artifact_dir / "training_manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for record in manifest.get("artifacts", {}).values():
                artifact = artifact_dir / record["file"]
                if not artifact.is_file() or sha256(artifact) != record.get("sha256"):
                    errors.append(f"K-Means artifact checksum mismatch: {record.get('file', 'unknown')}")
        except (OSError, ValueError, KeyError, TypeError):
            errors.append("K-Means artifact manifest is invalid")

    ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    missing_rules = [rule for rule in IGNORE_RULES if rule not in ignore_text.splitlines()]
    if missing_rules:
        errors.append(f".gitignore lacks required exclusions: {', '.join(missing_rules)}")

    tracked = git("ls-files", "-z").split("\0")
    for name in (item for item in tracked if item):
        path = Path(name)
        lowered = name.lower()
        if path.name.lower() == ".env" or (path.name.lower().startswith(".env.") and path.name != ".env.example"):
            errors.append(f"environment file is tracked: {name}")
        if any(part.lower() in {".venv", "venv", "node_modules", ".next", "__pycache__", ".pytest_cache", "backups"}
               for part in path.parts):
            errors.append(f"local cache, dependency, or backup path is tracked: {name}")
        if lowered.endswith((".db", ".sqlite", ".sqlite3", ".zip", ".log", ".db-wal", ".db-shm", ".db-journal")):
            errors.append(f"local state or archive is tracked: {name}")

    if errors:
        print(f"FAIL: {len(errors)} release validation issue(s).")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: {TAG} points to {RELEASE_COMMIT}; required runtime files, feature count, artifact hashes, and ignore rules verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
