# NASA SRTM terrain

- **Observed product:** NASA SRTMGL1 V003 DEM and NUMNC companion at `data/raw/terrain/NASA_SRTM_or_NASADEM_Hyderabad/`.
- **DEM metadata:** 1,261 × 1,261 cells; EPSG:4326; approximate bounds 68.1999–68.5501°E and 25.1999–25.5501°N; nominal 30 m; elevation in metres; NoData -32768.
- **Status:** DEM and companion metadata inspected; a reprojection-aware slope raster, PNG overlay, and metadata were generated. Checksums are in `data/manifests/terrain-files.csv`.
- **Derived slope:** 1,582,752 valid cells; 0–28.8742°; mean 2.2768°; display range p02–p98 0.4404–6.4861°. UTM zone 42N at 30 m was used for gradient calculation.
- **Limitations:** slope is static terrain context, not a drainage, waterlogging, or crop-condition diagnosis. NUMNC was not treated as elevation; flow direction/accumulation and hydrology are not implemented.
