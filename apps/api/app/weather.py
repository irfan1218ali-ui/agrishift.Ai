"""Meteomatics hourly weather adapter. Forecasts are context only, never rotation scores."""
from __future__ import annotations

import base64
import json
import math
import time
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

API = "https://api.meteomatics.com"
PARAMS = "t_2m:C,precip_1h:mm,relative_humidity_2m:p,wind_speed_10m:ms"
TTL_SECONDS = 3 * 3600
_cache: Dict[Tuple[float, float], Tuple[float, dict]] = {}


def build_url(lat: float, lon: float, start: datetime, days: int = 1) -> str:
    start = start.astimezone(timezone.utc)
    s = start.replace(minute=0, second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")
    e = (start.replace(minute=0, second=0, microsecond=0) + timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"{API}/{s}--{e}:PT1H/{PARAMS}/{lat},{lon}/json"


def parse_meteomatics(payload: dict) -> dict:
    """Normalize provider series into hourly records and transparent daily summaries."""
    names = {
        "t_2m:C": "temperature_c", "precip_1h:mm": "precipitation_mm",
        "relative_humidity_2m:p": "relative_humidity_percent", "wind_speed_10m:ms": "wind_speed_ms",
    }
    by_time: Dict[str, dict] = {}
    for item in payload.get("data", []):
        output_key = names.get(item.get("parameter", ""))
        if not output_key:
            continue
        coordinates = item.get("coordinates") or []
        if not coordinates:
            continue
        for observation in (coordinates[0].get("dates") or []):
            timestamp = str(observation.get("date", ""))
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                continue
            value = observation.get("value")
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                normalized = None
            else:
                normalized = float(value)
            by_time.setdefault(dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"), {})[output_key] = normalized
    hourly = [{"timestamp_utc": t, **values} for t, values in sorted(by_time.items())]
    grouped: dict[str, list] = defaultdict(list)
    for row in hourly:
        grouped[row["timestamp_utc"][:10]].append(row)
    daily = []
    for day, rows in sorted(grouped.items()):
        temps = [r["temperature_c"] for r in rows if r.get("temperature_c") is not None]
        rain = [r["precipitation_mm"] for r in rows if r.get("precipitation_mm") is not None]
        humidities = [r["relative_humidity_percent"] for r in rows if r.get("relative_humidity_percent") is not None]
        winds = [r["wind_speed_ms"] for r in rows if r.get("wind_speed_ms") is not None]
        daily.append({
            "date": day, "tmax_c": max(temps) if temps else None, "tmin_c": min(temps) if temps else None,
            "rain_total_mm": sum(rain) if rain else None,
            "rh_mean": sum(humidities) / len(humidities) if humidities else None,
            "wind_max_ms": max(winds) if winds else None,
        })
    return {"hourly": hourly, "days": daily}


def fetch_meteomatics(lat: float, lon: float, user: str, password: str,
                      now: datetime, timeout: float = 6.0) -> dict:
    url = build_url(lat, lon, now)
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {token}", "User-Agent": "AgriShiftAI/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return parse_meteomatics(payload)


def _load_sample(samples_dir: Path, today: date, sample_file: Optional[Path] = None) -> Optional[dict]:
    path = Path(sample_file) if sample_file else Path(samples_dir) / "meteomatics_sample.json"
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("data"), list):
            parsed = parse_meteomatics(payload)
            generated = payload.get("dateGenerated")
            times = [r["timestamp_utc"] for r in parsed["hourly"]]
            valid_from, valid_until = (times[0], times[-1]) if times else (None, None)
        elif isinstance(payload, dict) and isinstance(payload.get("days"), list):
            # Compatibility for the clearly labelled ZIP placeholder; its dates are not implied to be live.
            parsed = {"hourly": [], "days": payload["days"]}
            generated = payload.get("generated_at")
            valid_from = payload.get("valid_from")
            valid_until = payload.get("valid_until")
        else:
            return None
        if not parsed["days"]:
            return None
        now = datetime.now(timezone.utc)
        end_dt = None
        if valid_until:
            try:
                end_dt = datetime.fromisoformat(str(valid_until).replace("Z", "+00:00"))
            except ValueError:
                pass
        expired = bool(end_dt and end_dt < now)
        return {"available": True, "source": "meteomatics", "is_live": False, "is_sample": True,
                "generated_at": generated, "valid_from": valid_from, "valid_until": valid_until,
                "expired": expired, **parsed}
    except (OSError, ValueError, TypeError, KeyError):
        return None


def get_weather(lat: float, lon: float, *, user: str, password: str, samples_dir: Path,
                demo_mode: bool, now: Optional[datetime] = None,
                fetcher: Callable[..., dict] = fetch_meteomatics, use_cache: bool = True,
                sample_file: Optional[Path] = None) -> dict:
    now = now or datetime.now(timezone.utc)
    key = (round(lat, 2), round(lon, 2))
    if user and password:
        if use_cache and key in _cache and time.time() - _cache[key][0] < TTL_SECONDS:
            return _cache[key][1]
        try:
            data = fetcher(lat, lon, user, password, now)
            if data and data.get("days"):
                hourly = data.get("hourly", [])
                valid_from = hourly[0]["timestamp_utc"] if hourly else None
                valid_until = hourly[-1]["timestamp_utc"] if hourly else None
                info = {"available": True, "source": "meteomatics", "is_live": True, "is_sample": False,
                        "generated_at": now.isoformat().replace("+00:00", "Z"), "valid_from": valid_from,
                        "valid_until": valid_until, "expired": False, **data}
                if use_cache:
                    _cache[key] = (time.time(), info)
                return info
        except Exception:
            pass
    sample = _load_sample(samples_dir, now.date(), sample_file)
    if sample:
        return sample
    return {"available": False, "source": "meteomatics", "is_live": False, "is_sample": False,
            "expired": False, "hourly": [], "days": []}
