"""Feature reader: nearest pre-processed point from features.json (made by Member 4).

features.json format
--------------------
{
  "meta": {"satellite_window": "2025-09-01/2025-09-30", "landsat_date": "2025-09-22"},
  "points": [
    {"id": "hyd_001", "lat": 25.39, "lon": 68.37,
     "features": {
        "ndvi_mean": 0.41, "ndmi_mean": 0.12, "bsi_mean": 0.03, "surface_temp_c": 36.2, "cloud_free_fraction": 0.93,
        "elevation_m": 28.0, "slope_deg": 0.3, "low_lying_flag": false,
        "tmax_mean_by_month": {"1": 24.1, ... "12": 25.0},
        "heat_days_40c_by_month": {"1": 0, ... "12": 0},
        "rain_mm_by_month": {"1": 6, ...}, "rh_mean": 52.0, "wind_mean": 3.1,
        "smap_surface_mean": 0.21, "smap_rootzone_mean": 0.30,
        "gpm_total_mm": 18.2, "gpm_rainy_days": 3, "gpm_max_daily_mm": 9.0
     }}
  ]
}
Missing values: leave the key out or use null. NEVER fill with guesses.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _num(x) -> Optional[float]:
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)) and math.isfinite(x):
        return float(x)
    return None


def _month_dict(d) -> Optional[Dict[int, float]]:
    """{'1': v, ...} -> {1: v, ...}; returns None unless all 12 months are numeric."""
    if not isinstance(d, dict):
        return None
    out: Dict[int, float] = {}
    for k, v in d.items():
        try:
            m = int(k)
        except (TypeError, ValueError):
            return None
        n = _num(v)
        if n is None or not 1 <= m <= 12:
            return None
        out[m] = n
    return out if set(out) == set(range(1, 13)) else None


def normalize(raw: dict, min_cloud_free: float,
              power_fallback: Optional[Callable[[], Optional[dict]]] = None) -> dict:
    """Validate one point's raw features. Returns a dict with:
        values (only valid ones), sources (list of present source names), sources_present (int)
    A source counts as present only when its values are valid.
    """
    raw = raw or {}
    f: dict = {}
    sources = []

    # --- Landsat (unusable when too cloudy)
    ndvi = _num(raw.get("ndvi_mean"))
    cloud_free = _num(raw.get("cloud_free_fraction"))
    if ndvi is not None and (cloud_free is None or cloud_free >= min_cloud_free):
        f["ndvi_mean"] = ndvi
        for k in ("ndmi_mean", "bsi_mean", "surface_temp_c", "cloud_free_fraction"):
            if _num(raw.get(k)) is not None:
                f[k] = _num(raw[k])
        sources.append("landsat")

    # --- SRTM
    if isinstance(raw.get("low_lying_flag"), bool):
        f["low_lying_flag"] = raw["low_lying_flag"]
        for k in ("elevation_m", "slope_deg"):
            if _num(raw.get(k)) is not None:
                f[k] = _num(raw[k])
        sources.append("srtm")

    # --- NASA POWER (needs all 12 months of heat days)
    heat = _month_dict(raw.get("heat_days_40c_by_month"))
    power = raw
    if heat is None and power_fallback is not None:
        fb = power_fallback()
        if fb:
            power = fb
            heat = _month_dict(fb.get("heat_days_40c_by_month"))
    if heat is not None:
        f["heat_days_40c_by_month"] = heat
        for k in ("tmax_mean_by_month", "rain_mm_by_month"):
            md = _month_dict(power.get(k))
            if md is not None:
                f[k] = md
        for k in ("rh_mean", "wind_mean"):
            if _num(power.get(k)) is not None:
                f[k] = _num(power[k])
        sources.append("power")

    # --- SMAP / GPM (regional context only, not scored)
    if _num(raw.get("smap_surface_mean")) is not None:
        f["smap_surface_mean"] = _num(raw["smap_surface_mean"])
        if _num(raw.get("smap_rootzone_mean")) is not None:
            f["smap_rootzone_mean"] = _num(raw["smap_rootzone_mean"])
        sources.append("smap")
    if _num(raw.get("gpm_total_mm")) is not None:
        f["gpm_total_mm"] = _num(raw["gpm_total_mm"])
        for k in ("gpm_rainy_days", "gpm_max_daily_mm"):
            if _num(raw.get(k)) is not None:
                f[k] = _num(raw[k])
        sources.append("gpm")

    f["sources"] = sources
    f["sources_present"] = len(sources)
    return f


class FeatureStore:
    """Loads features.json lazily (re-reads if the file changes)."""

    def __init__(self, path: Path, max_km: float = 5.0, min_cloud_free: float = 0.5):
        self.path = Path(path)
        self.max_km = max_km
        self.min_cloud_free = min_cloud_free
        self._mtime: Optional[float] = None
        self._data: Optional[dict] = None

    def _load(self) -> Optional[dict]:
        try:
            mtime = self.path.stat().st_mtime
        except OSError:
            self._data, self._mtime = None, None
            return None
        if self._data is None or mtime != self._mtime:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict) or not isinstance(data.get("points"), list):
                raise ValueError(f"{self.path}: expected an object with a 'points' list")
            self._data, self._mtime = data, mtime
        return self._data

    def available(self) -> bool:
        try:
            d = self._load()
        except Exception:
            return False
        return bool(d and d["points"])

    def meta(self) -> dict:
        d = self._load()
        return (d or {}).get("meta", {}) or {}

    def nearest(self, lat: float, lon: float) -> Optional[Tuple[dict, float]]:
        """(raw point dict, distance_km) of the closest point within max_km, else None."""
        d = self._load()
        if not d:
            return None
        best, best_km = None, None
        for p in d["points"]:
            plat, plon = _num(p.get("lat")), _num(p.get("lon"))
            if plat is None or plon is None:
                continue
            km = haversine_km(lat, lon, plat, plon)
            if best_km is None or km < best_km:
                best, best_km = p, km
        if best is None or best_km > self.max_km:
            return None
        return best, best_km

    def get(self, lat: float, lon: float,
            power_fallback: Optional[Callable[[], Optional[dict]]] = None) -> Optional[dict]:
        hit = self.nearest(lat, lon)
        if hit is None:
            return None
        point, km = hit
        feats = normalize(point.get("features") or {}, self.min_cloud_free, power_fallback)
        feats["_point_id"] = point.get("id")
        feats["_distance_km"] = round(km, 3)
        return feats
