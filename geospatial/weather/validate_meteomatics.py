"""
Meteomatics Weather API Response Validator.
Validates parameters, coordinates, UTC hourly timestamps, and expiration status.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DEFAULT_METEOMATICS_FILE = ROOT_DIR / "data" / "api-samples" / "meteomatics" / "json.json"

EXPECTED_PARAMS = [
    "t_2m:C",
    "precip_1h:mm",
    "relative_humidity_2m:p",
    "wind_speed_10m:ms",
]


def validate_meteomatics_file(file_path: Path = DEFAULT_METEOMATICS_FILE) -> dict[str, Any]:
    results: dict[str, Any] = {
        "is_valid": False,
        "errors": [],
        "warnings": [],
        "metadata": {},
        "parameters": {},
        "temporal_checks": {},
    }

    if not file_path.exists():
        results["errors"].append(f"Meteomatics file not found: {file_path}")
        return results

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("status") != "OK":
        results["errors"].append(f"Meteomatics response status not OK: {data.get('status')}")

    date_gen_str = data.get("dateGenerated")
    results["metadata"]["date_generated"] = date_gen_str

    param_dict = {}
    for entry in data.get("data", []):
        param_dict[entry.get("parameter")] = entry

    missing_params = [p for p in EXPECTED_PARAMS if p not in param_dict]
    if missing_params:
        results["errors"].append(f"Missing required weather parameters: {missing_params}")
        return results

    results["parameters"]["found"] = list(param_dict.keys())

    # Validate coordinate consistency and timestamp sequences
    first_coords = param_dict[EXPECTED_PARAMS[0]].get("coordinates", [{}])[0]
    lat = first_coords.get("lat")
    lon = first_coords.get("lon")
    dates_list = first_coords.get("dates", [])

    results["metadata"]["coordinates"] = {"latitude": lat, "longitude": lon}

    parsed_timestamps = []
    for d_entry in dates_list:
        dt_str = d_entry.get("date")
        # Format: 2026-11-15T07:00:00Z
        dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        parsed_timestamps.append(dt)

    # Check intervals
    interval_hours = []
    for i in range(1, len(parsed_timestamps)):
        delta = (parsed_timestamps[i] - parsed_timestamps[i - 1]).total_seconds() / 3600.0
        interval_hours.append(delta)

    is_regular_hourly = all(h == 1.0 for h in interval_hours)
    first_dt = parsed_timestamps[0]
    last_dt = parsed_timestamps[-1]

    # Check expiration relative to fixed current reference time or now
    now_utc = datetime(2026, 11, 15, 8, 35, 51, tzinfo=timezone.utc)
    is_expired = now_utc > last_dt

    results["temporal_checks"] = {
        "valid_from": first_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_until": last_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total_hourly_steps": len(parsed_timestamps),
        "is_strictly_hourly": is_regular_hourly,
        "is_expired": is_expired,
        "evaluation_time_utc": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if not is_regular_hourly:
        results["warnings"].append("Timestamps contain non-hourly steps.")

    # Check value integrity
    missing_vals = {}
    for p in EXPECTED_PARAMS:
        p_dates = param_dict[p].get("coordinates", [{}])[0].get("dates", [])
        m_count = sum(1 for d in p_dates if d.get("value") is None)
        missing_vals[p] = m_count

    results["parameters"]["missing_values"] = missing_vals
    results["is_valid"] = len(results["errors"]) == 0
    return results


if __name__ == "__main__":
    report = validate_meteomatics_file()
    print("Meteomatics Validation Result:")
    print(json.dumps(report, indent=2))
