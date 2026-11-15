import json

from sqlalchemy import create_engine
from starlette.requests import Request

from app import db
from app.main import _error


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
