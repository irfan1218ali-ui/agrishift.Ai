# NASA GPM IMERG precipitation validation

The supplied NASA Giovanni export is a seven-day, time-averaged daily precipitation-rate map for 2025-09-01 through 2025-09-07. It contains 12 valid cells at about 0.1 degree, with units mm/day.

| Statistic | Value | Meaning |
|---|---:|---|
| Regional mean daily rate | 5.465 mm/day | Mean across the supplied grid and weekly average |
| Minimum cell mean rate | 4.050 mm/day | Minimum spatial cell average over the same period |
| Maximum cell mean rate | 6.763 mm/day | Maximum spatial cell average over the same period |

This file is not a daily series. It cannot identify rainy-day counts or peak daily rainfall. The application therefore exposes the mean daily rate and source dates only; it does not report those unsupported daily measures or a weekly total. GPM is regional satellite context, not a farm rain gauge.
