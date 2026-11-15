# Geospatial resolution policy

## Source scale

Field-oriented imagery comes from Landsat 8/9 C2 L2 subject to pixel support, acquisition date, clouds, QA and metadata. SRTM/NASADEM is terrain context, not crop condition. SMAP and GPM IMERG are regional products; NASA POWER is regional climate context; Meteomatics is forecast context with product-dependent support. Record native resolution, temporal support, coverage and quality for each layer.

Never upscale coarse regional observations and call them field-scale truth. A tile's display resolution is separate from measurement resolution. Zonal summaries disclose how many source pixels support a field estimate and report insufficient coverage when support is poor.

## Processing sequence and policy

Field polygon → asset/API lookup → source validation → quality masking → clipping → CRS validation → justified reprojection → temporal aggregation → resolution-aware harmonization → indicators → COG → tiles → zonal statistics → model features.

Use EPSG:4326 for stored/interchange field geometry. Retain each raster CRS, transform and resolution; choose a projected CRS for area/distance only where justified. Do not force all rasters into one resolution. Use nearest-neighbor for categorical masks; select documented continuous resampling based on variable semantics. Never interpolate across NoData. Record NoData, scale/offset, QA logic, source checksum, processing code/config, output CRS, display resolution and lineage.

For Landsat C2 L2 apply scale and offset from product documentation/metadata before scientific interpretation. Apply QA_PIXEL cloud, shadow, snow and water bits with product-versioned policy. Temporal summaries record UTC window, reducer and valid-observation count. Do not calculate outputs until source files have been inspected.
