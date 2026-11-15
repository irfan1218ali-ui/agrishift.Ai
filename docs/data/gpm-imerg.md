# NASA GPM IMERG

- **Product:** GPM_3IMERGDF V07 Final Run.
- **Purpose/variable:** supplied asset is a weekly time-averaged daily precipitation rate; it does not support daily totals, rainy days, or maximum daily rainfall.
- **Unit/temporal/spatial:** mm/day; daily; 0.1° (approximately 10 km), regional estimate.
- **Access/status:** two matching exports were inspected: one NetCDF and one GeoTIFF. Their units are `mm/day`, grid is EPSG:4326 at about 0.1°, and the NetCDF identifies the V07 Final Run weekly average.
- **Storage:** source files retain their original names in `data/raw/gpm-imerg/`; checksum and metadata records are in `data/manifests/gpm-files.csv`.
- **Observed summary:** 12 valid cells; mean 5.4650 mm/day; cell means range 4.0500–6.7629 mm/day; 2025-09-01 through 2025-09-07 UTC.
- **Limitations/model/map:** coarse regional context, not an individual field rain gauge. The supplied weekly aggregate cannot be expanded into daily series or summed into a verified weekly total.
