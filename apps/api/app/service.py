"""Glue between HTTP, data readers and the rotation engine. No web framework imports here (easy to test)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Optional

from .config import Settings, get_settings
from .features import FeatureStore
from . import power as power_mod
from . import weather as weather_mod
from . import regional_context as regional_context_mod
from .schemas import AnalyzeRequest

from rotation_engine import load_crops, recommend  # noqa: E402  (path set in config.py)

SPECIAL = {"sugarcane": "special_long", "banana": "special_perm"}   # recognised, never recommended
CORE_SOURCES = ("landsat", "srtm", "power")                         # scoring needs these three
DISCLAIMER_ID = "disclaimer_001"


@dataclass
class Deps:
    settings: Settings
    crops: dict
    store: FeatureStore
    weather_fn: Callable[[float, float], dict]
    power_fn: Callable[[float, float], Optional[dict]]
    regional_context_fn: Callable[[], dict]


def build_deps(settings: Optional[Settings] = None) -> Deps:
    s = settings or get_settings()
    crops = load_crops(str(s.crops_csv))          # fails loudly at start-up if the table is broken
    store = FeatureStore(s.features_path, max_km=s.features_max_km, min_cloud_free=s.min_cloud_free)

    def weather_fn(lat: float, lon: float) -> dict:
        return weather_mod.get_weather(lat, lon, user=s.meteomatics_user, password=s.meteomatics_password,
                                       samples_dir=s.samples_dir, demo_mode=s.demo_mode,
                                       sample_file=s.meteomatics_sample_path)

    def power_fn(lat: float, lon: float) -> Optional[dict]:
        if s.power_csv_path and s.power_csv_path.is_file():
            return power_mod.summarize_csv(s.power_csv_path)
        if s.power_live_enabled:
            return power_mod.get_monthly_features(lat, lon, s.cache_dir, s.samples_dir)
        return None

    def regional_context_fn() -> dict:
        return regional_context_mod.get_regional_context(
            s.root / "data" / "processed" / "model-features" / "regional_context.json")

    return Deps(settings=s, crops=crops, store=store, weather_fn=weather_fn,
                 power_fn=power_fn, regional_context_fn=regional_context_fn)


def _insufficient(reason_id: str, demo_mode: bool = False) -> dict:
    return {"status": "insufficient_data", "reason_id": reason_id,
            "data_mode": "DEMO" if demo_mode else "REAL",
            "limitations": ["Validated Landsat, terrain, and climate features are required for a field recommendation."]}


def _in_pilot_area(s: Settings, lat: float, lon: float) -> bool:
    return s.min_lat <= lat <= s.max_lat and s.min_lon <= lon <= s.max_lon


def analyze(req: AnalyzeRequest, deps: Deps, today: Optional[date] = None) -> dict:
    """Raises ValueError for an unknown crop id (HTTP 422). Everything else returns a response dict."""
    s = deps.settings
    known = set(deps.crops) | set(SPECIAL)
    if req.current_crop not in known:
        raise ValueError(f"unknown current_crop '{req.current_crop}'")
    if req.previous_crop not in (None, "", "unknown") and req.previous_crop not in known:
        raise ValueError(f"unknown previous_crop '{req.previous_crop}'")

    # 1) permanent / long crops: recognised, not a rotation case
    if req.current_crop in SPECIAL:
        return {"status": "not_applicable", "reason_id": SPECIAL[req.current_crop]}

    # 2) pilot area only
    if not _in_pilot_area(s, req.lat, req.lon):
        return {"status": "not_applicable", "reason_id": "out_of_area",
                "data_mode": "DEMO" if s.demo_mode else "REAL",
                "limitations": ["This location is outside the Hyderabad pilot area."]}

    # 3) pre-processed features (nearest point) - never guessed
    try:
        feats = deps.store.get(req.lat, req.lon, power_fallback=lambda: deps.power_fn(req.lat, req.lon))
    except Exception:
        feats = None
    if feats is None or not all(src in feats["sources"] for src in CORE_SOURCES):
        return _insufficient("no_data_001", s.demo_mode)

    # 4) forecast is context only (counts as the 6th data source for confidence)
    try:
        forecast = deps.weather_fn(req.lat, req.lon)
    except Exception:
        forecast = {"available": False, "source": "meteomatics", "is_sample": False}
    forecast_ok = bool(forecast.get("available"))
    sources_present = feats["sources_present"] + (1 if forecast_ok else 0)

    engine_features = {
        "ndvi_mean": feats["ndvi_mean"],
        "low_lying_flag": feats["low_lying_flag"],
        "heat_days_40c_by_month": feats["heat_days_40c_by_month"],
        "sources_present": sources_present,
    }
    engine_request = {
        "current_crop": req.current_crop, "water_source": req.water_source, "water_amount": req.water_amount,
        "salinity": req.salinity, "waterlogging": req.waterlogging, "priority": req.priority,
    }
    try:
        result = recommend(deps.crops, engine_request, engine_features, today or date.today())
    except ValueError:
        return _insufficient("no_data_001", s.demo_mode)

    if result["status"] != "ok":
        return {"status": "insufficient_data", "reason_id": result["reason_id"],
                "field_health": result.get("field_health"),
                "data_mode": "DEMO" if s.demo_mode else "REAL",
                "limitations": ["Three distinct, rule-valid rotation strategies could not be generated."]}

    meta = deps.store.meta()
    confidence = []
    validated = meta.get("validation_status") == "validated"
    aligned = meta.get("temporal_alignment") == "validated"
    for option in result["options"]:
        parts = {
            "core_environmental_data": 35 if all(src in feats["sources"] for src in CORE_SOURCES) else 0,
            "data_validation": 20 if validated else 0,
            "crop_rule_verification": 25 if option["crop_verified"] else 0,
            "farmer_input_completeness": 10,
            "temporal_alignment": 10 if aligned else 0,
        }
        score = sum(parts.values())
        dots = 3 if score >= 80 else (2 if score >= 55 else 1)
        if not option["crop_verified"]:
            dots = min(dots, 2)
        option["confidence_score"] = score
        option["confidence_dots"] = dots
        confidence.append({"option_id": option["id"], "score": score, "dots": dots, "breakdown": parts})
    regional_payload = deps.regional_context_fn()
    return {
        "status": "ok",
        "is_demo": bool(s.demo_mode and deps.store.path.name.endswith("example.json")),
        "data_mode": "DEMO" if s.demo_mode else "REAL",
        "analysis_method": "nearest_available_point",
        "data_snapshot": {
            "satellite_window": meta.get("satellite_window"),
            "landsat_date": meta.get("landsat_date"),
        },
        "feature_point_id": feats.get("_point_id"),
        "field_health": result["field_health"],
        "field_context": {"vegetation_condition": result["field_health"],
                          "cluster_id": None, "cluster_label": None,
                          "cluster_interpretation": "Environmental clustering unavailable; no K-Means model was trained."},
        "regional_context": regional_payload.get("regional_context", {}) if regional_payload.get("available") else {},
        "regional_context_status": regional_payload.get("status", "unavailable"),
        "temporal_alignment": regional_payload.get("temporal_alignment"),
        "forecast": {"available": forecast_ok, "source": "meteomatics",
                     "is_live": bool(forecast.get("is_live")),
                     "is_sample": bool(forecast.get("is_sample")),
                     "expired": bool(forecast.get("expired")),
                     "generated_at": forecast.get("generated_at"),
                     "valid_from": forecast.get("valid_from"),
                     "valid_until": forecast.get("valid_until"),
                     "days": forecast.get("days", [])},
        "options": result["options"],
        "confidence": confidence,
        "dataset_metadata": meta.get("sources", {}),
        "model_metadata": {"name": None, "version": None, "status": "not_trained"},
        "limitations": [
            "Crop rotation is rule-based and does not predict crop yield.",
            "Crop-rule values remain unverified and require local agronomist review.",
            "SMAP and GPM are regional context, not field measurements.",
            "No validated Landsat feature set or K-Means model is currently available.",
        ],
        "disclaimer_id": DISCLAIMER_ID,
    }


def crops_payload(deps: Deps) -> list:
    web_crops = deps.settings.web_dir / "static" / "crops"
    out = []
    for c in deps.crops.values():
        pic = web_crops / f"{c.id}.png"
        out.append({
            "id": c.id, "season": c.season,
            "names": {"en": c.name_en, "ur": c.name_ur, "sd": c.name_sd},
            "picture_url": f"/static/crops/{c.id}.png" if pic.exists() else None,
            "verified": c.verified,
        })
    for cid, (en, ur, sd) in {"sugarcane": ("Sugarcane", "گنا", "ڪمند"),
                              "banana": ("Banana / orchard", "کیلا / باغ", "ڪيلو / باغ")}.items():
        pic = web_crops / f"{cid}.png"
        out.append({"id": cid, "season": None, "names": {"en": en, "ur": ur, "sd": sd},
                    "picture_url": f"/static/crops/{cid}.png" if pic.exists() else None,
                    "verified": False, "special": SPECIAL[cid]})
    return out
