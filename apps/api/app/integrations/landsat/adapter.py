"""Landsat C2 L2 adapter protocol; no bundle processing is implemented."""
from typing import Protocol
from ..contracts import RasterDataAdapter

class LandsatDataAdapter(RasterDataAdapter, Protocol):
    """Normalizes scene metadata and QA references without opening scene files."""
