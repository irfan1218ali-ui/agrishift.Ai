"""NASA POWER API adapter protocol; makes no requests."""
from typing import Protocol
from ..contracts import TimeSeriesDataAdapter

class NasaPowerAdapter(TimeSeriesDataAdapter, Protocol):
    """Normalizes historical regional climate responses after access is approved."""
