"""Validated nearest-point access for precomputed environmental features."""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import median
from typing import Callable, Dict, Optional, Tuple


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometres."""
    radius_km = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(a))


def _num(value) -> Optional[float]:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)
    return None


def _month_dict(values) -> Optional[Dict[int, float]]:
    """Normalize a complete month-keyed map, returning None for partial data."""
    if not isinstance(values, dict):
        return None
    out: Dict[int, float] = {}
    for key, value in values.items():
        try:
            month = int(key)
        except (TypeError, ValueError):
            return None
        number = _num(value)
        if number is None or not 1 <= month <= 12:
            return None
        out[month] = number
    return out if set(out) == set(range(1, 13)) else None


def normalize(raw: dict, min_cloud_free: float,
              power_fallback: Optional[Callable[[], Optional[dict]]] = None) -> dict:
    """Keep only validated feature values; SMAP/GPM remain context-only."""
    raw = raw or {}
    result: dict = {}
    sources = []

    ndvi = _num(raw.get("ndvi_mean"))
    cloud_free = _num(raw.get("cloud_free_fraction"))
    if ndvi is not None and (cloud_free is None or cloud_free >= min_cloud_free):
        result["ndvi_mean"] = ndvi
        for key in ("ndmi_mean", "bsi_mean", "surface_temp_c", "cloud_free_fraction"):
            if _num(raw.get(key)) is not None:
                result[key] = _num(raw[key])
        sources.append("landsat")

    if isinstance(raw.get("low_lying_flag"), bool):
        result["low_lying_flag"] = raw["low_lying_flag"]
        for key in ("elevation_m", "slope_deg"):
            if _num(raw.get(key)) is not None:
                result[key] = _num(raw[key])
        sources.append("srtm")

    heat = _month_dict(raw.get("heat_days_40c_by_month"))
    power = raw
    if heat is None and power_fallback is not None:
        fallback = power_fallback()
        if fallback:
            power = fallback
            heat = _month_dict(fallback.get("heat_days_40c_by_month"))
    if heat is not None:
        result["heat_days_40c_by_month"] = heat
        for key in ("tmin_mean_by_month", "tmax_mean_by_month", "rain_mm_by_month"):
            values = _month_dict(power.get(key))
            if values is not None:
                result[key] = values
        for key in ("rh_mean", "wind_mean", "solar_radiation_mean"):
            if _num(power.get(key)) is not None:
                result[key] = _num(power[key])
        sources.append("power")

    for key in ("smap_surface_mean", "smap_rootzone_mean", "gpm_mean_daily_rate_mm_day"):
        if _num(raw.get(key)) is not None:
            result[key] = _num(raw[key])
    if "smap_surface_mean" in result:
        sources.append("smap")
    if "gpm_mean_daily_rate_mm_day" in result:
        sources.append("gpm")

    result["sources"] = sources
    result["sources_present"] = len(sources)
    return result


class FeatureStore:
    """Cache a validated feature document and perform bounded Haversine lookup."""

    def __init__(self, path: Path, max_km: float = 2.0, min_cloud_free: float = 0.5):
        self.path = Path(path)
        self.max_km = max_km
        self.min_cloud_free = min_cloud_free
        self._mtime: Optional[float] = None
        self._data: Optional[dict] = None
        self._grid_spacing_m: Optional[float] = None

    def _load(self) -> Optional[dict]:
        try:
            mtime = self.path.stat().st_mtime
        except OSError:
            self._data, self._mtime, self._grid_spacing_m = None, None, None
            return None
        if self._data is None or mtime != self._mtime:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("points"), list) or not data["points"]:
                raise ValueError("feature document must contain a non-empty points array")
            meta = data.get("meta")
            if not isinstance(meta, dict):
                raise ValueError("feature document must contain metadata")
            if meta.get("data_mode") in {"real", "demo"} and not meta.get("feature_schema_version"):
                raise ValueError("feature_schema_version is missing")
            for point in data["points"]:
                if (not isinstance(point, dict) or _num(point.get("lat")) is None
                        or _num(point.get("lon")) is None or not isinstance(point.get("features"), dict)):
                    raise ValueError("feature point has invalid coordinates or features")
            self._data, self._mtime = data, mtime
            self._grid_spacing_m = self._estimate_grid_spacing(data["points"])
        return self._data

    @staticmethod
    def _estimate_grid_spacing(points: list[dict]) -> Optional[float]:
        if len(points) < 2:
            return None
        nearest_distances = []
        for index, point in enumerate(points):
            distance = min(
                haversine_km(point["lat"], point["lon"], other["lat"], other["lon"])
                for other_index, other in enumerate(points) if other_index != index
            )
            nearest_distances.append(distance * 1000)
        return float(median(nearest_distances))

    def available(self) -> bool:
        try:
            data = self._load()
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            return False
        return bool(data and data["points"])

    def meta(self) -> dict:
        data = self._load()
        return (data or {}).get("meta", {}) or {}

    def contains(self, lat: float, lon: float) -> Optional[bool]:
        bounds = self.meta().get("pilot_bounds") or {}
        if not bounds:
            return None
        return (bounds["south"] <= lat <= bounds["north"]
                and bounds["west"] <= lon <= bounds["east"])

    def nearest(self, lat: float, lon: float) -> Optional[Tuple[dict, float]]:
        """Return (point, distance_km) only inside the configured distance limit."""
        data = self._load()
        if not data:
            return None
        best, best_km = None, None
        for point in data["points"]:
            km = haversine_km(lat, lon, point["lat"], point["lon"])
            if best_km is None or km < best_km:
                best, best_km = point, km
        if best is None or best_km > self.max_km:
            return None
        return best, best_km

    def get(self, lat: float, lon: float,
            power_fallback: Optional[Callable[[], Optional[dict]]] = None) -> Optional[dict]:
        hit = self.nearest(lat, lon)
        if hit is None:
            return None
        point, km = hit
        raw = dict(point.get("features") or {})
        regional = point.get("regional_context") or {}
        raw.update({key: regional[key] for key in (
            "smap_surface_mean", "smap_rootzone_mean", "gpm_mean_daily_rate_mm_day"
        ) if key in regional})
        features = normalize(raw, self.min_cloud_free, power_fallback)
        cluster = point.get("clustering") or {
            "cluster_id": point.get("cluster_id"),
            "cluster_label": point.get("cluster_label"),
            "cluster_distance": point.get("cluster_distance"),
        }
        features.update({
            "_point_id": point.get("id"),
            "_distance_km": round(km, 4),
            "_distance_m": round(km * 1000, 1),
            "_analysis_radius_m": int(point.get("analysis_radius_m", 150)),
            "_grid_spacing_m": round(self._grid_spacing_m) if self._grid_spacing_m else None,
            "_analysis_method": "nearest_precomputed_point",
            "_cluster": cluster,
            "_regional_context": regional,
            "_data_quality": point.get("data_quality") or {},
            "_point": point,
        })
        return features
