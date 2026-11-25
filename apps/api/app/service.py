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
from .ml.clustering import describe_cluster
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
    clustering_fn: Callable[[dict, dict], Optional[dict]]


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
        return regional_context_mod.get_regional_context(s.root)

    def clustering_fn(point: dict, features: dict) -> Optional[dict]:
        if s.demo_mode:
            return None
        return describe_cluster(s.root / "ml" / "clustering" / "artifacts", point, features)

    return Deps(settings=s, crops=crops, store=store, weather_fn=weather_fn,
                 power_fn=power_fn, regional_context_fn=regional_context_fn,
                 clustering_fn=clustering_fn)


def _insufficient(reason_id: str, demo_mode: bool = False) -> dict:
    return {"status": "insufficient_data", "reason_id": reason_id,
            "data_mode": "DEMO" if demo_mode else "REAL",
            "limitations": ["Validated Landsat, terrain, and climate features are required for a field recommendation."]}


def _in_pilot_area(s: Settings, lat: float, lon: float) -> bool:
    return s.min_lat <= lat <= s.max_lat and s.min_lon <= lon <= s.max_lon


def analyze(req: AnalyzeRequest, deps: Deps, today: Optional[date] = None) -> dict:
    """Build an explainable rotation response from the nearest validated pilot point."""
    s = deps.settings
    known = set(deps.crops) | set(SPECIAL)
    if req.current_crop not in known:
        raise ValueError(f"unknown current_crop '{req.current_crop}'")
    if req.previous_crop not in (None, "", "unknown") and req.previous_crop not in known:
        raise ValueError(f"unknown previous_crop '{req.previous_crop}'")
    if req.current_crop in SPECIAL:
        return {"status": "not_applicable", "reason_id": SPECIAL[req.current_crop],
                "data_mode": "DEMO" if s.demo_mode else "REAL"}
    if not _in_pilot_area(s, req.lat, req.lon) or deps.store.contains(req.lat, req.lon) is False:
        return {"status": "not_applicable", "reason_id": "out_of_area",
                "data_mode": "DEMO" if s.demo_mode else "REAL",
                "limitations": ["This location is outside the validated Hyderabad pilot coverage."]}

    try:
        feats = deps.store.get(req.lat, req.lon, power_fallback=lambda: deps.power_fn(req.lat, req.lon))
    except Exception:
        feats = None
    if feats is None:
        if deps.store.available():
            return {"status": "not_applicable", "reason_id": "nearest_point_too_far",
                    "data_mode": "DEMO" if s.demo_mode else "REAL",
                    "limitations": ["The nearest validated environmental analysis point is farther than 2,000 m."]}
        return _insufficient("no_data_001", s.demo_mode)

    required = {
        "ndvi_mean", "ndmi_mean", "bsi_mean", "surface_temp_c", "cloud_free_fraction",
        "low_lying_flag", "elevation_m", "slope_deg", "heat_days_40c_by_month",
        "tmax_mean_by_month", "rain_mm_by_month",
    }
    if not all(source in feats["sources"] for source in CORE_SOURCES) or not required.issubset(feats):
        return _insufficient("no_data_001", s.demo_mode)

    try:
        forecast = deps.weather_fn(req.lat, req.lon)
    except Exception:
        forecast = {"available": False, "status": "unavailable", "source": "meteomatics",
                    "is_live": False, "is_sample": False, "days": []}
    forecast_ok = bool(forecast.get("available"))
    engine_features = {
        "ndvi_mean": feats["ndvi_mean"],
        "low_lying_flag": feats["low_lying_flag"],
        "heat_days_40c_by_month": feats["heat_days_40c_by_month"],
        # Coarse context and forecast availability cannot replace core inputs.
        "sources_present": len(CORE_SOURCES),
    }
    engine_request = {
        "current_crop": req.current_crop, "water_source": req.water_source,
        "water_amount": req.water_amount, "salinity": req.salinity,
        "waterlogging": req.waterlogging, "priority": req.priority,
    }
    try:
        rotation = recommend(deps.crops, engine_request, engine_features, today or date.today(),
                             include_score_breakdown=True)
    except ValueError:
        return _insufficient("no_data_001", s.demo_mode)
    if rotation["status"] != "ok":
        return {"status": "insufficient_data", "reason_id": rotation["reason_id"],
                "data_mode": "DEMO" if s.demo_mode else "REAL",
                "limitations": ["Three distinct, rule-valid rotation strategies could not be generated."]}

    meta = deps.store.meta()
    point = feats.get("_point") or {}
    cluster = deps.clustering_fn(point, feats) if deps.clustering_fn else None
    quality = feats.get("_data_quality") or {}
    validated = bool(quality.get("core_sources_valid"))
    raw_temporal = quality.get("temporal_alignment_score", 0.0)
    try:
        temporal_points = round(max(0.0, min(1.0, float(raw_temporal))) * 10, 1)
    except (TypeError, ValueError):
        temporal_points = 0.0
    farmer_values = (req.current_crop, req.water_source, req.water_amount, req.salinity, req.waterlogging)
    farmer_points = round(sum(v not in (None, "", "unknown") for v in farmer_values) / 5 * 10, 1)
    confidence_by_option = []
    for option in rotation["options"]:
        parts = {
            "core_environmental_data": 35,
            "data_validation": 20 if validated else 0,
            "crop_rule_verification": 25 if option["crop_verified"] else 0,
            "farmer_input_completeness": farmer_points,
            "temporal_alignment": temporal_points,
        }
        score = round(sum(parts.values()), 1)
        dots_count = 3 if score >= 80 else (2 if score >= 55 else 1)
        if not option["crop_verified"]:
            dots_count = min(dots_count, 2)
        option["confidence_score"] = score
        option["confidence_dots"] = dots_count
        option["expert_review_required"] = bool(option.get("expert_needed") or not option["crop_verified"])
        option["confidence_reasons"] = []
        if not validated:
            option["confidence_reasons"].append("Source validation is incomplete.")
        if not option["crop_verified"]:
            option["confidence_reasons"].append("Crop constraints are unverified and require local expert review.")
        if farmer_points < 10:
            option["confidence_reasons"].append("Some farmer observations are unknown or incomplete.")
        if temporal_points < 10:
            option["confidence_reasons"].append("Source observation periods are not fully aligned.")
        confidence_by_option.append({"option_id": option["id"], "score": score,
                                     "dots": dots_count, "breakdown": parts})

    regional_payload = deps.regional_context_fn()
    regional = regional_payload.get("regional_context", {}) if regional_payload.get("available") else {}
    dates = meta.get("source_dates") or {}
    resolutions = meta.get("source_resolutions") or {}
    landsat_date = dates.get("landsat_9") or meta.get("landsat_date")
    scene = "LC09_L2SP_151043_20250930_20251001_02_T1" if landsat_date == "2025-09-30" else None
    confidence_scores = [x["score"] for x in confidence_by_option]
    overall_score = min(confidence_scores) if confidence_scores else 0
    overall_dots = 3 if overall_score >= 80 else (2 if overall_score >= 55 else 1)
    reasons = sorted({r for option in rotation["options"] for r in option["confidence_reasons"]})
    cluster_value = cluster or {"cluster_id": None, "cluster_label": None,
                                "interpretation": "Environmental clustering is unavailable."}
    environmental = {key: feats.get(key) for key in (
        "ndvi_mean", "ndmi_mean", "bsi_mean", "surface_temp_c", "cloud_free_fraction",
        "elevation_m", "slope_deg", "low_lying_flag", "tmax_mean_by_month", "tmin_mean_by_month",
        "heat_days_40c_by_month", "rain_mm_by_month", "rh_mean", "wind_mean", "solar_radiation_mean",
    )}
    dataset_metadata = {
        "landsat_9": {"scene": scene, "observation_date": landsat_date, "resolution": resolutions.get("landsat_9")},
        "srtm": {"observation_date": dates.get("srtm_dem"), "resolution": resolutions.get("srtm_dem")},
        "nasa_power": {"period": dates.get("nasa_power_climate"), "resolution": resolutions.get("nasa_power_climate")},
    }
    return {
        "status": "ok", "is_demo": bool(s.demo_mode),
        "data_mode": "DEMO" if s.demo_mode else "REAL",
        "analysis_method": "nearest_precomputed_point",
        "data_snapshot": {"landsat_date": landsat_date, "scene": scene,
                          "source_dates": dates, "source_resolutions": resolutions},
        "feature_point_id": feats.get("_point_id"),
        "feature_point": {"id": feats.get("_point_id"), "distance_m": feats.get("_distance_m"),
                          "analysis_radius_m": feats.get("_analysis_radius_m", req.radius_m),
                          "grid_spacing_m": feats.get("_grid_spacing_m")},
        "field_context": {"vegetation_condition": rotation["field_health"],
                          "cluster": cluster_value,
                          "cluster_id": cluster_value.get("cluster_id"),
                          "cluster_label": cluster_value.get("cluster_label"),
                          "cluster_interpretation": cluster_value.get("interpretation"),
                          "environmental_features": environmental},
        "regional_context": regional,
        "regional_context_status": regional_payload.get("status", "unavailable"),
        "temporal_alignment": regional_payload.get("temporal_alignment", "not_aligned"),
        "weather": forecast,
        "forecast": {"available": forecast_ok, "status": forecast.get("status", "unavailable"),
                     "source": "meteomatics", "is_live": bool(forecast.get("is_live")),
                     "is_sample": bool(forecast.get("is_sample")), "expired": bool(forecast.get("expired")),
                     "generated_at": forecast.get("generated_at"), "valid_from": forecast.get("valid_from"),
                     "valid_until": forecast.get("valid_until"), "coordinates": forecast.get("coordinates"),
                     "days": forecast.get("days", [])},
        "options": rotation["options"], "rotation_options": rotation["options"],
        "confidence_by_option": confidence_by_option,
        "confidence": {"score": overall_score, "dots": "●" * overall_dots + "○" * (3 - overall_dots),
                       "reasons": reasons, "formula": {"core_environmental_data": 35,
                       "data_validation": 20, "crop_rule_verification": 25,
                       "farmer_input_completeness": 10, "temporal_alignment": 10}},
        "dataset_metadata": dataset_metadata,
        "model_metadata": {"name": cluster.get("model_name") if cluster else None,
                           "version": cluster.get("model_version") if cluster else None,
                           "status": "available" if cluster else "unavailable"},
        "limitations": [
            "Crop rotation is rule-based and does not predict crop yield.",
            "Crop-rule values remain unverified and require local agronomist review.",
            "SMAP and GPM are coarse regional context, not field measurements.",
            "The nearest validated environmental analysis point was used; this is not an exact field analysis.",
            "GPM provides a weekly mean daily rate, not daily totals, rainy-day counts, or maximum daily rainfall.",
            "Environmental clustering is not a crop-health or disease diagnosis.",
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
