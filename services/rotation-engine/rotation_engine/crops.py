"""Crop table loader (knowledge/crops.csv). Pure Python, no dependencies."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict

# Ordinal scales. The CSV keeps human-readable words; the engine uses these numbers.
WATER_LEVELS = {"very_low": 1, "low": 2, "low_medium": 3, "medium": 4,
                "medium_high": 5, "high": 6, "very_high": 7}
TOL_LEVELS = {"very_low": 1, "low": 2, "low_medium": 3, "medium": 4, "good": 5}
SEASONS = ("rabi", "kharif")
HARD_RULES = {"water", "salinity", "waterlog"}


@dataclass(frozen=True)
class Crop:
    id: str
    name_en: str
    name_ur: str
    name_sd: str
    season: str
    sow_start: int          # calendar month 1-12
    sow_end: int            # calendar month 1-12
    dur_min: int            # months
    dur_max: int            # months
    water_need: int         # 1..7
    heat_tol: int           # 1..5
    salinity_tol: int       # 1..5
    waterlog_tol: int       # 1..5
    family: str
    n_fixing: bool
    source: str
    verified: bool
    verified_by: str
    hard_constraints: frozenset[str]


def _level(table: Dict[str, int], value: str, field: str, crop_id: str) -> int:
    key = (value or "").strip().lower()
    if key not in table:
        raise ValueError(f"crops.csv: crop '{crop_id}' has invalid {field} '{value}'")
    return table[key]


def _bool(value: str, field: str, crop_id: str) -> bool:
    v = (value or "").strip().lower()
    if v not in ("true", "false"):
        raise ValueError(f"crops.csv: crop '{crop_id}' has invalid {field} '{value}'")
    return v == "true"


def _month(value: str, field: str, crop_id: str) -> int:
    m = int(value)
    if not 1 <= m <= 12:
        raise ValueError(f"crops.csv: crop '{crop_id}' {field} must be 1-12")
    return m


def load_crops(path: str) -> Dict[str, Crop]:
    """Load crops in file order. Raises ValueError on any invalid row (fail loudly)."""
    crops: Dict[str, Crop] = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cid = row["id"].strip()
            if not cid:
                raise ValueError("crops.csv: empty crop id")
            if cid in crops:
                raise ValueError(f"crops.csv: duplicate crop id '{cid}'")
            season = row["season"].strip().lower()
            if season not in SEASONS:
                raise ValueError(f"crops.csv: crop '{cid}' has invalid season '{season}'")
            c = Crop(
                id=cid,
                name_en=row["name_en"].strip(),
                name_ur=row["name_ur"].strip(),
                name_sd=row["name_sd"].strip(),
                season=season,
                sow_start=_month(row["sow_start_m"], "sow_start_m", cid),
                sow_end=_month(row["sow_end_m"], "sow_end_m", cid),
                dur_min=int(row["duration_min_m"]),
                dur_max=int(row["duration_max_m"]),
                water_need=_level(WATER_LEVELS, row["water_need"], "water_need", cid),
                heat_tol=_level(TOL_LEVELS, row["heat_tol"], "heat_tol", cid),
                salinity_tol=_level(TOL_LEVELS, row["salinity_tol"], "salinity_tol", cid),
                waterlog_tol=_level(TOL_LEVELS, row["waterlog_tol"], "waterlog_tol", cid),
                family=row["family"].strip().lower(),
                n_fixing=_bool(row["n_fixing"], "n_fixing", cid),
                source=row["source"].strip(),
                verified=_bool(row["verified"], "verified", cid),
                verified_by=row.get("verified_by", "").strip(),
                hard_constraints=frozenset(
                    rule.strip().lower()
                    for rule in (row.get("hard_constraints", "") or "").replace("|", ",").split(",")
                    if rule.strip()
                ),
            )
            if c.hard_constraints - HARD_RULES:
                raise ValueError(f"crops.csv: crop '{cid}' has unknown hard constraint")
            if c.hard_constraints and not c.verified:
                raise ValueError(f"crops.csv: crop '{cid}' cannot declare hard constraints while unverified")
            if c.sow_start > c.sow_end or c.dur_min > c.dur_max or c.dur_min < 1:
                raise ValueError(f"crops.csv: crop '{cid}' has inconsistent sowing/duration values")
            crops[cid] = c
    if not crops:
        raise ValueError("crops.csv is empty")
    return crops
