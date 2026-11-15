"""SRTM/NASADEM adapter protocol; product choice remains pending."""
from typing import Protocol
from ..contracts import RasterDataAdapter

class TerrainDataAdapter(RasterDataAdapter, Protocol):
    """Normalizes selected terrain product metadata; no source is selected yet."""
