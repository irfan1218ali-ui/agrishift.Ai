# Six-source MVP strategy

The MVP fixes six source families to keep integration and validation work manageable for four owners. They cover regional soil moisture, rainfall, field imagery/temperature, terrain, historical climate, and short-term forecast.

| Source | Responsibility | Limits and controls |
|---|---|---|
| NASA SMAP SPL4SMGP | Surface/root-zone moisture context, anomalies, pre-sowing moisture and seasonal reliability | Approx. 9 km is regional; preserve observation time and native scale. Never imply field-sensor precision or upscale into field truth. |
| NASA GPM IMERG GPM_3IMERGDF V07 Final | Daily rate, weekly/monthly accumulation, wet/dry spells, heavy rain and anomalies | 0.1° (~10 km) regional estimate. Keep units/time interval explicit; do not mix Early/Late/Final runs. |
| USGS Landsat 8/9 C2 L2 | Reflectance, surface temperature, NDVI/EVI/NDWI/NDMI/BSI, bare soil, vegetation and image features | Apply QA_PIXEL before interpretation and product scale/offset; retain scene/cloud metadata. Display pixels do not change source resolution. |
| NASA SRTM or NASADEM | Elevation, slope, aspect, flow, runoff/erosion context | Mostly static; document selected product, resolution, datum, processing and uncertainty. |
| NASA POWER API | Historical temperature, precipitation context, humidity, wind, solar, GDD/heat indicators | Regional climate context, not a farm station. Preserve parameter, units and aggregation. |
| Meteomatics Weather API | Current conditions, hourly forecast and short-term rain/temperature/humidity/wind/alerts | Forecast lead time and provider uncertainty matter. Credentials stay backend-only; confirm terms/products. |

SMAP, GPM and POWER overlap in water/climate context but have different observation mechanisms, temporal supports and scales; they are complementary evidence, not interchangeable values. Landsat covers spectral condition on clear acquisition dates. Terrain adds static topographic context. Meteomatics adds near-term forecast, not climatology.

Limitations include data gaps, clouds, revisit timing, coarse pixels, unknown irrigation/soil, short test periods and sparse labels. Missing inputs must remain missing or lower confidence. Future expansion requires a user need, license/terms review, spatial/temporal fit, operational cost, validation plan and owner assignment.
