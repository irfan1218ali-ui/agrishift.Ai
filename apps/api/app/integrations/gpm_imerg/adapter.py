"""GPM IMERG adapter protocol; no acquisition or raster inspection is implemented."""
from typing import Protocol
from ..contracts import RasterDataAdapter

class GpmImergDataAdapter(RasterDataAdapter, Protocol):
    """Normalizes local IMERG assets while preserving run type, units and temporal support."""
