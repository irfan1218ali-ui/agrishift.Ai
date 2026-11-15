"""Read context-only SMAP and GPM summaries produced by Step 2A."""
from __future__ import annotations

import json
from pathlib import Path

from .config import get_settings


def _read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def get_regional_context(root: Path | None = None) -> dict:
    root = Path(root) if root else get_settings().root
    base = root / "data" / "processed" / "regional"
    smap = _read_json(base / "smap_summary.json")
    gpm = _read_json(base / "gpm_summary.json")
    if not smap or not gpm:
        return {"available": False, "status": "unavailable", "regional_context": {},
                "temporal_alignment": "unavailable",
                "limitations": ["Validated regional context summaries are unavailable."]}
    return {
        "available": True,
        "status": "context_only",
        "regional_context": {
            "soil_moisture": {
                "surface_mean": smap.get("smap_surface_mean"),
                "rootzone_mean": smap.get("smap_rootzone_mean"),
                "unit": smap.get("units", "m^3/m^3"),
                "observation_start_utc": smap.get("smap_observation_start"),
                "observation_end_utc": smap.get("smap_observation_end"),
                "source": "NASA SMAP SPL4SMGP V008",
                "note": smap.get("smap_limitation", "Regional context; not a field measurement."),
            },
            "rainfall": {
                "mean_daily_mm_per_day": gpm.get("mean_daily_rate_mm_day"),
                "minimum_cell_mean_daily_mm_per_day": gpm.get("minimum_cell_mean_daily_rate_mm_day"),
                "maximum_cell_mean_daily_mm_per_day": gpm.get("maximum_cell_mean_daily_rate_mm_day"),
                "unit": "mm/day",
                "observation_start_utc": gpm.get("gpm_observation_start"),
                "observation_end_utc": gpm.get("gpm_observation_end"),
                "source": "NASA GPM IMERG Final Run V07",
                "note": gpm.get("gpm_limitation"),
            },
        },
        "temporal_alignment": "not_aligned",
        "limitations": [
            smap.get("smap_limitation", "SMAP is coarse regional context."),
            gpm.get("gpm_limitation", "GPM is an aggregate regional rate, not a daily series."),
        ],
    }
