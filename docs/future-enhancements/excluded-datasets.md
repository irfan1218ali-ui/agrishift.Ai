# Excluded datasets and providers — Future, not part of MVP

The following sources are explicitly outside the six-source MVP. They must not have active adapters, runtime dependencies, environment variables, catalog status rows, or integration tests. Reconsider only through a documented use case/ADR, license and cost review, spatial/temporal suitability analysis, validation plan, and owner assignment.

- Sentinel-2
- Harmonized Landsat Sentinel-2 (HLS)
- ECOSTRESS
- MODIS
- VIIRS
- GLDAS
- NLDAS
- ERA5
- FAO GAEZ
- USDA Web Soil Survey
- SSURGO
- STATSGO2
- CropScape CDL
- PRISM
- NAIP
- NLCD
- CoCoRaHS
- USGS NWIS
- OpenET
- LANDFIRE
- GEDI
- USDA QuickStats
- USDA AMS Market News

NASA CMR/AppEEARS automation, Microsoft Planetary Computer STAC and Copernicus integrations are also future-only supporting integrations, not MVP runtime requirements. Historical ADRs may discuss prior options; this file is the current scope authority.
