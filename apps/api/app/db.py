"""SQLite persistence for analysis requests and versioned result metadata."""
from __future__ import annotations

import csv
import hashlib
import json
from functools import lru_cache
from uuid import uuid4

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, MetaData, String, Table, Text, create_engine, inspect, select, text
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
    Column("feature_point_id", String(128)), Column("distance_to_feature_point_m", Float),
    Column("analysis_method", String(80)), Column("cluster_id", Integer), Column("cluster_label", String(128)),
    Column("rotation_results_json", Text, nullable=False), Column("confidence_score", Float),
    Column("confidence_dots", Integer), Column("limitations_json", Text),
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
    Column("artifact_path", String(512)), Column("artifact_checksum", String(64)),
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
    engine = engine or get_engine()
    metadata.create_all(engine)
    # create_all does not add columns to an existing SQLite file; apply additive migrations.
    if engine.dialect.name == "sqlite":
        additions = {
            "analysis_results": {
                "distance_to_feature_point_m": "FLOAT",
                "analysis_method": "VARCHAR(80)",
                "confidence_dots": "INTEGER",
                "limitations_json": "TEXT",
            },
            "model_runs": {"artifact_checksum": "VARCHAR(64)"},
        }
        with engine.begin() as connection:
            inspector = inspect(engine)
            for table_name, columns in additions.items():
                existing = {item["name"] for item in inspector.get_columns(table_name)}
                for name, sql_type in columns.items():
                    if name not in existing:
                        connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {name} {sql_type}"))
    _seed_validated_metadata(engine)


def _seed_validated_metadata(engine: Engine) -> None:
    """Idempotently register catalog rows and the verified K-Means run, if present."""
    root = get_settings().root
    catalog = root / "data" / "catalog" / "datasets.csv"
    if catalog.is_file():
        with catalog.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        with engine.begin() as connection:
            for row in rows:
                exists = connection.execute(select(dataset_metadata.c.id).where(
                    dataset_metadata.c.provider == row.get("provider", ""),
                    dataset_metadata.c.product == row.get("product", ""),
                    dataset_metadata.c.version == row.get("version", ""),
                )).first()
                if exists:
                    continue
                period = row.get("test_date_range", "")
                start, separator, end = period.partition(" to ")
                connection.execute(dataset_metadata.insert().values(
                    provider=row.get("provider") or "unknown", product=row.get("product") or "unknown",
                    version=row.get("version"), observation_start=start or None,
                    observation_end=(end if separator else start) or None,
                    source_resolution=row.get("spatial_resolution"),
                    validation_status=row.get("status"), checksum=None,
                    metadata_json=json.dumps({key: row.get(key) for key in (
                        "dataset_id", "mission_or_service", "variables", "temporal_resolution",
                        "test_location", "limitations", "notes")}, ensure_ascii=False),
                ))

    artifacts = root / "ml" / "clustering" / "artifacts"
    manifest_path = artifacts / "training_manifest.json"
    metrics_path = artifacts / "metrics.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        artifact = artifacts / manifest["artifacts"]["kmeans"]["file"]
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if digest != manifest["artifacts"]["kmeans"]["sha256"]:
            return
        k = int(metrics["selected_k"])
        version = f"kmeans-k{k}-{manifest.get('library_version', 'unknown')}"
        model_name = manifest.get("model_name", "AgriShift Environmental K-Means")
        with engine.begin() as connection:
            exists = connection.execute(select(model_runs.c.id).where(
                model_runs.c.model_name == model_name, model_runs.c.model_version == version)).first()
            if not exists:
                connection.execute(model_runs.insert().values(
                    model_name=model_name, model_version=version,
                    feature_schema_version=manifest.get("feature_schema_version", "1.0"),
                    training_timestamp=None, metrics_json=json.dumps(metrics),
                    artifact_path="ml/clustering/artifacts/kmeans.joblib", artifact_checksum=digest,
                ))
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return


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
        feature_point = response.get("feature_point") or {}
        field_context = response.get("field_context") or {}
        cluster = field_context.get("cluster") or {}
        conf = response.get("confidence") or {}
        dots = conf.get("dots") if isinstance(conf, dict) else None
        conn.execute(analysis_results.insert().values(
            id=result_id, request_id=request_id, feature_point_id=response.get("feature_point_id"),
            distance_to_feature_point_m=feature_point.get("distance_m"),
            analysis_method=response.get("analysis_method"),
            cluster_id=cluster.get("cluster_id"), cluster_label=cluster.get("cluster_label"),
            rotation_results_json=json.dumps(response, ensure_ascii=False),
            confidence_score=conf.get("score") if isinstance(conf, dict) else (max(confidences) if confidences else None),
            confidence_dots=dots.count("●") if isinstance(dots, str) else None,
            limitations_json=json.dumps(response.get("limitations", []), ensure_ascii=False),
            status=response.get("status", "unknown"),
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
