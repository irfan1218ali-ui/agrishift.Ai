"""Authenticated, database-backed endpoints for the single AgriShift expert role."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import date, datetime, time as datetime_time, timedelta, timezone
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, or_, select
from sqlalchemy.engine import Engine

from . import db
from .service import build_deps
from rotation_engine.engine import Ctx, score_components, upcoming_seasons

COOKIE_NAME = "agrishift_expert_session"
SESSION_TTL_SECONDS = 8 * 60 * 60
PASSWORD_HASH_ITERATIONS = 600_000
DECISIONS = ("approved", "approved_with_changes", "needs_more_information", "unsuitable")
FINAL_REVIEW_STATUSES = DECISIONS

router = APIRouter(prefix="/api/v2/expert", tags=["expert portal"])
auth_router = APIRouter(prefix="/auth", tags=["expert authentication"])


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def create_password_hash(password: str, iterations: int = PASSWORD_HASH_ITERATIONS) -> str:
    """Create an environment-ready PBKDF2-SHA256 password hash."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iteration_text, salt_text, digest_text = encoded.split("$", 3)
        iterations = int(iteration_text)
        if algorithm != "pbkdf2_sha256" or not 100_000 <= iterations <= 2_000_000:
            return False
        expected = _unb64(digest_text)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _unb64(salt_text), iterations)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _session_secret() -> str:
    secret = os.environ.get("EXPERT_SESSION_SECRET", "")
    if len(secret) < 32:
        raise HTTPException(status_code=503, detail="Expert session signing is not configured.")
    return secret


def _sign(payload: str) -> str:
    return _b64(hmac.new(_session_secret().encode("utf-8"), payload.encode("ascii"), hashlib.sha256).digest())


def _new_session(user: dict[str, Any]) -> tuple[str, int, int]:
    now = int(time.time())
    expires = now + SESSION_TTL_SECONDS
    payload = _b64(json.dumps({"sub": user["id"], "role": "EXPERT", "iat": now,
                               "exp": expires, "nonce": secrets.token_urlsafe(16)},
                              separators=(",", ":")).encode("utf-8"))
    return f"{payload}.{_sign(payload)}", now, expires


def _engine() -> Engine:
    engine = db.get_engine()
    db.initialize(engine)
    return engine


def _current_expert(request: Request) -> dict[str, Any]:
    if (not os.environ.get("EXPERT_EMAIL", "").strip() or
            not os.environ.get("EXPERT_PASSWORD_HASH", "").strip() or
            len(os.environ.get("EXPERT_SESSION_SECRET", "")) < 32):
        raise HTTPException(status_code=503, detail="Expert authentication is not configured.")
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=401, detail="Expert authentication is required.")
    try:
        payload, signature = token.split(".", 1)
        if not hmac.compare_digest(_sign(payload), signature):
            raise ValueError("invalid signature")
        claims = json.loads(_unb64(payload))
        if claims.get("role") != "EXPERT":
            raise HTTPException(status_code=403, detail="This session is not authorized for the expert portal.")
        now = int(time.time())
        if (not isinstance(claims.get("exp"), int)
                or not isinstance(claims.get("iat"), int) or claims["exp"] <= now
                or claims["iat"] > now + 60):
            raise ValueError("expired or invalid claims")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Expert session is invalid or expired.")

    engine = _engine()
    with engine.connect() as connection:
        user = connection.execute(select(db.expert_users).where(
            db.expert_users.c.id == claims.get("sub"))).mappings().first()
    if not user or not user["is_active"]:
        raise HTTPException(status_code=401, detail="Expert session is invalid or expired.")
    if user["role"] != "EXPERT":
        raise HTTPException(status_code=403, detail="This account is not authorized for the expert portal.")
    revoked = user["session_revoked_before"]
    if revoked:
        revoked_timestamp = revoked.replace(tzinfo=timezone.utc).timestamp() if revoked.tzinfo is None else revoked.timestamp()
        if claims["iat"] <= int(revoked_timestamp):
            raise HTTPException(status_code=401, detail="Expert session has been revoked.")
    return {"id": user["id"], "email": user["email"], "role": user["role"]}


class LoginBody(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=254)
    password: str = Field(min_length=1, max_length=1024)


class ReviewBody(BaseModel):
    decision: Literal["approved", "approved_with_changes", "needs_more_information", "unsuitable"] | None = None
    comments: str = Field(default="", max_length=10_000)
    suggested_rotation: list[dict[str, Any]] | dict[str, Any] | None = None
    soil_test_requested: bool = False


class ReviewPatch(BaseModel):
    decision: Literal["approved", "approved_with_changes", "needs_more_information", "unsuitable"] | None = None
    comments: str | None = Field(default=None, max_length=10_000)
    suggested_rotation: list[dict[str, Any]] | dict[str, Any] | None = None
    soil_test_requested: bool | None = None


class NotesBody(BaseModel):
    content: str = Field(max_length=20_000)


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat() if isinstance(value, datetime) else str(value)


def _review_dict(row: Any) -> dict[str, Any]:
    return {"review_id": row["id"], "analysis_id": row["analysis_id"],
            "expert_user_id": row["expert_user_id"], "decision": row["decision"],
            "comments": row["comments"],
            "suggested_rotation": json.loads(row["suggested_rotation_json"]) if row["suggested_rotation_json"] else None,
            "soil_test_requested": bool(row["soil_test_requested"]),
            "reviewed_at": _iso(row["reviewed_at"]), "created_at": _iso(row["created_at"]),
            "updated_at": _iso(row["updated_at"])}


def _rotation_components_for_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    result = record.get("result") or {}
    request = record.get("request") or {}
    features = (result.get("field_context") or {}).get("environmental_features") or {}
    options = result.get("options") or result.get("rotation_options") or []
    current = request.get("current_crop")
    deps = build_deps()
    current_crop = deps.crops.get(current)
    heat = features.get("heat_days_40c_by_month")
    ndvi, low_lying = features.get("ndvi_mean"), features.get("low_lying_flag")
    if not current_crop or not isinstance(heat, dict) or not isinstance(ndvi, (int, float)) or not isinstance(low_lying, bool):
        return []
    heat_days = {int(k): float(v) for k, v in heat.items()}
    if set(heat_days) != set(range(1, 13)):
        return []
    engine_request = {"current_crop": current, "water_source": request.get("water_source", "canal"),
                      "water_amount": request.get("water_level", request.get("water_amount", "medium")),
                      "salinity": request.get("salinity", "unknown"),
                      "waterlogging": request.get("waterlogging", "unknown"),
                      "priority": request.get("priority", "balanced")}
    rows = []
    for option in options:
        seasons = option.get("seasons") or []
        if len(seasons) != 2:
            continue
        first, second = (deps.crops.get(seasons[i].get("crop")) for i in range(2))
        if not first or not second:
            continue
        slots = []
        for item in seasons:
            label = str(item.get("season", ""))
            season = "rabi" if label.lower().startswith("rabi") else "kharif" if label.lower().startswith("kharif") else ""
            slots.append((season, label))
        wkey = engine_request["priority"] if option.get("id") == "existing" else "balanced"
        if option.get("id") == "priority":
            wkey = engine_request["priority"] if engine_request["priority"] != "balanced" else "save_water_soil"
        ctx = Ctx(crops=deps.crops, current=current_crop, water_source=engine_request["water_source"],
                  water_amount=engine_request["water_amount"], salinity=engine_request["salinity"],
                  waterlogging=engine_request["waterlogging"], priority=engine_request["priority"],
                  low_lying=low_lying, ndvi=float(ndvi), heat_days=heat_days,
                  sources_present=3, slots=slots)
        breakdown = option.get("score_breakdown") or score_components(
            first, second, ctx, wkey, float(option.get("score", 0)))
        for key, component in breakdown.items():
            rows.append({"analysis_id": record["analysis_id"], "option_id": option.get("id", "unknown"),
                         "component_key": key, "value": float(component["value"]),
                         "reason": str(component["reason"]), "rule_id": str(component["rule_id"]),
                         "verified": bool(component["verified"]), "source": str(component["source"])})
    return rows


def _save_missing_score_components(engine: Engine, record: dict[str, Any]) -> None:
    rows = _rotation_components_for_record(record)
    if not rows:
        return
    with engine.begin() as connection:
        for row in rows:
            exists = connection.execute(select(db.rotation_score_components.c.id).where(
                db.rotation_score_components.c.analysis_id == row["analysis_id"],
                db.rotation_score_components.c.option_id == row["option_id"],
                db.rotation_score_components.c.component_key == row["component_key"])).first()
            if not exists:
                connection.execute(db.rotation_score_components.insert().values(**row))


def _load_score_breakdown(engine: Engine, analysis_id: str) -> dict[str, dict[str, dict[str, Any]]]:
    with engine.connect() as connection:
        rows = connection.execute(select(db.rotation_score_components).where(
            db.rotation_score_components.c.analysis_id == analysis_id).order_by(
                db.rotation_score_components.c.option_id, db.rotation_score_components.c.id)).mappings()
    out: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        out.setdefault(row["option_id"], {})[row["component_key"]] = {
            "value": row["value"], "reason": row["reason"], "rule_id": row["rule_id"],
            "verified": bool(row["verified"]), "source": row["source"]}
    return out


def _require_analysis(engine: Engine, analysis_id: str) -> dict[str, Any]:
    record = db.load_analysis(analysis_id, engine)
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return record


def _set_review_status(connection: Any, analysis_id: str, status: str, review_id: str | None,
                       expert_user_id: str, reviewed_at: datetime | None) -> None:
    existing = connection.execute(select(db.analysis_review_status.c.analysis_id).where(
        db.analysis_review_status.c.analysis_id == analysis_id)).first()
    values = {"status": status, "last_review_id": review_id, "expert_user_id": expert_user_id,
              "reviewed_at": reviewed_at, "updated_at": datetime.now(timezone.utc)}
    if existing:
        connection.execute(db.analysis_review_status.update().where(
            db.analysis_review_status.c.analysis_id == analysis_id).values(**values))
    else:
        connection.execute(db.analysis_review_status.insert().values(
            analysis_id=analysis_id, created_at=datetime.now(timezone.utc), **values))


@auth_router.post("/login")
def login(body: LoginBody, response: Response):
    if (not os.environ.get("EXPERT_EMAIL", "").strip() or
            not os.environ.get("EXPERT_PASSWORD_HASH", "").strip()):
        raise HTTPException(status_code=503, detail="Expert account is not configured.")
    _session_secret()
    engine = _engine()
    email = str(body.email).strip().lower()
    with engine.connect() as connection:
        user = connection.execute(select(db.expert_users).where(db.expert_users.c.email == email)).mappings().first()
    if not user or not user["is_active"] or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")
    if user["role"] != "EXPERT":
        raise HTTPException(status_code=403, detail="This account is not authorized for the expert portal.")
    token, now, expires = _new_session(user)
    logged_in_at = datetime.fromtimestamp(now, timezone.utc)
    with engine.begin() as connection:
        connection.execute(db.expert_users.update().where(db.expert_users.c.id == user["id"]).values(
            last_login_at=logged_in_at, updated_at=logged_in_at))
    response.set_cookie(COOKIE_NAME, token, max_age=expires - now,
                        expires=datetime.fromtimestamp(expires, timezone.utc),
                        httponly=True, secure=True, samesite="strict", path="/")
    return {"authenticated": True, "role": "EXPERT", "email": user["email"], "expires_at": expires}


@auth_router.post("/logout")
def logout(response: Response, expert: dict[str, Any] = Depends(_current_expert)):
    now = datetime.now(timezone.utc)
    engine = _engine()
    with engine.begin() as connection:
        connection.execute(db.expert_users.update().where(db.expert_users.c.id == expert["id"]).values(
            session_revoked_before=now, updated_at=now))
    response.delete_cookie(COOKIE_NAME, path="/", httponly=True, secure=True, samesite="strict")
    return {"authenticated": False}


@auth_router.get("/me")
def me(expert: dict[str, Any] = Depends(_current_expert)):
    return {"authenticated": True, **expert}


@router.get("/analyses")
def list_analyses(
    status: str | None = Query(default=None, pattern="^(not_reviewed|under_review|approved|approved_with_changes|needs_more_information|unsuitable|ok|not_applicable|insufficient_data)$"),
    confidence: str | None = Query(default=None, pattern="^(low|medium|high)$"),
    previous_crop: str | None = None, priority: str | None = None, salinity: str | None = None,
    waterlogging: str | None = None, date_from: date | None = None, date_to: date | None = None,
    search: str | None = Query(default=None, max_length=200),
    page: int = Query(default=1, ge=1), page_size: int = Query(default=20, ge=1, le=100),
    expert: dict[str, Any] = Depends(_current_expert),
):
    engine = _engine()
    conditions = []
    review_status = func.coalesce(db.analysis_review_status.c.status, "not_reviewed")
    if status:
        conditions.append(or_(review_status == status, db.analysis_results.c.status == status))
    if confidence == "low":
        conditions.append(db.analysis_results.c.confidence_score < 55)
    elif confidence == "medium":
        conditions.append(and_(db.analysis_results.c.confidence_score >= 55, db.analysis_results.c.confidence_score < 80))
    elif confidence == "high":
        conditions.append(db.analysis_results.c.confidence_score >= 80)
    for column, value in ((db.analysis_requests.c.previous_crop, previous_crop),
                          (db.analysis_requests.c.priority, priority),
                          (db.analysis_requests.c.salinity, salinity),
                          (db.analysis_requests.c.waterlogging, waterlogging)):
        if value is not None:
            conditions.append(column == value)
    if date_from:
        conditions.append(db.analysis_requests.c.created_at >= datetime.combine(date_from, datetime_time.min))
    if date_to:
        conditions.append(db.analysis_requests.c.created_at < datetime.combine(date_to + timedelta(days=1), datetime_time.min))
    if search:
        needle = f"%{search.strip().lower()}%"
        conditions.append(or_(func.lower(db.analysis_requests.c.id).like(needle),
                              func.lower(db.analysis_requests.c.current_crop).like(needle),
                              func.lower(func.coalesce(db.analysis_requests.c.previous_crop, "")).like(needle)))
    base = select(db.analysis_requests.c.id).select_from(
        db.analysis_requests.join(db.analysis_results, db.analysis_results.c.request_id == db.analysis_requests.c.id)
        .outerjoin(db.analysis_review_status, db.analysis_review_status.c.analysis_id == db.analysis_requests.c.id))
    if conditions:
        base = base.where(*conditions)
    with engine.connect() as connection:
        total = connection.execute(select(func.count()).select_from(base.subquery())).scalar_one()
        ids = connection.execute(base.order_by(db.analysis_requests.c.created_at.desc(), db.analysis_requests.c.id)
                                  .offset((page - 1) * page_size).limit(page_size)).scalars().all()
    items = []
    for analysis_id in ids:
        record = _require_analysis(engine, analysis_id)
        items.append(record)
    return {"items": items, "total": total, "page": page, "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size}


@router.get("/analyses/summary")
def analysis_summary(expert: dict[str, Any] = Depends(_current_expert)):
    engine = _engine()
    statuses = db.analysis_review_status.c.status
    with engine.connect() as connection:
        total = connection.execute(select(func.count()).select_from(db.analysis_requests.join(
            db.analysis_results, db.analysis_results.c.request_id == db.analysis_requests.c.id))).scalar_one()
        pending = connection.execute(select(func.count()).select_from(db.analysis_review_status).where(
            statuses.in_(["not_reviewed", "under_review"]))).scalar_one()
        completed = connection.execute(select(func.count()).select_from(db.analysis_review_status).where(
            statuses.in_(FINAL_REVIEW_STATUSES))).scalar_one()
        low_confidence = connection.execute(select(func.count()).select_from(db.analysis_results).where(
            db.analysis_results.c.confidence_score < 55)).scalar_one()
        recent_ids = connection.execute(select(db.analysis_requests.c.id).select_from(
            db.analysis_requests.join(db.analysis_results, db.analysis_results.c.request_id == db.analysis_requests.c.id)
        ).order_by(db.analysis_requests.c.created_at.desc()).limit(8)).scalars().all()
    recent = [_require_analysis(engine, analysis_id) for analysis_id in recent_ids]
    return {"total_analyses": total, "pending_reviews": pending,
            "low_confidence_analyses": low_confidence, "completed_reviews": completed,
            "recent_analyses": recent}


@router.get("/analyses/{analysis_id}")
def analysis_detail(analysis_id: str, expert: dict[str, Any] = Depends(_current_expert)):
    engine = _engine()
    record = _require_analysis(engine, analysis_id)
    _save_missing_score_components(engine, record)
    with engine.connect() as connection:
        reviews = connection.execute(select(db.expert_reviews).where(
            db.expert_reviews.c.analysis_id == analysis_id).order_by(
                db.expert_reviews.c.created_at.desc())).mappings().all()
        note = connection.execute(select(db.expert_notes).where(and_(
            db.expert_notes.c.analysis_id == analysis_id,
            db.expert_notes.c.expert_user_id == expert["id"]))).mappings().first()
    return {"analysis": record, "review_status": record.get("review_status", "not_reviewed"),
            "score_breakdown": _load_score_breakdown(engine, analysis_id),
            "reviews": [_review_dict(row) for row in reviews],
            "notes": ({"content": note["content"], "created_at": _iso(note["created_at"]),
                       "updated_at": _iso(note["updated_at"])} if note else {"content": "", "created_at": None, "updated_at": None})}


@router.get("/analyses/{analysis_id}/reviews")
def analysis_reviews(analysis_id: str, expert: dict[str, Any] = Depends(_current_expert)):
    engine = _engine()
    _require_analysis(engine, analysis_id)
    with engine.connect() as connection:
        rows = connection.execute(select(db.expert_reviews).where(
            db.expert_reviews.c.analysis_id == analysis_id).order_by(
                db.expert_reviews.c.created_at.desc())).mappings().all()
    return {"items": [_review_dict(row) for row in rows]}


@router.post("/analyses/{analysis_id}/reviews", status_code=201)
def create_review(analysis_id: str, body: ReviewBody, expert: dict[str, Any] = Depends(_current_expert)):
    engine = _engine()
    _require_analysis(engine, analysis_id)
    now = datetime.now(timezone.utc)
    review_id = str(uuid4())
    status = body.decision or "under_review"
    reviewed_at = now if body.decision else None
    with engine.begin() as connection:
        connection.execute(db.expert_reviews.insert().values(
            id=review_id, analysis_id=analysis_id, expert_user_id=expert["id"], decision=body.decision,
            comments=body.comments, suggested_rotation_json=json.dumps(body.suggested_rotation, ensure_ascii=False) if body.suggested_rotation is not None else None,
            soil_test_requested=body.soil_test_requested, reviewed_at=reviewed_at, created_at=now, updated_at=now))
        _set_review_status(connection, analysis_id, status, review_id, expert["id"], reviewed_at)
        row = connection.execute(select(db.expert_reviews).where(db.expert_reviews.c.id == review_id)).mappings().one()
    return _review_dict(row)


@router.patch("/reviews/{review_id}")
def update_review(review_id: str, body: ReviewPatch, expert: dict[str, Any] = Depends(_current_expert)):
    engine = _engine()
    with engine.begin() as connection:
        existing = connection.execute(select(db.expert_reviews).where(
            db.expert_reviews.c.id == review_id)).mappings().first()
        if not existing:
            raise HTTPException(status_code=404, detail="Review not found.")
        if existing["expert_user_id"] != expert["id"]:
            raise HTTPException(status_code=403, detail="This review belongs to another expert account.")
        values = body.model_dump(exclude_unset=True)
        if "suggested_rotation" in values:
            values["suggested_rotation_json"] = json.dumps(values.pop("suggested_rotation"), ensure_ascii=False) if values["suggested_rotation"] is not None else None
        values["updated_at"] = datetime.now(timezone.utc)
        decision = values.get("decision", existing["decision"])
        if decision is None:
            reviewed_at, status = None, "under_review"
        else:
            reviewed_at, status = datetime.now(timezone.utc), decision
        values["reviewed_at"] = reviewed_at
        connection.execute(db.expert_reviews.update().where(db.expert_reviews.c.id == review_id).values(**values))
        _set_review_status(connection, existing["analysis_id"], status, review_id, expert["id"], reviewed_at)
        row = connection.execute(select(db.expert_reviews).where(db.expert_reviews.c.id == review_id)).mappings().one()
    return _review_dict(row)


@router.get("/analyses/{analysis_id}/notes")
def get_notes(analysis_id: str, expert: dict[str, Any] = Depends(_current_expert)):
    engine = _engine()
    _require_analysis(engine, analysis_id)
    with engine.connect() as connection:
        row = connection.execute(select(db.expert_notes).where(and_(
            db.expert_notes.c.analysis_id == analysis_id,
            db.expert_notes.c.expert_user_id == expert["id"]))).mappings().first()
    return {"analysis_id": analysis_id, "content": row["content"] if row else "",
            "created_at": _iso(row["created_at"]) if row else None,
            "updated_at": _iso(row["updated_at"]) if row else None}


@router.put("/analyses/{analysis_id}/notes")
def save_notes(analysis_id: str, body: NotesBody, expert: dict[str, Any] = Depends(_current_expert)):
    engine = _engine()
    _require_analysis(engine, analysis_id)
    now, note_id = datetime.now(timezone.utc), str(uuid4())
    with engine.begin() as connection:
        existing = connection.execute(select(db.expert_notes.c.id).where(and_(
            db.expert_notes.c.analysis_id == analysis_id,
            db.expert_notes.c.expert_user_id == expert["id"]))).first()
        if existing:
            connection.execute(db.expert_notes.update().where(db.expert_notes.c.id == existing.id).values(
                content=body.content, updated_at=now))
        else:
            connection.execute(db.expert_notes.insert().values(
                id=note_id, analysis_id=analysis_id, expert_user_id=expert["id"],
                content=body.content, created_at=now, updated_at=now))
        row = connection.execute(select(db.expert_notes).where(and_(
            db.expert_notes.c.analysis_id == analysis_id,
            db.expert_notes.c.expert_user_id == expert["id"]))).mappings().one()
    return {"analysis_id": analysis_id, "content": row["content"],
            "created_at": _iso(row["created_at"]), "updated_at": _iso(row["updated_at"])}


router.include_router(auth_router)
