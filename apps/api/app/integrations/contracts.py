"""Shared six-source adapter contracts; no network calls are performed here."""
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class ProviderHealth(StrEnum):
    AVAILABLE = "available"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class ProviderConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider_id: str
    timeout_seconds: float = Field(default=30, gt=0, le=300)
    max_retries: int = Field(default=3, ge=0, le=10)
    cache_ttl_seconds: int = Field(default=0, ge=0)
    username: SecretStr | None = None
    password: SecretStr | None = None
    base_url: str | None = None


class SpatialQuery(BaseModel):
    bbox: tuple[float, float, float, float] | None = None
    geometry: dict[str, Any] | None = None
    crs: str = "EPSG:4326"


class TemporalQuery(BaseModel):
    start_datetime: datetime
    end_datetime: datetime


class DatasetQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset_id: str
    spatial: SpatialQuery | None = None
    temporal: TemporalQuery | None = None
    variables: list[str] = Field(default_factory=list)


class DataAsset(BaseModel):
    asset_id: str
    uri: str
    provider: str
    product: str
    original_filename: str | None = None
    checksum_sha256: str | None = None
    license_reference: str | None = None


class ObservationMetadata(BaseModel):
    provider: str
    product: str
    version: str | None = None
    observed_at: datetime | None = None
    retrieved_at: datetime | None = None
    spatial_resolution: str | None = None
    temporal_resolution: str | None = None
    units: dict[str, str] = Field(default_factory=dict)
    quality_status: str = "unknown"
    source_metadata: dict[str, Any] = Field(default_factory=dict)


class RasterMetadata(ObservationMetadata):
    crs: str | None = None
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)
    transform: list[float] | None = None
    nodata: float | str | None = None
    scale: list[float] = Field(default_factory=list)
    offset: list[float] = Field(default_factory=list)


class TimeSeriesResponse(BaseModel):
    metadata: ObservationMetadata
    records: list[dict[str, Any]] = Field(default_factory=list)


class ProviderError(Exception):
    """Normalized safe adapter error; omit credentials and private request bodies."""
    code = "PROVIDER_ERROR"

    def __init__(self, message: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.retryable = retryable


class RateLimitError(ProviderError):
    code = "RATE_LIMITED"


class AuthenticationError(ProviderError):
    code = "AUTHENTICATION_FAILED"


class DataUnavailableError(ProviderError):
    code = "DATA_UNAVAILABLE"


class DataAdapter(Protocol):
    provider_id: str
    async def health(self) -> ProviderHealth: ...


class RasterDataAdapter(DataAdapter, Protocol):
    async def inspect_asset(self, asset: DataAsset) -> RasterMetadata: ...


class TimeSeriesDataAdapter(DataAdapter, Protocol):
    async def query(self, request: DatasetQuery) -> TimeSeriesResponse: ...
