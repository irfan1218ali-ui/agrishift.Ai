from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app import db, expert_api, main
from app.config import get_settings
from app.schemas.analyze import AnalyzeRequest


COMPONENTS = (
    "base_score", "seasonal_fit", "water_compatibility", "rotation_diversity",
    "legume_benefit", "heat_suitability", "salinity_adjustment",
    "waterlogging_adjustment", "farmer_priority_adjustment", "verification_penalty",
    "final_score",
)


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///" + (tmp_path / "expert.sqlite").as_posix())
    monkeypatch.setenv("EXPERT_EMAIL", "expert@example.test")
    monkeypatch.setenv("EXPERT_PASSWORD_HASH", expert_api.create_password_hash("correct-horse", 100_000))
    monkeypatch.setenv("EXPERT_SESSION_SECRET", "phase-two-test-session-secret-32-bytes")
    monkeypatch.setenv("DEMO_MODE", "false")
    expert_api.reset_login_failures()
    db.get_engine.cache_clear()
    main.deps.cache_clear()
    with TestClient(main.app, base_url="https://testserver") as test_client:
        yield test_client
    db.get_engine.cache_clear()
    main.deps.cache_clear()


@pytest.fixture
def signed_in(client):
    response = client.post("/api/v2/expert/auth/login", json={
        "email": "expert@example.test", "password": "correct-horse"})
    assert response.status_code == 200
    return client


def _component(value: float) -> dict:
    return {"value": value, "reason": "Test factor from stored analysis inputs.",
            "rule_id": "TEST-RULE-001", "verified": False, "source": "test fixture"}


def save_analysis(client, *, current="cotton", previous="wheat", priority="balanced",
                  salinity="no", waterlogging="no", confidence=72.0, created=None):
    engine = db.get_engine()
    now = created or datetime.now(timezone.utc)
    request_data = {"lat": 25.21748, "lon": 68.334874, "radius_m": 150,
                    "previous_crop": previous, "current_crop": current, "water_source": "canal",
                    "water_amount": "medium", "salinity": salinity, "waterlogging": waterlogging,
                    "priority": priority, "language": "en"}
    options = []
    for option_id, score in (("existing", 62), ("balanced", 74), ("priority", 68)):
        options.append({"id": option_id, "seasons": [{"season": "rabi_2026_27", "crop": "wheat"},
                       {"season": "kharif_2027", "crop": "cotton"}], "score": score,
                       "confidence_score": confidence, "confidence_dots": 2, "water_drops": 2,
                       "light": "yellow", "crop_verified": False, "expert_needed": True,
                       "warnings": ["Unverified crop rule."],
                       "score_breakdown": {name: _component(float(score)) for name in COMPONENTS}})
    result = {"status": "ok", "data_mode": "REAL", "confidence": {"score": confidence},
              "options": options, "field_context": {"cluster": {"cluster_id": 0, "cluster_label": "Intermediate condition"},
                "environmental_features": {"ndvi_mean": 0.4, "low_lying_flag": False,
                    "heat_days_40c_by_month": {str(month): 0 for month in range(1, 13)}}},
              "dataset_metadata": {"landsat_9": {"observation_date": "2025-09-30", "resolution": 30}},
              "model_metadata": {"name": "Saved K-Means", "version": "1", "status": "available"},
              "limitations": ["Environmental clustering is not crop prediction."],
              "forecast": {"available": False, "is_live": False, "is_sample": False}}
    analysis_id = db.save_analysis(request_data, result, engine)
    if created:
        with engine.begin() as connection:
            connection.execute(db.analysis_requests.update().where(db.analysis_requests.c.id == analysis_id)
                               .values(created_at=created))
    return analysis_id


def test_expert_login_me_logout_and_secure_cookie(client):
    login = client.post("/api/v2/expert/auth/login", json={
        "email": "expert@example.test", "password": "correct-horse"})
    assert login.status_code == 200
    assert login.json()["role"] == "EXPERT"
    cookie = login.headers["set-cookie"].lower()
    assert "httponly" in cookie and "secure" in cookie and "samesite=strict" in cookie
    me = client.get("/api/v2/expert/auth/me")
    assert me.json()["email"] == "expert@example.test"
    assert me.headers["cache-control"] == "no-store"
    logout = client.post("/api/v2/expert/auth/logout")
    assert logout.status_code == 200
    assert client.get("/api/v2/expert/auth/me").status_code == 401


def test_invalid_expert_login_is_401(client):
    response = client.post("/api/v2/expert/auth/login", json={
        "email": "expert@example.test", "password": "wrong-password"})
    unknown = client.post("/api/v2/expert/auth/login", json={
        "email": "unknown@example.test", "password": "wrong-password"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert unknown.status_code == response.status_code
    assert unknown.json()["error"]["message"] == response.json()["error"]["message"]


def test_expert_login_rate_limit_is_structured(client):
    for _ in range(expert_api.LOGIN_FAILURE_LIMIT):
        response = client.post("/api/v2/expert/auth/login", json={
            "email": "expert@example.test", "password": "wrong-password"})
        assert response.status_code == 401
    limited = client.post("/api/v2/expert/auth/login", json={
        "email": "expert@example.test", "password": "correct-horse"})
    assert limited.status_code == 429
    assert int(limited.headers["retry-after"]) > 0
    assert limited.json()["error"]["code"] == "RATE_LIMITED"


def test_production_requires_expert_session_configuration(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.test")
    monkeypatch.setenv("EXPERT_EMAIL", "expert@example.test")
    monkeypatch.setenv("EXPERT_PASSWORD_HASH", "pbkdf2_sha256$600000$salt$digest")
    monkeypatch.delenv("EXPERT_SESSION_SECRET", raising=False)
    with pytest.raises(ValueError, match="EXPERT_SESSION_SECRET"):
        get_settings()


def test_sqlite_foreign_keys_are_enabled_and_enforced(client):
    engine = db.get_engine()
    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one() == 1
    with pytest.raises(IntegrityError):
        with engine.begin() as connection:
            connection.execute(db.expert_notes.insert().values(
                id="missing-parent-note", analysis_id="missing-analysis",
                expert_user_id="missing-expert", content="must reject"))


def test_request_bodies_over_one_mib_are_rejected(client):
    response = client.post("/api/v1/analyze", content=b"x" * (1024 * 1024 + 1),
                           headers={"content-type": "application/json"})
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "PAYLOAD_TOO_LARGE"


def test_unauthenticated_access_has_structured_401(client):
    response = client.get("/api/v2/expert/analyses")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_non_expert_session_has_structured_403(client):
    login = client.post("/api/v2/expert/auth/login", json={
        "email": "expert@example.test", "password": "correct-horse"})
    assert login.status_code == 200
    user_id = login.json().get("id")
    if not user_id:
        with db.get_engine().connect() as connection:
            user_id = connection.execute(db.expert_users.select()).mappings().one()["id"]
    now = int(expert_api.time.time())
    payload = expert_api._b64(json.dumps({
        "sub": user_id, "role": "FARMER", "iat": now, "exp": now + 60, "nonce": "test"},
        separators=(",", ":")).encode())
    token = f"{payload}.{expert_api._sign(payload)}"
    client.cookies.set(expert_api.COOKIE_NAME, token)
    response = client.get("/api/v2/expert/analyses")
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_session_expiry_is_rejected(client, monkeypatch):
    now = 1_700_000_000
    monkeypatch.setattr(expert_api.time, "time", lambda: now)
    login = client.post("/api/v2/expert/auth/login", json={
        "email": "expert@example.test", "password": "correct-horse"})
    assert login.status_code == 200
    monkeypatch.setattr(expert_api.time, "time", lambda: now + expert_api.SESSION_TTL_SECONDS + 1)
    response = client.get("/api/v2/expert/auth/me")
    assert response.status_code == 401


def test_analysis_list_filters_and_pagination(signed_in):
    save_analysis(signed_in, confidence=42, previous="wheat", priority="save_water", salinity="yes")
    save_analysis(signed_in, confidence=65, previous="cotton", priority="balanced")
    save_analysis(signed_in, confidence=88, previous="wheat", priority="balanced", waterlogging="yes")
    page = signed_in.get("/api/v2/expert/analyses?page=1&page_size=2").json()
    assert page["total"] == 3 and len(page["items"]) == 2 and page["total_pages"] == 2
    filtered = signed_in.get("/api/v2/expert/analyses?confidence=low&previous_crop=wheat&priority=save_water&salinity=yes").json()
    assert filtered["total"] == 1
    assert filtered["items"][0]["request"]["salinity"] == "yes"
    assert signed_in.get("/api/v2/expert/analyses?waterlogging=yes").json()["total"] == 1
    search = signed_in.get("/api/v2/expert/analyses?search=cotton").json()
    assert search["total"] == 3


def test_analysis_date_and_review_status_filters(signed_in):
    old_id = save_analysis(signed_in, created=datetime(2025, 1, 1))
    new_id = save_analysis(signed_in, created=datetime(2026, 1, 1))
    response = signed_in.get("/api/v2/expert/analyses?date_from=2025-12-31&date_to=2026-12-31&status=not_reviewed")
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["analysis_id"] == new_id
    assert old_id != new_id


def test_analysis_detail_exposes_persisted_score_breakdown(signed_in):
    analysis_id = save_analysis(signed_in)
    response = signed_in.get(f"/api/v2/expert/analyses/{analysis_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["analysis"]["analysis_id"] == analysis_id
    assert body["review_status"] == "not_reviewed"
    assert len(body["analysis"]["result"]["options"]) == 3
    assert set(body["score_breakdown"]["balanced"]) == set(COMPONENTS)
    for component in body["score_breakdown"]["balanced"].values():
        assert {"value", "reason", "rule_id", "verified", "source"} <= set(component)


def test_additive_database_migration_preserves_saved_analyses(signed_in):
    analysis_id = save_analysis(signed_in)
    db.initialize(db.get_engine())
    with db.get_engine().connect() as connection:
        existing = connection.execute(db.analysis_requests.select().where(
            db.analysis_requests.c.id == analysis_id)).first()
        tables = set(db.metadata.tables)
    assert existing is not None
    assert {"expert_users", "expert_reviews", "expert_notes", "analysis_review_status",
            "rotation_score_components"} <= tables


def test_review_creation_update_history_and_farmer_status(signed_in):
    analysis_id = save_analysis(signed_in)
    created = signed_in.post(f"/api/v2/expert/analyses/{analysis_id}/reviews", json={
        "comments": "Review started", "soil_test_requested": True})
    assert created.status_code == 201
    review_id = created.json()["review_id"]
    status = signed_in.get(f"/api/v2/expert/analyses/{analysis_id}").json()["review_status"]
    assert status == "under_review"
    updated = signed_in.patch(f"/api/v2/expert/reviews/{review_id}", json={
        "decision": "approved_with_changes", "comments": "Adjust sowing date.",
        "suggested_rotation": [{"season": "rabi", "crop": "wheat"}]})
    assert updated.status_code == 200 and updated.json()["reviewed_at"]
    assert updated.json()["reviewed_at"].endswith("Z")
    assert updated.json()["suggested_rotation"] == [{"season": "rabi", "crop": "wheat"}]
    assert signed_in.get(f"/api/v2/expert/analyses/{analysis_id}/reviews").json()["items"][0]["decision"] == "approved_with_changes"
    farmer_record = signed_in.get(f"/api/v1/analyses/{analysis_id}").json()
    assert farmer_record["review_status"] == "approved_with_changes"


def test_server_side_notes_persist(signed_in):
    analysis_id = save_analysis(signed_in)
    saved = signed_in.put(f"/api/v2/expert/analyses/{analysis_id}/notes", json={"content": "Inspect north edge."})
    assert saved.status_code == 200
    assert signed_in.get(f"/api/v2/expert/analyses/{analysis_id}/notes").json()["content"] == "Inspect north edge."
    with db.get_engine().connect() as connection:
        row = connection.execute(db.expert_notes.select()).mappings().one()
    assert row["content"] == "Inspect north edge." and row["expert_user_id"]


def test_summary_counts_all_analysis_and_review_states(signed_in):
    analysis_id = save_analysis(signed_in, confidence=42)
    save_analysis(signed_in, confidence=88)
    signed_in.post(f"/api/v2/expert/analyses/{analysis_id}/reviews", json={"decision": "approved"})
    response = signed_in.get("/api/v2/expert/analyses/summary")
    assert response.status_code == 200
    body = response.json()
    assert body["total_analyses"] == 2 and body["completed_reviews"] == 1
    assert body["low_confidence_analyses"] == 1 and len(body["recent_analyses"]) == 2


def test_missing_analysis_and_invalid_review_are_structured(signed_in):
    missing = signed_in.get("/api/v2/expert/analyses/missing-id")
    assert missing.status_code == 404 and missing.json()["error"]["code"] == "RESOURCE_NOT_FOUND"
    analysis_id = save_analysis(signed_in)
    invalid = signed_in.post(f"/api/v2/expert/analyses/{analysis_id}/reviews", json={"decision": "maybe"})
    assert invalid.status_code == 422 and invalid.json()["error"]["code"] == "VALIDATION_ERROR"


def test_existing_farmer_analysis_flow_still_saves_three_options(signed_in):
    request = AnalyzeRequest(lat=25.21748, lon=68.334874, radius_m=150,
        current_crop="cotton", previous_crop="unknown", water_source="canal", water_amount="medium",
        salinity="no", waterlogging="no", priority="balanced", language="en")
    response = main.analyze(request)
    assert response["status"] == "ok" and len(response["options"]) == 3
    saved = main.get_analysis(response["analysis_id"])
    assert saved["review_status"] == "not_reviewed"
    assert set(saved["result"]["options"][0]["score_breakdown"]) == set(COMPONENTS)
