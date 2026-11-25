import json
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy import create_engine
from starlette.requests import Request

from app import db
from app import main
from app.main import _error, deps
from app.schemas.analyze import AnalyzeRequest


def test_analysis_persistence_write_and_read(tmp_path):
    engine = create_engine("sqlite:///" + (tmp_path / "analysis.sqlite").as_posix())
    request = {
        "lat": 25.39, "lon": 68.37, "radius_m": 150, "previous_crop": "unknown",
        "current_crop": "cotton", "water_source": "canal", "water_amount": "medium",
        "salinity": "unknown", "waterlogging": "unknown", "priority": "balanced", "language": "en",
    }
    result = {"status": "insufficient_data", "data_mode": "REAL", "options": [], "limitations": ["No validated features"]}
    analysis_id = db.save_analysis(request, result, engine)
    record = db.load_analysis(analysis_id, engine)
    assert record["analysis_id"] == analysis_id
    assert record["request"]["current_crop"] == "cotton"
    assert record["result"]["status"] == "insufficient_data"
    assert record["result"]["analysis_id"] == analysis_id
    assert {"analysis_requests", "analysis_results", "dataset_metadata", "model_runs"}.issubset(
        set(db.metadata.tables)
    )


def test_standard_error_body_has_request_id():
    request = Request({"type": "http", "method": "GET", "path": "/api/v1/layers/ndvi.png",
                       "headers": [], "query_string": b"", "server": ("test", 80),
                       "client": ("test", 1), "scheme": "http", "root_path": ""})
    request.state.request_id = "request-test-id"
    response = _error(request, 404, "RESOURCE_NOT_FOUND", "layer not available")
    payload = json.loads(response.body)
    assert response.status_code == 404
    assert payload["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert payload["error"]["request_id"] == "request-test-id"


def test_real_farmer_journey_layers_weather_and_persisted_analysis(monkeypatch, tmp_path):
    root = db.get_settings().root
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("AGRISHIFT_ROOT", str(root))
    monkeypatch.setenv("DATABASE_URL", "sqlite:///" + (tmp_path / "farmer.sqlite").as_posix())
    monkeypatch.setenv("METEOMATICS_SAMPLE_FILE", str(
        root / "data" / "processed" / "weather" / "meteomatics_daily.json"))
    monkeypatch.setenv("METEOMATICS_USERNAME", "")
    monkeypatch.setenv("METEOMATICS_USER", "")
    monkeypatch.setenv("METEOMATICS_PASSWORD", "")
    db.get_engine.cache_clear()
    deps.cache_clear()
    try:
        assert (root / "apps" / "web" / "index.html").is_file()
        health = main.health()
        assert health["data_mode"] == "REAL" and health["features_available"] is True
        assert health["environmental_clustering"] == "available"

        layers = main.layer_metadata()
        assert set(layers["layers"]) == {"ndvi", "ndmi", "bsi", "slope"}
        assert layers["bounds"] == {"west": 68.2, "south": 25.2, "east": 68.55, "north": 25.55}
        for name in ("ndvi", "ndmi", "bsi", "slope"):
            response = main.layer(name)
            assert Path(response.path).read_bytes().startswith(b"\x89PNG\r\n\x1a\n")

        weather = main.weather(25.21748, 68.334874)
        assert weather["is_sample"] is True and weather["is_live"] is False
        valid_until = datetime.fromisoformat(weather["valid_until"].replace("Z", "+00:00"))
        expected_expired = valid_until < datetime.now(timezone.utc)
        assert weather["status"] == "saved_sample" and weather["expired"] is expected_expired
        assert weather["days"] and "rain_total_mm" in weather["days"][0]

        request = AnalyzeRequest(
            lat=25.21748, lon=68.334874, radius_m=150,
            current_crop="cotton", previous_crop="unknown", water_source="canal",
            water_amount="medium", salinity="no", waterlogging="no",
            priority="balanced", language="en",
        )
        analysis = main.analyze(request)
        assert analysis["status"] == "ok" and analysis["data_mode"] == "REAL"
        assert analysis["analysis_method"] == "nearest_precomputed_point"
        assert analysis["feature_point"]["id"] == "hyd_001"
        assert analysis["feature_point"]["distance_m"] == 0
        assert analysis["field_context"]["cluster_label"] in {
            "Relatively vegetated", "Intermediate condition", "Higher bare/thermal exposure"
        }
        assert analysis["field_context"]["cluster_id"] is not None
        assert analysis["weather"]["is_sample"] is True
        assert len(analysis["options"]) == 3
        assert len({tuple((s["crop"], s["season"]) for s in o["seasons"])
                    for o in analysis["options"]}) == 3
        assert all(o["confidence_dots"] <= 2 for o in analysis["options"] if not o["crop_verified"])

        saved = main.get_analysis(analysis["analysis_id"])
        assert saved["result"]["analysis_id"] == analysis["analysis_id"]
        assert saved["result"]["field_context"]["cluster_id"] == analysis["field_context"]["cluster_id"]
    finally:
        engine = db.get_engine()
        engine.dispose()
        db.get_engine.cache_clear()
        deps.cache_clear()
