import json
from datetime import date

import pytest

from app.config import Settings, get_settings
from app.features import FeatureStore
from app import service
from app.schemas import AnalyzeRequest

ROOT = get_settings().root
NOV = date(2026, 11, 15)
HEAT = {str(m): 0 for m in range(1, 13)}
HEAT.update({"4": 4, "5": 12, "6": 10, "7": 3, "9": 3})


def point_features(**over):
    f = {"ndvi_mean": 0.45, "ndmi_mean": 0.1, "bsi_mean": 0.05, "surface_temp_c": 35, "cloud_free_fraction": 0.9,
         "elevation_m": 28, "slope_deg": 0.3, "low_lying_flag": False,
         "heat_days_40c_by_month": dict(HEAT), "rh_mean": 50, "wind_mean": 3,
         "smap_surface_mean": 0.21, "gpm_total_mm": 18.2}
    f.update(over)
    return {k: v for k, v in f.items() if v is not None}


def make_deps(tmp_path, features=None, weather=None, power=None, points=True):
    fp = tmp_path / "features.json"
    if points:
        fp.write_text(json.dumps({"meta": {"satellite_window": "2025-09-01/2025-09-30", "landsat_date": "2025-09-22"},
                                  "points": [{"id": "p1", "lat": 25.39, "lon": 68.37,
                                              "features": features if features is not None else point_features()}]}))
    settings = Settings(root=ROOT, demo_mode=False, features_path=fp,
                        features_example_path=ROOT / "data" / "features" / "features.example.json",
                        crops_csv=ROOT / "knowledge" / "crops.csv",
                        samples_dir=tmp_path, cache_dir=tmp_path, layers_dir=tmp_path, web_dir=tmp_path,
                        meteomatics_user="", meteomatics_password="", cors_origins=["*"],
                        power_csv_path=None, meteomatics_sample_path=None)
    d = service.build_deps(settings)
    d.weather_fn = weather or (lambda lat, lon: {"available": True, "source": "meteomatics", "is_sample": False, "days": []})
    d.power_fn = power or (lambda lat, lon: None)
    d.regional_context_fn = lambda: {"available": False, "status": "unavailable", "regional_context": {}}
    return d


def req(**kw):
    base = dict(lat=25.39, lon=68.37, radius_m=150, current_crop="cotton", previous_crop="unknown",
                water_source="canal", water_amount="medium", salinity="no", waterlogging="no",
                priority="balanced", language="sd")
    base.update(kw)
    return AnalyzeRequest(**base)


def test_ok_response_matches_contract(tmp_path):
    out = service.analyze(req(), make_deps(tmp_path), NOV)
    assert out["status"] == "ok"
    assert out["data_snapshot"] == {"satellite_window": "2025-09-01/2025-09-30", "landsat_date": "2025-09-22"}
    assert out["field_health"]["template_id"].startswith("health_")
    assert out["forecast"]["available"] is True
    assert out["forecast"]["is_live"] is False and out["forecast"]["is_sample"] is False
    assert out["analysis_method"] == "nearest_available_point"
    assert out["disclaimer_id"] == "disclaimer_001"
    assert [o["id"] for o in out["options"]] == ["existing", "balanced", "priority"]
    assert out["regional_context"] == {}  # test feature values never impersonate validated regional context
    assert out["regional_context_status"] == "unavailable"
    json.dumps(out)                      # must be JSON serialisable


def test_unverified_crop_rules_cap_confidence_at_two_dots(tmp_path):
    out = service.analyze(req(), make_deps(tmp_path), NOV)
    assert out["options"][1]["confidence_dots"] <= 2
    assert out["options"][1]["confidence_score"] < 80


def test_no_forecast_loses_a_dot(tmp_path):
    d = make_deps(tmp_path, weather=lambda a, b: {"available": False, "source": "meteomatics", "is_sample": False})
    out = service.analyze(req(), d, NOV)
    assert out["forecast"]["available"] is False
    assert out["options"][1]["confidence_dots"] <= 2


def test_sugarcane_and_banana_not_applicable(tmp_path):
    d = make_deps(tmp_path)
    assert service.analyze(req(current_crop="sugarcane"), d, NOV)["reason_id"] == "special_long"
    assert service.analyze(req(current_crop="banana"), d, NOV)["reason_id"] == "special_perm"


def test_out_of_area_pin(tmp_path):
    out = service.analyze(req(lat=24.86, lon=67.01), make_deps(tmp_path), NOV)     # Karachi
    assert out["status"] == "not_applicable" and out["reason_id"] == "out_of_area"


def test_no_features_file_is_insufficient(tmp_path):
    d = make_deps(tmp_path, points=False)
    out = service.analyze(req(), d, NOV)
    assert out["status"] == "insufficient_data" and out["reason_id"] == "no_data_001"


def test_real_mode_does_not_fall_back_to_example_features(monkeypatch):
    monkeypatch.setenv("AGRISHIFT_ROOT", str(ROOT))
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.delenv("FEATURES_FILE", raising=False)
    monkeypatch.delenv("FEATURES_PATH", raising=False)
    settings = get_settings()
    assert settings.features_path == ROOT / "data" / "features" / "features.json"
    assert not FeatureStore(settings.features_path).available()
    assert FeatureStore(settings.features_example_path).available()


def test_demo_mode_explicitly_selects_example_features(monkeypatch):
    monkeypatch.setenv("AGRISHIFT_ROOT", str(ROOT))
    monkeypatch.setenv("DEMO_MODE", "true")
    monkeypatch.delenv("FEATURES_FILE", raising=False)
    monkeypatch.delenv("FEATURES_PATH", raising=False)
    settings = get_settings()
    assert settings.demo_mode is True
    assert settings.features_path == settings.features_example_path


def test_production_rejects_wildcard_cors(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ORIGINS", "*")
    with pytest.raises(ValueError, match="must not contain"):
        get_settings()


def test_pin_far_from_any_point_is_insufficient(tmp_path):
    out = service.analyze(req(lat=25.60, lon=68.60), make_deps(tmp_path), NOV)     # inside box, >5 km from point
    assert out["status"] == "insufficient_data" and out["reason_id"] == "no_data_001"


@pytest.mark.parametrize("missing", ["ndvi_mean", "low_lying_flag", "heat_days_40c_by_month"])
def test_missing_core_data_is_insufficient(tmp_path, missing):
    d = make_deps(tmp_path, features=point_features(**{missing: None}))
    out = service.analyze(req(), d, NOV)
    assert out["status"] == "insufficient_data" and out["reason_id"] == "no_data_001"


def test_cloudy_landsat_is_treated_as_missing(tmp_path):
    d = make_deps(tmp_path, features=point_features(cloud_free_fraction=0.2))
    assert service.analyze(req(), d, NOV)["reason_id"] == "no_data_001"


def test_incomplete_heat_months_are_not_guessed(tmp_path):
    bad = dict(HEAT)
    del bad["2"]
    d = make_deps(tmp_path, features=point_features(heat_days_40c_by_month=bad))
    assert service.analyze(req(), d, NOV)["reason_id"] == "no_data_001"


def test_power_fallback_fills_climate(tmp_path):
    fb = {"heat_days_40c_by_month": {m: 0.0 for m in range(1, 13)}, "rh_mean": 40.0}
    d = make_deps(tmp_path, features=point_features(heat_days_40c_by_month=None), power=lambda a, b: fb)
    assert service.analyze(req(), d, NOV)["status"] == "ok"


def test_smap_gpm_missing_still_ok_but_fewer_dots(tmp_path):
    d = make_deps(tmp_path, features=point_features(smap_surface_mean=None, gpm_total_mm=None))
    out = service.analyze(req(), d, NOV)
    assert out["status"] == "ok"
    assert out["regional_context"] == {}
    assert out["options"][1]["confidence_dots"] <= 2
