"""Check active MVP scope and catalog consistency without opening scientific files."""
from __future__ import annotations

import csv
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_IDS = {
    "nasa-smap-spl4smgp-v008-hyderabad",
    "nasa-gpm-3imergdf-v07-hyderabad",
    "usgs-landsat-c2-l2-lc08-151043-20250922",
    "nasa-srtm-hyderabad",
    "nasa-power-climate",
    "meteomatics-weather",
}
EXPECTED_ADAPTERS = {"smap", "gpm_imerg", "landsat", "terrain", "nasa_power", "meteomatics"}
ALLOWED_STATUSES = {
    "NOT_STARTED", "DOWNLOADED", "REGISTERED", "VALIDATION_PENDING", "VALIDATED",
    "PROCESSING_READY", "API_ACCESS_PENDING", "API_ACCESS_CONFIRMED", "BLOCKED",
    "VALIDATED_CONTEXT_ONLY", "ASSETS_MISSING", "VALIDATED_SLOPE_DERIVED",
    "SAVED_CSV_VALIDATED", "SAVED_SAMPLE_VALIDATED_NOT_LIVE",
}
errors: list[str] = []

def rows(name: str) -> list[dict[str, str]]:
    with (ROOT / name).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        result = list(reader)
        for line, row in enumerate(result, start=2):
            if None in row:
                errors.append(f"{name}:{line}: row has more values than header")
            if any(value is None for value in row.values()):
                errors.append(f"{name}:{line}: row has fewer values than header")
        return result

datasets = rows("data/catalog/datasets.csv")
if {r["dataset_id"] for r in datasets} != EXPECTED_IDS:
    errors.append("dataset catalog must contain exactly the six active source IDs")
statuses = rows("data/catalog/data-status.csv")
if {r["dataset_id"] for r in statuses} != EXPECTED_IDS:
    errors.append("data-status catalog must contain exactly the six active source IDs")
for row in statuses:
    if row["status"] not in ALLOWED_STATUSES:
        errors.append(f"invalid status for {row['dataset_id']}: {row['status']}")
api_rows = rows("data/catalog/api-endpoints.csv")
if {r["provider"] for r in api_rows} != {"NASA POWER", "Meteomatics"}:
    errors.append("API endpoint catalog must contain only NASA POWER and Meteomatics")

adapter_dir = ROOT / "apps/api/app/integrations"
adapters = {p.name for p in adapter_dir.iterdir() if p.is_dir() and p.name != "__pycache__"}
if adapters != EXPECTED_ADAPTERS:
    errors.append(f"active adapter packages differ from six-source set: {sorted(adapters)}")

required_paths = [
    "apps/web/src/app", "apps/web/src/components", "apps/web/src/features",
    "apps/web/src/hooks", "apps/web/src/lib", "apps/web/src/services", "apps/web/src/stores",
    "apps/web/src/types", "apps/web/public", "apps/web/tests",
    "apps/api/app/api/v1", "apps/api/app/core", "apps/api/app/db", "apps/api/app/models",
    "apps/api/app/schemas", "apps/api/app/repositories", "apps/api/app/services",
    "apps/api/app/workers", "apps/api/app/middleware", "apps/api/migrations", "apps/api/tests",
    "database/models", "database/migrations", "database/seeds", "database/schemas",
    "database/views", "database/diagrams", "database/data-dictionary",
    "packages/shared-types", "packages/shared-config", "packages/ui", "packages/map-components",
    "packages/crop-knowledge",
    "data/catalog/datasets.csv", "data/catalog/variables.csv", "data/catalog/api-endpoints.csv",
    "data/catalog/licenses.csv", "data/catalog/data-status.csv",
    "data/boundaries/pakistan", "data/boundaries/sindh", "data/boundaries/demo-fields",
    "data/raw/smap", "data/raw/gpm-imerg", "data/raw/landsat", "data/raw/terrain",
    "data/api-samples/nasa-power", "data/api-samples/meteomatics", "data/interim",
    "data/processed", "data/model-ready", "data/labels", "data/crop-knowledge", "data/manifests",
    "geospatial/validation", "geospatial/preprocessing/raster_io", "geospatial/preprocessing/clipping",
    "geospatial/preprocessing/reprojection", "geospatial/preprocessing/quality_masks",
    "geospatial/preprocessing/nodata", "geospatial/harmonization", "geospatial/soil-moisture",
    "geospatial/rainfall", "geospatial/landsat", "geospatial/terrain", "geospatial/indices",
    "geospatial/zonal-statistics", "geospatial/tiling", "geospatial/tests",
    "ml/common", "ml/datasets", "ml/features", "ml/segmentation", "ml/crop-suitability",
    "ml/seasonal-risk", "ml/rotation-ranking", "ml/explainability", "ml/registry", "ml/tests",
    "services/model-inference", "services/rotation-engine", "services/report-service", "services/notification-service",
    "infrastructure/docker", "infrastructure/github-actions", "infrastructure/azure",
    "infrastructure/storage", "infrastructure/monitoring", "infrastructure/backup",
    "tests/contract", "tests/integration", "tests/end-to-end", "docs/future-enhancements",
    "docs/architecture/system-overview.md", "docs/architecture/six-source-strategy.md",
    "docs/data/data-management.md", "docs/geospatial/resolution-policy.md",
    "docs/ml/model-architecture.md", "docs/development/team-boundaries.md",
    "docs/development/folder-ownership.md", "docs/adr/0016-six-source-mvp.md",
    "docs/data/smap.md", "docs/data/gpm-imerg.md", "docs/data/landsat.md",
    "docs/data/terrain.md", "docs/data/nasa-power.md", "docs/data/meteomatics.md",
    "docs/development/folder-ownership.md", "data/manifests/smap-files.csv",
    "data/manifests/gpm-imerg-files.csv", "data/manifests/landsat-files.csv",
    "data/manifests/terrain-files.csv",
]
for required_path in required_paths:
    if not (ROOT / required_path).exists():
        errors.append(f"required six-source architecture path is missing: {required_path}")

ignored_dirs = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".ruff_cache",
                ".mypy_cache", ".tmp-zip-review", "node_modules", ".next"}
for directory in (p for p in ROOT.rglob("*") if p.is_dir() and not ignored_dirs.intersection(p.parts)):
    readme = directory / "README.md"
    if not readme.exists():
        errors.append(f"folder has no purpose/ownership README: {directory.relative_to(ROOT)}")
        continue
    contents = readme.read_text(encoding="utf-8")
    for label in ("Owner:", "Inputs:", "Outputs:", "Must not store:"):
        if label not in contents:
            errors.append(f"{directory.relative_to(ROOT)}/README.md missing {label}")

env = (ROOT / ".env.example").read_text(encoding="utf-8").upper()
for inactive_config in ("NASA_EARTHDATA_", "APPEEARS_", "COPERNICUS_", "CDS_API_", "MPC_"):
    if inactive_config in env:
        errors.append(f"inactive provider configuration remains in .env.example: {inactive_config}")

for candidate in (
    "data/raw/gpm-imerg/GIOVANNI-g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.tif",
    "data/raw/gpm-imerg/g4.timeAvgMap.GPM_3IMERGDF_07_precipitation.20250901-20250907.68E_25N_68E_25N.nc",
):
    if (ROOT / candidate).exists():
        result = subprocess.run(["git", "check-ignore", "--quiet", candidate], cwd=ROOT, check=False)
        if result.returncode != 0:
            errors.append(f"existing raw GPM asset is not Git-ignored: {candidate}")

if errors:
    print("Six-source validation failed:\n" + "\n".join(f"- {e}" for e in errors))
    raise SystemExit(1)
print("Six-source validation passed: six catalog entries, six statuses, two API providers, adapter scope, and raw GPM ignore rules.")
