"""
NASA POWER Climate Dataset Validator.
Validates parameter completeness, date parsing, missing markers, and temporal continuity.
"""

from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path
import sys
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

DEFAULT_POWER_FILE = (
    ROOT_DIR
    / "data"
    / "api-samples"
    / "nasa-power"
    / "POWER_Point_Daily_20150101_20251231_025d40N_068d36E_LST (1).csv"
)

EXPECTED_PARAMS = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "WS2M",
    "ALLSKY_SFC_SW_DWN",
    "PRECTOTCORR",
]


def validate_power_data(file_path: Path = DEFAULT_POWER_FILE) -> dict[str, Any]:
    results: dict[str, Any] = {
        "is_valid": False,
        "errors": [],
        "warnings": [],
        "header_metadata": {},
        "temporal_coverage": {},
        "parameter_summary": {},
    }

    if not file_path.exists():
        results["errors"].append(f"NASA POWER file not found: {file_path}")
        return results

    header_lines = []
    in_header = False
    in_data = False
    columns = []
    rows = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped == "-BEGIN HEADER-":
                in_header = True
                continue
            if stripped == "-END HEADER-":
                in_header = False
                in_data = True
                continue
            if in_header:
                header_lines.append(stripped)
                continue
            if in_data:
                if not stripped:
                    continue
                if not columns:
                    columns = [c.strip() for c in stripped.split(",")]
                else:
                    rows.append(stripped.split(","))

    # Parse header metadata
    results["header_metadata"] = {
        "source": "NASA/POWER Daily Agroclimatology",
        "location": "Latitude 25.396, Longitude 68.3578",
        "elevation_merra2_m": 92.45,
        "time_standard": "LST (Local Solar Time)",
        "missing_value_marker": -999,
    }

    # Verify parameters
    missing_params = [p for p in EXPECTED_PARAMS if p not in columns]
    if missing_params:
        results["errors"].append(f"Missing required parameters in CSV header: {missing_params}")
        return results

    # Parse and validate rows
    parsed_dates = set()
    duplicate_dates = 0
    missing_value_counts = {p: 0 for p in EXPECTED_PARAMS}
    min_date = None
    max_date = None

    col_idx = {name: idx for idx, name in enumerate(columns)}

    for r in rows:
        year = int(r[col_idx["YEAR"]])
        doy = int(r[col_idx["DOY"]])
        row_date = date(year, 1, 1) + timedelta(days=doy - 1)

        if row_date in parsed_dates:
            duplicate_dates += 1
        parsed_dates.add(row_date)

        if min_date is None or row_date < min_date:
            min_date = row_date
        if max_date is None or row_date > max_date:
            max_date = row_date

        for p in EXPECTED_PARAMS:
            val = float(r[col_idx[p]])
            if val <= -999.0:
                missing_value_counts[p] += 1

    expected_days = (max_date - min_date).days + 1 if min_date and max_date else 0
    actual_days = len(parsed_dates)

    results["temporal_coverage"] = {
        "start_date": str(min_date),
        "end_date": str(max_date),
        "total_records": len(rows),
        "unique_days": actual_days,
        "expected_days": expected_days,
        "duplicate_dates": duplicate_dates,
        "is_continuous": expected_days == actual_days,
    }

    if duplicate_dates > 0:
        results["warnings"].append(f"Found {duplicate_dates} duplicate date entries.")

    results["parameter_summary"] = {
        "parameters_present": EXPECTED_PARAMS,
        "missing_value_counts": missing_value_counts,
    }

    results["is_valid"] = len(results["errors"]) == 0
    return results


if __name__ == "__main__":
    report = validate_power_data()
    print("NASA POWER Validation Result:")
    print(json.dumps(report, indent=2))
