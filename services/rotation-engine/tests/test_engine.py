import os
import sys
from dataclasses import replace
from datetime import date

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rotation_engine import load_crops, recommend, upcoming_seasons  # noqa: E402
from rotation_engine import engine as eng  # noqa: E402

CSV = os.path.join(HERE, "..", "..", "..", "knowledge", "crops.csv")
CROPS = load_crops(CSV)
NOV = date(2026, 11, 15)

HEAT = {m: 0.0 for m in range(1, 13)}
HEAT.update({4: 4.0, 5: 12.0, 6: 10.0, 7: 3.0, 8: 1.0, 9: 3.0})


def feats(**kw):
    f = {"ndvi_mean": 0.55, "low_lying_flag": False, "heat_days_40c_by_month": dict(HEAT), "sources_present": 6}
    f.update(kw)
    return f


def req(**kw):
    r = {"current_crop": "cotton", "water_source": "canal", "water_amount": "medium",
         "salinity": "no", "waterlogging": "no", "priority": "balanced"}
    r.update(kw)
    return r


def seq(o):
    return tuple(s["crop"] for s in o["seasons"])


def test_crops_table_loads():
    assert len(CROPS) == 12
    assert all(not c.verified for c in CROPS.values())      # nothing verified yet
    assert CROPS["wheat"].season == "rabi" and CROPS["cotton"].season == "kharif"


def test_upcoming_seasons():
    assert upcoming_seasons(date(2026, 11, 15)) == [("rabi", "rabi_2026_27"), ("kharif", "kharif_2027")]
    assert upcoming_seasons(date(2027, 3, 1)) == [("kharif", "kharif_2027"), ("rabi", "rabi_2027_28")]
    assert upcoming_seasons(date(2026, 12, 31))[0][1] == "rabi_2026_27"


def test_three_distinct_options_in_order():
    out = recommend(CROPS, req(), feats(), NOV)
    assert out["status"] == "ok"
    ids = [o["id"] for o in out["options"]]
    assert ids == ["existing", "balanced", "priority"]
    assert len({seq(o) for o in out["options"]}) == 3


def test_existing_option_is_farmers_way():
    out = recommend(CROPS, req(current_crop="cotton"), feats(), NOV)
    ex = out["options"][0]
    assert seq(ex) == ("wheat", "cotton")
    assert [s["season"] for s in ex["seasons"]] == ["rabi_2026_27", "kharif_2027"]


def test_recommended_options_never_violate_hard_rules():
    out = recommend(CROPS, req(), feats(), NOV)
    for o in out["options"][1:]:
        assert o["light"] in ("green", "yellow")


def test_wheat_after_wheat_is_rejected_red_warning():
    out = recommend(CROPS, req(current_crop="wheat"), feats(), NOV)
    ex = out["options"][0]
    assert seq(ex)[0] == "wheat"
    assert ex["light"] == "red"
    assert "caution_rule_repeat_001" in ex["caution_ids"]
    for o in out["options"][1:]:
        assert seq(o)[0] != "wheat"


def test_low_water_applies_soft_penalty_to_unverified_rules():
    out = recommend(CROPS, req(water_amount="low", water_source="canal"), feats(), NOV)
    assert out["status"] == "ok"
    ctx = eng.Ctx(crops=CROPS, current=CROPS["cotton"], water_source="canal", water_amount="low",
                  salinity="no", waterlogging="no", priority="balanced", low_lying=False,
                  ndvi=0.5, heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    assert eng._unverified_rule_penalty(CROPS["rice"], ctx) > 0
    assert all("Agronomic value requires local verification." in o["warnings"] for o in out["options"])


def test_rain_fed_is_more_restrictive_than_canal():
    canal = recommend(CROPS, req(water_amount="low", water_source="canal"), feats(), NOV)
    rain = recommend(CROPS, req(water_amount="low", water_source="rain"), feats(), NOV)
    for o in rain["options"][1:]:
        for crop in seq(o):
            assert CROPS[crop].water_need <= 3
    assert canal["status"] == "ok"


def test_salinity_unverified_rule_warns_without_hard_rejection():
    out = recommend(CROPS, req(salinity="yes"), feats(), NOV)
    assert out["status"] == "ok"
    assert all("caution_rule_salt_001" not in o["caution_ids"] or o["warnings"] for o in out["options"])
    ctx = eng.Ctx(crops=CROPS, current=CROPS["cotton"], water_source="canal", water_amount="medium",
                  salinity="yes", waterlogging="no", priority="balanced", low_lying=False,
                  ndvi=0.5, heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    assert eng._unverified_rule_penalty(CROPS["chickpea"], ctx) > 0


def test_waterlogging_or_low_lying_unverified_rules_are_soft():
    for out in (recommend(CROPS, req(waterlogging="yes"), feats(), NOV),
                recommend(CROPS, req(), feats(low_lying_flag=True), NOV)):
        assert out["status"] == "ok"
        assert all(any(o["warning_ids"]) for o in out["options"])


def test_waterlogging_unverified_does_not_hard_reject():
    out = recommend(CROPS, req(waterlogging="yes"), feats(), NOV)
    assert out["status"] == "ok"
    assert all(o["expert_needed"] and o["warnings"] for o in out["options"])


def test_only_verified_explicit_hard_rule_can_reject():
    ctx = eng.Ctx(crops=CROPS, current=CROPS["cotton"], water_source="canal", water_amount="low",
                  salinity="no", waterlogging="no", priority="balanced", low_lying=False,
                  ndvi=0.5, heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    unverified = replace(CROPS["wheat"], water_need=7, hard_constraints=frozenset({"water"}))
    assert "water" not in eng.hard_violations(unverified, CROPS["mung_bean"], ctx)
    verified = replace(unverified, verified=True)
    assert "water" in eng.hard_violations(verified, CROPS["mung_bean"], ctx)


def test_overlap_rule():
    ctx = eng.Ctx(crops=CROPS, current=CROPS["cotton"], water_source="canal", water_amount="high",
                  salinity="no", waterlogging="no", priority="balanced", low_lying=False, ndvi=0.5,
                  heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    # berseem (sow Oct-Nov, 5-6 months) then mung (Jul) is fine; fabricate an impossible one:
    fake = CROPS["wheat"].__class__(**{**CROPS["wheat"].__dict__, "id": "slow", "dur_min": 9, "dur_max": 9})
    assert "overlap" in eng.hard_violations(fake, CROPS["mung_bean"], ctx)
    assert "overlap" not in eng.hard_violations(CROPS["wheat"], CROPS["mung_bean"], ctx)


def test_season_mismatch_rule():
    ctx = eng.Ctx(crops=CROPS, current=CROPS["cotton"], water_source="canal", water_amount="high",
                  salinity="no", waterlogging="no", priority="balanced", low_lying=False, ndvi=0.5,
                  heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    assert "season" in eng.hard_violations(CROPS["cotton"], CROPS["wheat"], ctx)


def test_priority_changes_ranking():
    water = recommend(CROPS, req(priority="save_water", water_amount="high"), feats(), NOV)["options"][2]
    soil = recommend(CROPS, req(priority="improve_soil", water_amount="high"), feats(), NOV)["options"][2]
    def wsum(o):
        return sum(CROPS[c].water_need for c in seq(o))
    assert wsum(water) <= wsum(soil)
    assert seq(water) != seq(soil) or water["score"] != soil["score"]


def test_save_water_priority_prefers_light_crops():
    out = recommend(CROPS, req(priority="save_water", water_amount="high"), feats(), NOV)
    assert out["options"][2]["water_drops"] == 1


def test_legume_gets_bonus_and_reason():
    out = recommend(CROPS, req(priority="improve_soil", water_amount="high"), feats(), NOV)
    opt = out["options"][2]
    assert any(CROPS[c].n_fixing for c in seq(opt))
    assert "why_legume_001" in opt["why_ids"]


def test_rice_then_wheat_is_not_rejected():
    ctx = eng.Ctx(crops=CROPS, current=CROPS["rice"], water_source="canal", water_amount="high",
                  salinity="no", waterlogging="no", priority="balanced", low_lying=False, ndvi=0.5,
                  heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    assert eng.hard_violations(CROPS["wheat"], CROPS["rice"], ctx) == []   # wheat -> rice allowed
    # rice (kharif) -> wheat (rabi) in a kharif-first window
    ctx2 = eng.Ctx(**{**ctx.__dict__, "current": CROPS["cotton"], "slots": upcoming_seasons(date(2027, 5, 1))})
    assert eng.hard_violations(CROPS["rice"], CROPS["wheat"], ctx2) == []


def test_weak_field_flags_expert_and_boosts_legume():
    weak = recommend(CROPS, req(), feats(ndvi_mean=0.2), NOV)
    assert weak["field_health"] == {"light": "red", "template_id": "health_poor_001"}
    good = recommend(CROPS, req(), feats(ndvi_mean=0.6), NOV)
    assert good["field_health"]["light"] == "green"
    ok = recommend(CROPS, req(), feats(ndvi_mean=0.4), NOV)
    assert ok["field_health"]["template_id"] == "health_moderate_001"


def test_confidence_dots_rules():
    base = recommend(CROPS, req(), feats(sources_present=6), NOV)["options"][1]["confidence_dots"]
    assert base == 2  # every crop rule in this table is unverified
    assert eng.confidence_dots(eng.Ctx(crops=CROPS, current=CROPS["cotton"], water_source="canal",
        water_amount="medium", salinity="no", waterlogging="no", priority="balanced", low_lying=False,
        ndvi=0.5, heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))) == 3
    assert recommend(CROPS, req(), feats(sources_present=3), NOV)["options"][1]["confidence_dots"] == 1
    both_unknown = recommend(CROPS, req(salinity="unknown", waterlogging="unknown"),
                             feats(sources_present=6), NOV)["options"][1]["confidence_dots"]
    assert both_unknown == 2


def test_unverified_crops_always_need_expert():
    out = recommend(CROPS, req(), feats(), NOV)
    for o in out["options"]:
        assert o["crop_verified"] is False
        assert o["expert_needed"] is True


def test_heat_exposure_lowers_heat_sensitive_crops():
    hot = dict(HEAT)
    hot.update({3: 20.0, 4: 25.0, 5: 28.0})       # very hot spring
    cool = {m: 0.0 for m in range(1, 13)}
    a = recommend(CROPS, req(priority="balanced"), feats(heat_days_40c_by_month=hot), NOV)
    b = recommend(CROPS, req(priority="balanced"), feats(heat_days_40c_by_month=cool), NOV)
    ea = [o for o in a["options"] if o["id"] == "existing"][0]
    eb = [o for o in b["options"] if o["id"] == "existing"][0]
    assert ea["score"] <= eb["score"]


def test_why_and_caution_limits_and_shape():
    out = recommend(CROPS, req(salinity="unknown", waterlogging="unknown"), feats(), NOV)
    for o in out["options"]:
        assert len(o["why_ids"]) <= 2
        assert len(o["caution_ids"]) <= (2 if o["light"] == "red" else 1)
        assert 1 <= o["water_drops"] <= 3 and 0 <= o["score"] <= 100
        assert o["confidence_dots"] in (1, 2, 3)
    assert set(o) == {"id", "seasons", "light", "water_drops", "score", "confidence_dots",
                      "why_ids", "caution_ids", "expert_needed", "crop_verified", "warnings", "warning_ids"}


def test_deterministic():
    a = recommend(CROPS, req(), feats(), NOV)
    b = recommend(CROPS, req(), feats(), NOV)
    assert a == b


def test_kharif_first_window():
    out = recommend(CROPS, req(current_crop="wheat"), feats(), date(2027, 4, 1))
    assert out["status"] == "ok"
    for o in out["options"]:
        assert [s["season"] for s in o["seasons"]] == ["kharif_2027", "rabi_2027_28"]


def test_bad_inputs_raise():
    with pytest.raises(ValueError):
        recommend(CROPS, req(current_crop="nope"), feats(), NOV)
    with pytest.raises(ValueError):
        recommend(CROPS, req(), {"ndvi_mean": 0.5}, NOV)
    bad = dict(HEAT)
    del bad[3]
    with pytest.raises(ValueError):
        recommend(CROPS, req(), feats(heat_days_40c_by_month=bad), NOV)
