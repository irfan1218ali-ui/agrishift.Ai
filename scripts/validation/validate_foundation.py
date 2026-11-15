"""Validate architecture foundation files without opening or processing raster data."""
from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
errors: list[str] = []

for path in ROOT.rglob("*.csv"):
    if ".git" in path.parts:
        continue
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = csv.reader(stream)
            header = next(rows)
            if not header or any(not column.strip() for column in header):
                errors.append(f"{path.relative_to(ROOT)}: missing/blank CSV header")
            if len(header) != len(set(header)):
                errors.append(f"{path.relative_to(ROOT)}: duplicate CSV header")
            for line, row in enumerate(rows, start=2):
                if row and len(row) != len(header):
                    errors.append(f"{path.relative_to(ROOT)}:{line}: {len(row)} values for {len(header)} columns")
    except (OSError, UnicodeError, csv.Error, StopIteration) as exc:
        errors.append(f"{path.relative_to(ROOT)}: CSV error: {exc}")

for path in ROOT.rglob("*.json"):
    if ".git" in path.parts:
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: JSON error: {exc}")

link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
for path in ROOT.rglob("*.md"):
    if ".git" in path.parts:
        continue
    for target in link_pattern.findall(path.read_text(encoding="utf-8")):
        target = target.strip().split()[0].strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        relative = target.split("#", 1)[0]
        if relative and not (path.parent / relative).exists():
            errors.append(f"{path.relative_to(ROOT)}: broken local link {target}")

ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
for required in ("/data/raw/**", ".env", "*.tif", "*.tiff", "*.nc", "*.h5", "*.zip", "*.tar", "node_modules/", "*.pt", "*.ckpt", "postgres-data/", ".local/"):
    if required not in ignore_text:
        errors.append(f".gitignore: missing rule {required}")

secret_assignment = re.compile(r"(?im)^[ \t]*[A-Z0-9_]*(?:PASSWORD|SECRET|TOKEN|API_KEY|CONNECTION_STRING|DSN)[A-Z0-9_]*[ \t]*=[ \t]*(\S+)")
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or "data" in path.parts and "raw" in path.parts or path.name == "validate_foundation.py":
        continue
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeError, OSError):
        continue
    if secret_assignment.search(content):
        errors.append(f"{path.relative_to(ROOT)}: non-empty secret-like assignment")

for name in ("crops.csv", "crop-calendar.csv", "crop-compatibility.csv", "water-requirements.csv", "soil-requirements.csv", "pest-families.csv"):
    path = ROOT / "data" / "crop-knowledge" / name
    if path.exists() and sum(1 for _ in path.open(encoding="utf-8")) != 1:
        errors.append(f"{path.relative_to(ROOT)}: crop values require evidence and expert review before entry")

for candidate in ("data/raw/smap/validation-sentinel.tif", "data/interim/validation-sentinel.nc", "data/processed/validation-sentinel.tif", "data/model-ready/validation-sentinel.parquet", "archive.zip", "archive.tar", "checkpoint.ckpt", "model.onnx", "postgres-data/pgdata", ".local/object-storage/asset", ".env"):
    result = subprocess.run(["git", "check-ignore", "--quiet", candidate], cwd=ROOT, check=False)
    if result.returncode != 0:
        errors.append(f".gitignore: expected {candidate} to be ignored")

for candidate in ("data/raw/README.md", "data/raw/smap/README.md", "data/processed/climate/README.md"):
    result = subprocess.run(["git", "check-ignore", "--quiet", candidate], cwd=ROOT, check=False)
    if result.returncode == 0:
        errors.append(f".gitignore: expected documentation {candidate} to remain addable")

if errors:
    print("Foundation validation failed:")
    print("\n".join(f"- {item}" for item in errors))
    raise SystemExit(1)

print("Foundation validation passed: CSV headers, JSON syntax, Markdown local links, secret placeholders, crop templates, and Git ignore rules.")
