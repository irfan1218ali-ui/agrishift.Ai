import json
from datetime import datetime, timezone

from app import power, weather
from app.features import FeatureStore, haversine_km, normalize


# ---------------------------------------------------------------- POWER
def daily_fixture(years=(2023, 2024)):
    tmax, rain, rh, ws = {}, {}, {}, {}
    for y in years:
        for m in range(1, 13):
            for d in (1, 2, 3, 4):
                key = f"{y}{m:02d}{d:02d}"
                tmax[key] = 41.0 if (m == 5 and d <= 2) else 30.0     # 2 hot days every May
                rain[key] = 1.0
                rh[key] = 50.0
                ws[key] = 2.0
    tmax["20230601"] = -999.0                                          # fill value must be skipped
    return {"T2M_MAX": tmax, "PRECTOTCORR": rain, "RH2M": rh, "WS2M": ws}


def test_power_url_matches_plan():
    u = power.build_url(25.39, 68.37)
    assert u.startswith("https://power.larc.nasa.gov/api/temporal/daily/point?")
    assert "parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN" in u
    assert "community=AG" in u and "longitude=68.37" in u and "latitude=25.39" in u
    assert "start=20150101" in u and "end=20251231" in u and "format=JSON" in u


def test_power_summarize():
    out = power.summarize(daily_fixture())
    assert out["heat_days_40c_by_month"][5] == 2.0
    assert out["heat_days_40c_by_month"][1] == 0.0
    assert out["tmax_mean_by_month"][1] == 30.0
    assert out["rain_mm_by_month"][1] == 4.0           # 4 days x 1 mm
    assert out["rh_mean"] == 50.0 and out["wind_mean"] == 2.0
    assert set(out["heat_days_40c_by_month"]) == set(range(1, 13))


def test_power_summarize_needs_all_months():
    d = daily_fixture()
    d["T2M_MAX"] = {k: v for k, v in d["T2M_MAX"].items() if k[4:6] != "02"}
    assert power.summarize(d) is None


def test_power_cache_and_failure(tmp_path):
    calls = []

    def fetcher(lat, lon):
        calls.append(1)
        return daily_fixture()

    a = power.get_monthly_features(25.39, 68.37, tmp_path, tmp_path, fetcher=fetcher)
    b = power.get_monthly_features(25.39, 68.37, tmp_path, tmp_path, fetcher=fetcher)
    assert a == b and len(calls) == 1                   # second call came from the cache
    other = power.get_monthly_features(25.5, 68.5, tmp_path, tmp_path, fetcher=lambda a, b: None)
    assert other is None                                # no network, no cache, no sample -> missing (never invented)


# ---------------------------------------------------------------- Meteomatics
MM = {"data": [
    {"parameter": "t_2m:C", "coordinates": [{"lat": 25.39, "lon": 68.37, "dates": [
        {"date": "2026-11-15T00:00:00Z", "value": 31.2}, {"date": "2026-11-15T01:00:00Z", "value": 32.0}]}]},
    {"parameter": "precip_1h:mm", "coordinates": [{"lat": 25.39, "lon": 68.37, "dates": [
        {"date": "2026-11-15T00:00:00Z", "value": 0.0}, {"date": "2026-11-15T01:00:00Z", "value": 2.5}]}]},
    {"parameter": "relative_humidity_2m:p", "coordinates": [{"lat": 25.39, "lon": 68.37, "dates": [
        {"date": "2026-11-15T00:00:00Z", "value": 50.0}, {"date": "2026-11-15T01:00:00Z", "value": 55.0}]}]},
    {"parameter": "wind_speed_10m:ms", "coordinates": [{"lat": 25.39, "lon": 68.37, "dates": [
        {"date": "2026-11-15T00:00:00Z", "value": 2.0}, {"date": "2026-11-15T01:00:00Z", "value": 4.0}]}]},
]}
NOW = datetime(2026, 11, 15, 8, 0, tzinfo=timezone.utc)


def test_meteomatics_url_and_parse():
    u = weather.build_url(25.39, 68.37, NOW)
    assert u == "https://api.meteomatics.com/2026-11-15T08:00:00Z--2026-11-16T08:00:00Z:PT1H/t_2m:C,precip_1h:mm,relative_humidity_2m:p,wind_speed_10m:ms/25.39,68.37/json"
    parsed = weather.parse_meteomatics(MM)
    assert len(parsed["hourly"]) == 2
    assert parsed["hourly"][0] == {"timestamp_utc": "2026-11-15T00:00:00Z", "temperature_c": 31.2,
                                     "precipitation_mm": 0.0, "relative_humidity_percent": 50.0, "wind_speed_ms": 2.0}
    assert parsed["days"] == [{"date": "2026-11-15", "tmax_c": 32.0, "tmin_c": 31.2,
                               "rain_total_mm": 2.5, "rh_mean": 52.5, "wind_max_ms": 4.0}]
    assert weather.parse_meteomatics({}) == {"hourly": [], "days": []}


def kw(tmp_path, **o):
    base = dict(user="", password="", samples_dir=tmp_path, demo_mode=False, now=NOW, use_cache=False)
    base.update(o)
    return base


def test_weather_no_credentials_means_unavailable(tmp_path):
    out = weather.get_weather(25.39, 68.37, **kw(tmp_path))
    assert out["available"] is False and out["is_live"] is False and out["is_sample"] is False
    assert out["days"] == []


def test_weather_live(tmp_path):
    def fetcher(*args, **kwargs):
        return weather.parse_meteomatics(MM)

    out = weather.get_weather(25.39, 68.37, **kw(tmp_path, user="u", password="p", fetcher=fetcher))
    assert out["available"] and not out["is_sample"] and len(out["days"]) == 1
    assert len(out["hourly"]) == 2


def test_weather_failure_uses_labelled_sample(tmp_path):
    (tmp_path / "meteomatics_sample.json").write_text(json.dumps(MM))

    def boom(*a, **k):
        raise OSError("offline")

    out = weather.get_weather(25.39, 68.37, **kw(tmp_path, user="u", password="p", fetcher=boom))
    assert out["available"] and out["is_sample"] is True
    assert out["hourly"][0]["timestamp_utc"] == "2026-11-15T00:00:00Z"
    assert out["days"][0]["date"] == "2026-11-15"


def test_weather_failure_without_sample_is_unavailable(tmp_path):
    def boom(*a, **k):
        raise OSError("offline")

    out = weather.get_weather(25.39, 68.37, **kw(tmp_path, user="u", password="p", fetcher=boom))
    assert out["available"] is False


def test_weather_demo_mode_uses_sample_without_credentials(tmp_path):
    (tmp_path / "meteomatics_sample.json").write_text(json.dumps({"days": [{"tmax_c": 30, "rain_mm": 0}]}))
    out = weather.get_weather(25.39, 68.37, **kw(tmp_path, demo_mode=True))
    assert out["is_sample"] is True


# ---------------------------------------------------------------- features
def test_haversine():
    assert abs(haversine_km(25.39, 68.37, 25.39, 68.37)) < 1e-9
    assert 100 < haversine_km(25.39, 68.37, 24.86, 67.01) < 160     # Hyderabad -> Karachi


def test_normalize_rejects_bad_values():
    f = normalize({"ndvi_mean": "0.4", "low_lying_flag": 1, "heat_days_40c_by_month": {"1": 1}}, 0.5)
    assert f["sources"] == [] and f["sources_present"] == 0


def test_feature_store_nearest(tmp_path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"points": [
        {"id": "a", "lat": 25.39, "lon": 68.37, "features": {}},
        {"id": "b", "lat": 25.50, "lon": 68.50, "features": {}}]}))
    st = FeatureStore(p, max_km=5)
    assert st.nearest(25.391, 68.371)[0]["id"] == "a"
    assert st.nearest(25.499, 68.499)[0]["id"] == "b"
    assert st.nearest(25.2, 68.2) is None
    assert FeatureStore(tmp_path / "missing.json").available() is False
