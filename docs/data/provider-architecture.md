# Active provider and file adapter architecture

Only six adapters are active: `SmapDataAdapter`, `GpmImergDataAdapter`, `LandsatDataAdapter`, `TerrainDataAdapter`, `NasaPowerAdapter`, and `MeteomaticsAdapter`. SMAP, GPM, Landsat and terrain consume local immutable files or later object-storage assets; automated acquisition is not required for MVP. NASA POWER and Meteomatics are the only active runtime external API adapters.

Shared contracts: `ProviderConfiguration`, `ProviderHealth`, `DataAsset`, `DatasetQuery`, `SpatialQuery`, `TemporalQuery`, `ObservationMetadata`, `RasterMetadata`, `TimeSeriesResponse`, `ProviderError`, `RateLimitError`, `AuthenticationError`, and `DataUnavailableError`.

Every adapter eventually validates configuration/request, applies bounded timeout/retry and caching, normalizes units/errors, preserves source and observation metadata, reports spatial/temporal resolution and quality, and emits lineage. Inject HTTP/clock/storage dependencies for tests. Meteomatics credentials stay backend-only. No full provider behavior or network calls are implemented.
