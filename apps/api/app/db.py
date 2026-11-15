"""SQLite persistence for analysis requests and versioned result metadata."""
from __future__ import annotations

import json
from functools import lru_cache
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, MetaData, String, Table, Text, create_engine, select
from sqlalchemy.engine import Engine
from sqlalchemy.sql import func

from .config import get_settings

metadata = MetaData()
analysis_requests = Table(
    "analysis_requests", metadata,
    Column("id", String(36), primary_key=True),
    Column("latitude", Float, nullable=False), Column("longitude", Float, nullable=False),
    Column("radius_m", Integer, nullable=False), Column("previous_crop", String(80)),
    Column("current_crop", String(80), nullable=False), Column("water_source", String(32), nullable=False),
    Column("water_level", String(32), nullable=False), Column("salinity", String(16), nullable=False),
    Column("waterlogging", String(16), nullable=False), Column("priority", String(32), nullable=False),
    Column("language", String(8), nullable=False), Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
analysis_results = Table(
    "analysis_results", metadata,
    Column("id", String(36), primary_key=True),
    Column("request_id", String(36), ForeignKey("analysis_requests.id"), nullable=False, unique=True),
    Column("feature_point_id", String(128)), Column("cluster_id", Integer), Column("cluster_label", String(128)),
    Column("rotation_results_json", Text, nullable=False), Column("confidence_score", Integer),
    Column("status", String(32), nullable=False), Column("created_at", DateTime(timezone=True), server_default=func.now()),
)
dataset_metadata = Table(
    "dataset_metadata", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True), Column("provider", String(80), nullable=False),
    Column("product", String(120), nullable=False), Column("version", String(40)),
    Column("observation_start", String(40)), Column("observation_end", String(40)),
    Column("source_resolution", String(80)), Column("validation_status", String(40)),
    Column("checksum", String(64)), Column("metadata_json", Text, nullable=False),
)
model_runs = Table(
    "model_runs", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True), Column("model_name", String(80), nullable=False),
    Column("model_version", String(80)), Column("feature_schema_version", String(80)),
    Column("training_timestamp", String(40)), Column("metrics_json", Text, nullable=False),
    Column("artifact_path", String(512)),
)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    settings = get_settings()
    url = __import__("os").environ.get("DATABASE_URL", "sqlite:///data/agrishift.db")
    if not url.startswith("sqlite:"):
        raise ValueError("The hackathon MVP database must use SQLite")
    if url in ("sqlite:///data/agrishift.db", "sqlite:///./data/agrishift.db"):
        path = settings.root / "data" / "agrishift.db"
        path.parent.mkdir(parents=True, exist_ok=True)
        url = "sqlite:///" + path.resolve().as_posix()
    return create_engine(url, connect_args={"check_same_thread": False})


def initialize(engine: Engine | None = None) -> None:
    metadata.create_all(engine or get_engine())


def save_analysis(request_data: dict, response: dict, engine: Engine | None = None) -> str:
    engine = engine or get_engine()
    initialize(engine)
    request_id = str(uuid4())
    result_id = str(uuid4())
    response["analysis_id"] = request_id
    with engine.begin() as conn:
        conn.execute(analysis_requests.insert().values(
            id=request_id, latitude=request_data["lat"], longitude=request_data["lon"],
            radius_m=request_data["radius_m"], previous_crop=request_data.get("previous_crop"),
            current_crop=request_data["current_crop"], water_source=request_data["water_source"],
            water_level=request_data["water_amount"], salinity=request_data["salinity"],
            waterlogging=request_data["waterlogging"], priority=request_data["priority"],
            language=request_data["language"],
        ))
        options = response.get("options", [])
        confidences = [o.get("confidence_score") for o in options if o.get("confidence_score") is not None]
        conn.execute(analysis_results.insert().values(
            id=result_id, request_id=request_id, feature_point_id=response.get("feature_point_id"),
            cluster_id=None, cluster_label=None, rotation_results_json=json.dumps(response, ensure_ascii=False),
            confidence_score=max(confidences) if confidences else None, status=response.get("status", "unknown"),
        ))
    return request_id


def load_analysis(analysis_id: str, engine: Engine | None = None) -> dict | None:
    engine = engine or get_engine()
    initialize(engine)
    statement = select(analysis_requests, analysis_results.c.rotation_results_json).join(
        analysis_results, analysis_requests.c.id == analysis_results.c.request_id
    ).where(analysis_requests.c.id == analysis_id)
    with engine.connect() as conn:
        row = conn.execute(statement).mappings().first()
    if row is None:
        return None
    return {
        "analysis_id": row["id"], "request": {key: row[key] for key in (
            "latitude", "longitude", "radius_m", "previous_crop", "current_crop", "water_source",
            "water_level", "salinity", "waterlogging", "priority", "language", "created_at"
        )},
        "result": json.loads(row["rotation_results_json"]),
    }
