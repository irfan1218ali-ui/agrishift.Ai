from typing import Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """POST /api/v1/analyze body (plan section 8.1)."""
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    radius_m: int = Field(default=150, ge=10, le=5000)
    current_crop: str = Field(min_length=1, max_length=40)
    previous_crop: Optional[str] = "unknown"
    water_source: Literal["canal", "tubewell", "rain"]
    water_amount: Literal["low", "medium", "high"]
    salinity: Literal["yes", "no", "unknown"]
    waterlogging: Literal["yes", "no", "unknown"]
    priority: Literal["save_water", "improve_soil", "balanced"] = "balanced"
    language: Literal["sd", "ur", "en"] = "en"
