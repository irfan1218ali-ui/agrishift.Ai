# Interactive map architecture

MapLibre GL JS is the browser renderer. The API provides field GeoJSON and a normalized layer catalog; authorized tile services resolve raster/vector tiles and metadata. Keep map rendering separate from geospatial processing and provider credentials.

Future responsibilities: current location with permission, place search, field polygon drawing/editing and area calculation, GeoJSON storage, satellite imagery, NDVI/EVI/NDWI, stress segmentation, regional soil-moisture context, rainfall, surface temperature, elevation/slope, forecasts, crop suitability, rotation scenarios, layer opacity, timeline, and clickable zone details.

Layer contract is in `docs/schemas/contracts.schema.json` (`TileLayerMetadata`) and includes id, name, category, source, type, tile URL, legend, opacity, observation/processing date, spatial/temporal resolution, confidence, coverage, attribution, metadata URL, and availability status. UI must display source/date/resolution/attribution and coverage/quality warnings; distinguish unavailable, stale, partial, and processing. Map pixel size must not imply measurement scale. Precise farmer boundaries and private layers require tenant auth and short-lived access.
