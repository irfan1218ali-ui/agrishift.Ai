"""AgriShift AI - FastAPI app.   Run:  uvicorn app.main:app --app-dir apps/api --port 8000"""
from __future__ import annotations

from contextlib import asynccontextmanager
from functools import lru_cache
import json
import os
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .schemas import AnalyzeRequest
from . import service
from . import db
from . import expert_api
from . import regional_context
from .ml.clustering import load_artifacts

LAYER_NAMES = {"ndvi", "ndmi", "bsi", "slope"}
MAX_REQUEST_BODY_BYTES = 1_048_576

@asynccontextmanager
async def lifespan(_: FastAPI):
    db.initialize()
    try:
        load_artifacts(_settings.root / "ml" / "clustering" / "artifacts")
    except Exception:
        # Health and non-ML analysis remain available when optional model files are absent.
        pass
    yield


app = FastAPI(title="AgriShift AI API", version=os.environ.get("APP_VERSION", "2.0.0"),
              description="Rule-based rotation options with neutral environmental clustering for the Hyderabad pilot.",
              lifespan=lifespan)

_settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=_settings.cors_origins,
                   allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                   allow_headers=["*"], allow_credentials=True)
app.include_router(expert_api.router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            request_size = int(content_length)
        except ValueError:
            return _error(request, 400, "INVALID_CONTENT_LENGTH", "The request content length is invalid.")
        if request_size > MAX_REQUEST_BODY_BYTES:
            return _error(request, 413, "PAYLOAD_TOO_LARGE", "Request bodies must be 1 MiB or smaller.")
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "geolocation=(self), camera=(), microphone=()")
    if request.url.path.startswith("/api/v2/expert/"):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Vary"] = "Cookie"
    return response


def _error(request: Request, status_code: int, code: str, message: str, details=None):
    return JSONResponse(status_code=status_code, content={"error": {
        "code": code, "message": message, "request_id": getattr(request.state, "request_id", str(uuid4())),
        "details": details or {},
    }})


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return _error(request, 422, "VALIDATION_ERROR", "The request contains invalid values.",
                   {"errors": [{"location": list(e.get("loc", ())), "message": e.get("msg"),
                                "type": e.get("type")} for e in exc.errors()]})


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    code = {401: "AUTHENTICATION_REQUIRED", 403: "FORBIDDEN", 404: "RESOURCE_NOT_FOUND",
            429: "RATE_LIMITED",
            422: "VALIDATION_ERROR", 503: "SERVICE_UNAVAILABLE"}.get(exc.status_code, "REQUEST_REJECTED")
    response = _error(request, exc.status_code, code, str(exc.detail))
    for header, value in (exc.headers or {}).items():
        response.headers[header] = value
    return response


@app.exception_handler(Exception)
async def unexpected_error(request: Request, exc: Exception):
    return _error(request, 500, "INTERNAL_ERROR", "The request could not be completed.")


@lru_cache(maxsize=1)
def deps() -> service.Deps:
    return service.build_deps()


@app.get("/api/v1/health")
def health():
    d = deps()
    try:
        load_artifacts(d.settings.root / "ml" / "clustering" / "artifacts")
        model_status = "available"
    except Exception:
        model_status = "unavailable"
    return {"status": "ok", "crops": len(d.crops), "features_available": d.store.available(),
            "demo_mode": d.settings.demo_mode, "data_mode": "DEMO" if d.settings.demo_mode else "REAL",
            "environmental_clustering": model_status,
            "meteomatics_configured": bool(d.settings.meteomatics_user and d.settings.meteomatics_password)}


@app.post("/api/v1/analyze")
def analyze(req: AnalyzeRequest):
    try:
        result = service.analyze(req, deps())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    result["analysis_id"] = db.save_analysis(req.model_dump(), result)
    return result


@app.get("/api/v1/crops")
def crops():
    return service.crops_payload(deps())


@app.get("/api/v1/context")
def context():
    return regional_context.get_regional_context(deps().settings.root)


@app.get("/api/v1/weather")
def weather(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    return deps().weather_fn(lat, lon)


@app.get("/api/v1/analyses/{analysis_id}")
def get_analysis(analysis_id: str):
    record = db.load_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="analysis not found")
    return record


@app.get("/api/v1/layers/{name}.png")
def layer(name: str):
    if name not in LAYER_NAMES:                       # whitelist = no path tricks
        raise HTTPException(status_code=404, detail="unknown layer")
    f = deps().settings.layers_dir / f"{name}.png"
    if not f.is_file():
        raise HTTPException(status_code=404, detail="layer not available")
    return FileResponse(str(f), media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})


@app.get("/api/v1/layers/metadata")
def layer_metadata():
    path = deps().settings.layers_dir / "metadata.json"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="layer metadata not available")
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
        bounds = metadata.get("bounds")
        if isinstance(bounds, dict):
            for info in (metadata.get("layers") or {}).values():
                info.setdefault("bounds", bounds)
        return metadata
    except (OSError, ValueError):
        raise HTTPException(status_code=404, detail="layer metadata is invalid")


# Serve the farmer web app (and audio/) from the same server, last so API routes win.
if _settings.web_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_settings.web_dir), html=True), name="web")
