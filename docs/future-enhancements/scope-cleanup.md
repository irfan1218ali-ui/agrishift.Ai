# Scope cleanup record

The prior foundation had inert provider stubs for NASA CMR/AppEEARS, Copernicus, Microsoft Planetary Computer, HLS, MODIS/VIIRS, ECOSTRESS, GLDAS, ERA5, FAO GAEZ, local farmer/soil/market adapters, and a flat set of six-source placeholders. It also had raw-data/geospatial placeholder folders for non-MVP sources.

Those source modules contained module documentation only and no provider behavior. Six source-specific adapter boundaries now live in their own packages. Non-MVP stubs and README-only raw/geospatial placeholder folders were removed from active directories after a timestamped backup. No GPM or SMAP scientific files were removed, moved, renamed, or processed. Useful excluded-source names and expansion criteria remain in `excluded-datasets.md`.
