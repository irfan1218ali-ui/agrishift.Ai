"""SMAP adapter protocol; local asset inspection is future work."""
from typing import Protocol
from ..contracts import RasterDataAdapter

class SmapDataAdapter(RasterDataAdapter, Protocol):
    """Normalizes locally registered SMAP assets without implying field-scale truth."""
