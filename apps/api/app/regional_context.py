"""Read only the validated, coarse context summaries; never satisfy field core data."""
from __future__ import annotations

import json
from pathlib import Path

from .config import get_settings


def get_regional_context(path: Path | None = None) -> dict:
    path = Path(path) if path else get_settings().root / "data" / "processed" / "model-features" / "regional_context.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"available": False, "status": "unavailable", "regional_context": {},
                "limitations": ["No validated regional context summary is available."]}
    if payload.get("validation_status") != "validated_context_only":
        return {"available": False, "status": "unavailable", "regional_context": {},
                "limitations": ["Regional context metadata has not passed validation."]}
    sources = payload.get("sources", {})
    smap = sources.get("smap", {})
    surface = smap.get("surface_soil_moisture", {})
    rootzone = smap.get("rootzone_soil_moisture", {})
    gpm = sources.get("gpm_imerg", {})
    return {
        "available": True, "status": "context_only",
        "regional_context": {
            "soil_moisture": {
                "surface_mean": surface.get("mean"), "rootzone_mean": rootzone.get("mean"),
                "unit": "m^3/m^3", "resolution_degrees": (surface.get("metadata") or {}).get("resolution_degrees"),
                "observation_start_utc": surface.get("observation_start_utc"),
                "observation_end_utc": surface.get("observation_end_utc"),
                "source": "NASA SMAP SPL4SMGP V008", "note": "Regional context; not an exact field measurement.",
            },
            "rainfall": {
                "mean_daily_mm_per_day": gpm.get("mean_daily_mm_per_day"),
                "unit": "mm/day", "observation_start_utc": (gpm.get("metadata") or {}).get("start_time"),
                "observation_end_utc": (gpm.get("metadata") or {}).get("end_time"),
                "source": "NASA GPM IMERG Final Run V07",
                "note": gpm.get("limitation"),
            },
        },
        "temporal_alignment": payload.get("temporal_alignment"),
        "limitations": payload.get("limitations", []),
    }
