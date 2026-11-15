"""Rule-based rotation engine (MVP, NO machine learning).

Plan reference: section 5. Everything here is explainable rules. All numeric
thresholds below are STARTING POINTS (unverified) and must be reviewed by an
agronomist before being treated as final.

Scoring (0-100):
    score = 100 * (w1*paani_fit + w2*zameen_fit + w3*mausam_fit + w4*rotation_faida) - penalties
Heat (POWER) is expressed through mausam_fit; penalties are: late sowing, same family twice.
SMAP / GPM / Meteomatics are NOT used in scoring.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

from .crops import Crop

# ---------------------------------------------------------------- configuration
WEIGHTS = {  # (paani, zameen, mausam, rotation_faida) - plan section 5.4
    "save_water": (0.45, 0.15, 0.20, 0.20),
    "improve_soil": (0.15, 0.35, 0.15, 0.35),
    "balanced": (0.30, 0.25, 0.20, 0.25),
    # third card when the farmer chose "balanced": average of save_water and improve_soil
    "save_water_soil": (0.30, 0.25, 0.175, 0.275),
}
AVAIL_LEVEL = {"low": 3, "medium": 5, "high": 7}   # water the farmer has, same 1..7 scale as crop need
RAIN_FED_LEVEL_DROP = 1                             # rain-fed water is less reliable
NDVI_WEAK = 0.30                                    # unverified
NDVI_GOOD = 0.50                                    # unverified
HEAT_DAYS_FULL_RISK = 15.0                          # heat days (>=40C) in crop months that mean "full" risk; unverified
HEAT_TOL_SCALE = {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.6, 5: 1.0}
HEAT_CAUTION_LEVEL = 0.30
PENALTY_LATE_SOWING = 4.0
PENALTY_SAME_FAMILY = 3.0
PENALTY_UNVERIFIED_RULE = 2.0               # uncalibrated warning-only penalty; agronomist review required
GREEN_MIN_SCORE = 70
TOTAL_SOURCES = 6                                   # landsat, srtm, power, smap, gpm, forecast
PARTNER = {"rabi": "wheat", "kharif": "cotton"}     # customary crop in the other season (for the "your way" card)

RULE_CAUTION = {
    "repeat": "caution_rule_repeat_001",
    "water": "caution_rule_water_001",
    "salinity": "caution_rule_salt_001",
    "waterlog": "caution_rule_waterlog_001",
    "overlap": "caution_rule_overlap_001",
}


# ---------------------------------------------------------------- seasons
def upcoming_seasons(today: date) -> List[Tuple[str, str]]:
    """Next two growing seasons as [(type, code), (type, code)].

    Sep-Dec -> rabi (this year/next) then kharif (next year)
    Jan-Aug -> kharif (this year) then rabi (this year/next)
    """
    y = today.year
    if today.month >= 9:
        return [("rabi", f"rabi_{y}_{(y + 1) % 100:02d}"), ("kharif", f"kharif_{y + 1}")]
    return [("kharif", f"kharif_{y}"), ("rabi", f"rabi_{y}_{(y + 1) % 100:02d}")]


# ---------------------------------------------------------------- context
@dataclass
class Ctx:
    crops: Dict[str, Crop]
    current: Crop
    water_source: str
    water_amount: str
    salinity: str
    waterlogging: str
    priority: str
    low_lying: bool
    ndvi: float
    heat_days: Dict[int, float]
    sources_present: int
    slots: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def weak(self) -> bool:
        return self.ndvi < NDVI_WEAK

    @property
    def avail(self) -> int:
        a = AVAIL_LEVEL[self.water_amount]
        if self.water_source == "rain":
            a = max(1, a - RAIN_FED_LEVEL_DROP)
        return a


# ---------------------------------------------------------------- timing helpers
def _sow_window(c: Crop, first: Optional[Crop]) -> Tuple[int, int]:
    """Sowing window on one continuous month axis. The second crop is shifted by 12 if it falls in the next calendar year."""
    if first is None:
        return c.sow_start, c.sow_end
    shift = 12 if c.sow_start <= first.sow_end else 0
    return c.sow_start + shift, c.sow_end + shift


def _heat_risk(c: Crop, ctx: Ctx) -> float:
    months = [((c.sow_start - 1 + i) % 12) + 1 for i in range(c.dur_min)]
    days = sum(ctx.heat_days.get(m, 0.0) for m in months)
    return min(1.0, days / HEAT_DAYS_FULL_RISK)


def _heat_exposure(c: Crop, ctx: Ctx) -> float:
    """risk * (1 - tolerance scale): 0 = no problem, 1 = worst."""
    return _heat_risk(c, ctx) * (1.0 - HEAT_TOL_SCALE[c.heat_tol])


# ---------------------------------------------------------------- hard rules (section 5.2)
def hard_violations(c1: Crop, c2: Crop, ctx: Ctx) -> List[str]:
    v: List[str] = []
    if c1.season != ctx.slots[0][0] or c2.season != ctx.slots[1][0]:
        v.append("season")
    if c1.id == c2.id or c1.id == ctx.current.id:
        v.append("repeat")
    if any(c.verified and "water" in c.hard_constraints and c.water_need > ctx.avail + 1 for c in (c1, c2)):
        v.append("water")
    if ctx.salinity == "yes" and any(c.verified and "salinity" in c.hard_constraints and c.salinity_tol <= 2 for c in (c1, c2)):
        v.append("salinity")
    if (ctx.waterlogging == "yes" or ctx.low_lying) and any(c.verified and "waterlog" in c.hard_constraints and c.waterlog_tol <= 2 for c in (c1, c2)):
        v.append("waterlog")
    earliest_harvest = c1.sow_start + c1.dur_min
    _, second_sow_end = _sow_window(c2, c1)
    if earliest_harvest > second_sow_end:
        v.append("overlap")
    return v


# ---------------------------------------------------------------- scoring (section 5.4)
def _paani_fit(c: Crop, ctx: Ctx) -> float:
    if c.water_need <= ctx.avail:
        avail_fit = 1.0
    elif c.water_need == ctx.avail + 1:
        avail_fit = 0.5
    else:
        avail_fit = 0.0
    thrift = 1.0 - (c.water_need - 1) / 6.0
    return 0.5 * avail_fit + 0.5 * thrift


def _tol_fit(tol: int) -> float:
    return (tol - 1) / 4.0


def _zameen_fit(c: Crop, ctx: Ctx) -> float:
    if ctx.salinity == "yes":
        sal = _tol_fit(c.salinity_tol)
    elif ctx.salinity == "no":
        sal = 1.0
    else:
        sal = 0.5 + 0.5 * _tol_fit(c.salinity_tol)
    if ctx.waterlogging == "yes" or ctx.low_lying:
        wl = _tol_fit(c.waterlog_tol)
    elif ctx.waterlogging == "no":
        wl = 1.0
    else:
        wl = 0.5 + 0.5 * _tol_fit(c.waterlog_tol)
    fit = (sal + wl) / 2.0
    if ctx.weak and c.n_fixing:          # weak field -> soil-health crops get a bonus
        fit = min(1.0, fit + 0.10)
    return fit


def _mausam_fit(c: Crop, ctx: Ctx) -> float:
    return 1.0 - _heat_exposure(c, ctx)


def _rotation_faida(c: Crop, prev: Crop) -> float:
    if c.n_fixing and prev.family != "legume":
        return 1.0                        # nitrogen-fixing crop after a non-legume
    if c.family == prev.family:
        return 0.4
    return 0.7


def _mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs)


def _unverified_rule_penalty(c: Crop, ctx: Ctx) -> float:
    """Apply a small, explicitly uncalibrated ranking penalty to unverified risk rules."""
    risks = {
        "water": c.water_need > ctx.avail,
        "salinity": ctx.salinity == "yes" and c.salinity_tol <= 2,
        "waterlog": (ctx.waterlogging == "yes" or ctx.low_lying) and c.waterlog_tol <= 2,
    }
    soft_risks = sum(
        risk and not (c.verified and rule in c.hard_constraints)
        for rule, risk in risks.items()
    )
    return PENALTY_UNVERIFIED_RULE * soft_risks


def score_sequence(c1: Crop, c2: Crop, ctx: Ctx, wkey: str) -> Tuple[float, bool]:
    """Returns (score 0..100, late_sowing_flag)."""
    w1, w2, w3, w4 = WEIGHTS[wkey]
    paani = _mean(_paani_fit(c, ctx) for c in (c1, c2))
    zameen = _mean(_zameen_fit(c, ctx) for c in (c1, c2))
    mausam = _mean(_mausam_fit(c, ctx) for c in (c1, c2))
    rot = _mean([_rotation_faida(c1, ctx.current), _rotation_faida(c2, c1)])
    penalties = 0.0
    for c, prev in ((c1, ctx.current), (c2, c1)):
        if c.family == prev.family:
            penalties += PENALTY_SAME_FAMILY
    latest_harvest = c1.sow_end + c1.dur_max
    second_sow_start, _ = _sow_window(c2, c1)
    late = latest_harvest > second_sow_start
    if late:
        penalties += PENALTY_LATE_SOWING
    penalties += sum(_unverified_rule_penalty(c, ctx) for c in (c1, c2))
    total = 100.0 * (w1 * paani + w2 * zameen + w3 * mausam + w4 * rot) - penalties
    return max(0.0, min(100.0, total)), late


# ---------------------------------------------------------------- confidence (section 5.5)
def confidence_dots(ctx: Ctx) -> int:
    missing = TOTAL_SOURCES - ctx.sources_present
    dots = 3
    if missing >= 3:
        dots -= 2
    elif missing >= 1:
        dots -= 1
    unknown = sum(1 for x in (ctx.salinity, ctx.waterlogging) if x == "unknown")
    if unknown >= 2:
        dots -= 1
    return max(1, min(3, dots))


# ---------------------------------------------------------------- explanation templates (section 5.6)
def _explain(c1: Crop, c2: Crop, ctx: Ctx, violations: List[str], late: bool,
             is_existing: bool) -> Tuple[List[str], List[str]]:
    crops = (c1, c2)
    water_ok = all(c.water_need <= ctx.avail for c in crops)
    max_need = max(c.water_need for c in crops)
    legume = any(c.n_fixing and prev.family != "legume" for c, prev in ((c1, ctx.current), (c2, c1)))
    exposed = [c for c in crops if _heat_risk(c, ctx) >= HEAT_CAUTION_LEVEL]
    heat_ok = bool(exposed) and all(c.heat_tol == 5 for c in exposed)
    facts = {
        "why_known_crop_002": ctx.current.id in (c1.id, c2.id),
        "why_water_ok_001": water_ok,
        "why_water_save_001": max_need <= 3,
        "why_legume_001": legume,
        "why_soil_help_001": legume and ctx.weak,
        "why_heat_ok_001": heat_ok,
    }
    order_existing = ["why_known_crop_002", "why_water_ok_001", "why_heat_ok_001"]
    order_other = ["why_water_save_001", "why_legume_001", "why_soil_help_001", "why_heat_ok_001", "why_water_ok_001"]
    order = order_existing if is_existing else order_other
    if violations:
        order = ["why_known_crop_002"]   # a red card only states that this is what the farmer does
    why = [k for k in order if facts[k]][:2]

    cautions: List[str] = []
    for rule in violations:
        cid = RULE_CAUTION.get(rule)
        if cid:
            cautions.append(cid)
    if not violations:
        if ctx.waterlogging == "unknown" and any(c.waterlog_tol <= 2 for c in crops):
            cautions.append("caution_waterlog_001")
        if late:
            cautions.append("caution_late_sowing_001")
        if any(_heat_exposure(c, ctx) >= HEAT_CAUTION_LEVEL for c in crops):
            cautions.append("caution_heat_001")
    cap = 2 if violations else 1
    return why, cautions[:cap]


# ---------------------------------------------------------------- option builder
def _option(opt_id: str, c1: Crop, c2: Crop, ctx: Ctx, wkey: str, dots: int, is_existing: bool) -> dict:
    violations = hard_violations(c1, c2, ctx)
    score, late = score_sequence(c1, c2, ctx, wkey)
    if violations:
        light = "red"
    else:
        light = "green" if score >= GREEN_MIN_SCORE else "yellow"
    need = max(c1.water_need, c2.water_need)
    drops = 1 if need <= 3 else (2 if need <= 5 else 3)
    why, cautions = _explain(c1, c2, ctx, violations, late, is_existing)
    verified = c1.verified and c2.verified
    option_dots = min(dots, 2) if not verified else dots
    warnings = [] if verified else ["Agronomic value requires local verification."]
    warning_ids = [] if verified else ["warning_unverified_001"]
    return {
        "id": opt_id,
        "seasons": [
            {"season": ctx.slots[0][1], "crop": c1.id},
            {"season": ctx.slots[1][1], "crop": c2.id},
        ],
        "light": light,
        "water_drops": drops,
        "score": int(round(score)),
        "confidence_dots": option_dots,
        "why_ids": why,
        "caution_ids": cautions,
        "expert_needed": (not verified) or option_dots <= 1 or light == "red",
        "crop_verified": verified,
        "warnings": warnings,
        "warning_ids": warning_ids,
    }


def _field_health(ndvi: float) -> dict:
    if ndvi >= NDVI_GOOD:
        return {"light": "green", "template_id": "health_good_001"}
    if ndvi >= NDVI_WEAK:
        return {"light": "yellow", "template_id": "health_moderate_001"}
    return {"light": "red", "template_id": "health_poor_001"}


# ---------------------------------------------------------------- public entry point
def recommend(crops: Dict[str, Crop], request: dict, features: dict, today: Optional[date] = None) -> dict:
    """Build the 3 options.

    request keys: current_crop, water_source, water_amount, salinity, waterlogging, priority
    features keys (all REQUIRED, caller must check first):
        ndvi_mean (float), low_lying_flag (bool), heat_days_40c_by_month ({1..12: float}),
        sources_present (int, 0..6)
    Returns {"status": "ok", "field_health":..., "options": [...]} or
            {"status": "insufficient_data", "reason_id": ..., "field_health":...}
    """
    today = today or date.today()
    current = crops.get(request["current_crop"])
    if current is None:
        raise ValueError(f"unknown current_crop '{request['current_crop']}'")

    ndvi = features.get("ndvi_mean")
    low_lying = features.get("low_lying_flag")
    heat_days = features.get("heat_days_40c_by_month")
    if not isinstance(ndvi, (int, float)) or isinstance(low_lying, bool) is False \
            or not isinstance(heat_days, dict) or set(heat_days) != set(range(1, 13)):
        raise ValueError("features missing or malformed (ndvi_mean, low_lying_flag, heat_days_40c_by_month)")

    ctx = Ctx(
        crops=crops, current=current,
        water_source=request["water_source"], water_amount=request["water_amount"],
        salinity=request["salinity"], waterlogging=request["waterlogging"],
        priority=request["priority"],
        low_lying=bool(low_lying), ndvi=float(ndvi), heat_days={int(k): float(v) for k, v in heat_days.items()},
        sources_present=int(features.get("sources_present", 0)),
        slots=upcoming_seasons(today),
    )
    health = _field_health(ctx.ndvi)
    dots = confidence_dots(ctx)

    firsts = [c for c in crops.values() if c.season == ctx.slots[0][0]]
    seconds = [c for c in crops.values() if c.season == ctx.slots[1][0]]

    # --- card 1: the farmer's own way (may be red = warning, never a recommendation)
    def slot_crop(slot_type: str) -> Crop:
        if current.season == slot_type:
            return current
        return crops[PARTNER[slot_type]]
    existing_pair = (slot_crop(ctx.slots[0][0]), slot_crop(ctx.slots[1][0]))

    # --- all rule-valid sequences
    valid = [(a, b) for a in firsts for b in seconds if not hard_violations(a, b, ctx)]

    def ranked(wkey: str, exclude: set):
        pool = [p for p in valid if (p[0].id, p[1].id) not in exclude]
        return sorted(pool, key=lambda p: (-score_sequence(p[0], p[1], ctx, wkey)[0], p[0].id, p[1].id))

    if not valid:
        return {"status": "insufficient_data", "reason_id": "no_safe_option_001", "field_health": health}

    options = []
    used = {(existing_pair[0].id, existing_pair[1].id)}
    options.append(_option("existing", existing_pair[0], existing_pair[1], ctx, ctx.priority, dots, True))

    bal = ranked("balanced", used)
    if bal:
        p = bal[0]
        options.append(_option("balanced", p[0], p[1], ctx, "balanced", dots, False))
        used.add((p[0].id, p[1].id))

    third_key = ctx.priority if ctx.priority != "balanced" else "save_water_soil"
    third = ranked(third_key, used)
    if third:
        p = third[0]
        options.append(_option("priority", p[0], p[1], ctx, third_key, dots, False))

    if len(options) != 3 or len({tuple((s["crop"] for s in option["seasons"])) for option in options}) != 3:
        return {"status": "insufficient_data", "reason_id": "three_distinct_options_unavailable_001",
                "field_health": health}

    return {"status": "ok", "field_health": health, "options": options}
