"""Meteomatics weather API adapter protocol; makes no requests."""
from typing import Protocol
from ..contracts import TimeSeriesDataAdapter

class MeteomaticsAdapter(TimeSeriesDataAdapter, Protocol):
    """Normalizes forecast/current data while preserving issue and valid times."""
