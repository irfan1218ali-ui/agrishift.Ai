# ADR 0009: Regional versus field scale

Status: Accepted. Date: 2026-11-15.

Store native measurement support separately from display resolution. SMAP, GPM and NASA POWER are regional context; Meteomatics forecasts are provider/product scale dependent. Landsat is field-oriented imagery subject to QA/revisit, while SRTM/NASADEM supplies terrain context. Never present resampled coarse data as field truth; disclose support, coverage and uncertainty.
