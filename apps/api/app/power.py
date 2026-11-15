"""NASA POWER client (daily point API) with disk cache.

Used only to fill in climate features when features.json lacks them.
There is NO invented fallback: a saved real response may be placed in
data/api-samples/power_sample.json (same shape as the API's "parameter" block);
if neither the network, the cache nor that file works, POWER counts as missing.
"""
from __future__ import annotations

import json
import csv
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Optional

POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN"
FILL = -999.0
HEAT_THRESHOLD_C = 40.0      # configurable, unverified (plan section 5.3)


def build_url(lat: float, lon: float, start: str = "20150101", end: str = "20251231") -> str:
    q = {"parameters": PARAMS, "community": "AG", "longitude": f"{lon}", "latitude": f"{lat}",
         "start": start, "end": end, "format": "JSON"}
    return POWER_URL + "?" + urllib.parse.urlencode(q, safe=",")


def fetch_daily(lat: float, lon: float, timeout: float = 45.0) -> Optional[dict]:
    """Returns the 'parameter' block ({"T2M_MAX": {"20150101": 31.2, ...}, ...}) or None on any failure."""
    try:
        req = urllib.request.Request(build_url(lat, lon), headers={"User-Agent": "AgriShiftAI/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode("utf-8"))
        param = payload["properties"]["parameter"]
        return param if isinstance(param, dict) and param else None
    except Exception:
        return None


def _valid(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v != FILL and v == v


def summarize(param: dict, heat_threshold: float = HEAT_THRESHOLD_C) -> Optional[dict]:
    """Daily POWER data -> the climate features used by the backend.

    heat_days_40c_by_month[m]  = average over years of (days with T2M_MAX >= threshold) in month m
    tmax_mean_by_month[m]      = mean T2M_MAX in month m
    rain_mm_by_month[m]        = average over years of the monthly PRECTOTCORR total
    rh_mean, wind_mean         = overall means of RH2M and WS2M
    Missing-value days (-999) are skipped. Returns None unless T2M_MAX covers all 12 months.
    """
    tmax = param.get("T2M_MAX") or {}
    heat_by_ym: Dict[tuple, int] = defaultdict(int)
    tmax_vals: Dict[int, list] = defaultdict(list)
    for date_s, v in tmax.items():
        if not _valid(v) or len(date_s) != 8:
            continue
        y, m = int(date_s[:4]), int(date_s[4:6])
        tmax_vals[m].append(float(v))
        heat_by_ym[(y, m)] += 1 if v >= heat_threshold else 0
    if set(tmax_vals) != set(range(1, 13)):
        return None
    heat_years: Dict[int, list] = defaultdict(list)
    for (y, m), n in heat_by_ym.items():
        heat_years[m].append(n)
    heat = {m: sum(heat_years[m]) / len(heat_years[m]) for m in range(1, 13)}
    tmax_mean = {m: sum(tmax_vals[m]) / len(tmax_vals[m]) for m in range(1, 13)}

    rain_ym: Dict[tuple, float] = defaultdict(float)
    for date_s, v in (param.get("PRECTOTCORR") or {}).items():
        if _valid(v) and len(date_s) == 8:
            rain_ym[(int(date_s[:4]), int(date_s[4:6]))] += float(v)
    rain_years: Dict[int, list] = defaultdict(list)
    for (y, m), total in rain_ym.items():
        rain_years[m].append(total)
    out = {"heat_days_40c_by_month": heat, "tmax_mean_by_month": tmax_mean}
    if set(rain_years) == set(range(1, 13)):
        out["rain_mm_by_month"] = {m: sum(rain_years[m]) / len(rain_years[m]) for m in range(1, 13)}

    for key, name in (("RH2M", "rh_mean"), ("WS2M", "wind_mean")):
        vals = [float(v) for v in (param.get(key) or {}).values() if _valid(v)]
        if vals:
            out[name] = sum(vals) / len(vals)
    return out


def summarize_csv(path: Path) -> Optional[dict]:
    """Read an already-saved NASA POWER daily CSV without making a provider request."""
    path = Path(path)
    parameters = {name: {} for name in (
        "T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN"
    )}
    try:
        with path.open(newline="", encoding="utf-8-sig") as stream:
            for line in stream:
                if line.strip() == "-END HEADER-":
                    break
            reader = csv.DictReader(stream)
            required = {"YEAR", "DOY", *parameters}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                return None
            for row in reader:
                try:
                    day = (date(int(row["YEAR"]), 1, 1) + timedelta(days=int(row["DOY"]) - 1)).strftime("%Y%m%d")
                except (TypeError, ValueError):
                    continue
                for name in parameters:
                    raw = row.get(name, "")
                    try:
                        value = float(raw)
                    except (TypeError, ValueError):
                        continue
                    if _valid(value):
                        parameters[name][day] = value
    except OSError:
        return None
    return summarize(parameters)


def get_monthly_features(lat: float, lon: float, cache_dir: Path, samples_dir: Path,
                         fetcher=fetch_daily, csv_path: Optional[Path] = None) -> Optional[dict]:
    """Use configured local CSV, then cache, live fetch, saved JSON sample, or None."""
    if csv_path:
        local = summarize_csv(csv_path)
        if local:
            return local
    cache_dir = Path(cache_dir)
    cache_file = cache_dir / f"power_{lat:.2f}_{lon:.2f}.json"
    param = None
    if cache_file.exists():
        try:
            param = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            param = None
    if param is None:
        param = fetcher(lat, lon)
        if param:
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(param), encoding="utf-8")
            except OSError:
                pass
    if param is None:
        sample = Path(samples_dir) / "power_sample.json"
        if sample.exists():
            try:
                param = json.loads(sample.read_text(encoding="utf-8"))
            except Exception:
                param = None
    return summarize(param) if param else None
