# Candidate indicator specifications

These are names and processing requirements only. No values are calculated or populated during restructure. Implementations must declare units, source bands/variables, quality masks, temporal window/reducer, CRS, native support, NoData, lineage and version.

## Landsat C2 Level-2

Candidate outputs: NDVI, EVI, NDWI, NDMI, Bare Soil Index, surface temperature, vegetation-cover percentage, vegetation anomaly, bare-soil percentage and water-related indicators. Inputs include SR_B2–SR_B7, ST_B10 and QA_PIXEL. Apply product scale/offset before indices; apply documented QA_PIXEL cloud/shadow/snow/water policy; record scene/date and valid-pixel coverage. No anomaly baseline or masks are assumed to exist.

## SMAP

Candidate summaries: surface/root-zone moisture mean, percentile, anomaly, consecutive low-moisture periods and seasonal moisture reliability. Preserve product variable/unit/time metadata and nominal ~9 km regional support; do not interpret as field sensor readings.

## GPM IMERG

Candidate summaries: daily rate, weekly/monthly accumulation, maximum daily amount, consecutive dry/wet days, heavy-rain days and rainfall anomaly. Verify mm/day semantics, product run, temporal coverage, nodata and aggregation window before summing or comparing.

## SRTM/NASADEM terrain

Candidate layers: elevation, slope, aspect, flow direction/accumulation, relative runoff, terrain wetness and relative erosion exposure. Record selected product, vertical datum, algorithms, projection and static nature. These are terrain proxies, not measured runoff/erosion.

## NASA POWER and Meteomatics

POWER candidate summaries: mean/max/min temperature, heatwave days, GDD, humidity/wind/solar summaries and seasonal climate indicators. Meteomatics candidate summaries: current conditions, hourly forecast, short-term rainfall/heat/wind risk and alerts. Preserve units, API parameter/product, request and retrieval time, forecast issue/valid times and caching window. Do not generate sample values in this stage.
