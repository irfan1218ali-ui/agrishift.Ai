# NASA POWER Agroclimatology Validation Report (Step 2A)

## 1. Executive Summary

This report documents the validation and climatological summarization of 11 continuous years (2015-01-01 through 2025-12-31) of daily NASA POWER meteorological records at the Hyderabad pilot location ($25.396^\circ\text{N}, 68.3578^\circ\text{E}$).

---

## 2. Dataset Properties & Provenance

- **Provider**: NASA Prediction of Worldwide Energy Resources (POWER) Project.
- **Data Source Models**: NASA GMAO MERRA-2 assimilation model and CERES SYN1deg satellite solar radiance products.
- **Physical File**: `data/api-samples/nasa-power/POWER_Point_Daily_20150101_20251231_025d40N_068d36E_LST (1).csv`
- **Time Standard**: Local Solar Time (LST)
- **Native Resolution**: $0.5^\circ \text{ latitude} \times 0.625^\circ \text{ longitude}$ grid cell average
- **Missing Value Marker**: `-999.0` (validated 0 missing records in the series)
- **Continuous Date Range**: 4,018 consecutive days from 2015-01-01 to 2025-12-31 without a single gap or duplicate.

---

## 3. Parameter Validation

| Parameter Code | Description | Provider Units | Validation Status |
| :--- | :--- | :--- | :--- |
| `T2M` | Temperature at 2 Meters | $^{\circ}\text{C}$ | VALIDATED |
| `T2M_MAX` | Daily Maximum Temperature at 2 Meters | $^{\circ}\text{C}$ | VALIDATED |
| `T2M_MIN` | Daily Minimum Temperature at 2 Meters | $^{\circ}\text{C}$ | VALIDATED |
| `RH2M` | Relative Humidity at 2 Meters | $\%$ | VALIDATED |
| `WS2M` | Wind Speed at 2 Meters | $\text{m}/\text{s}$ | VALIDATED |
| `ALLSKY_SFC_SW_DWN` | All-Sky Surface Shortwave Downward Irradiance | $\text{MJ}/\text{m}^2/\text{day}$ | VALIDATED |
| `PRECTOTCORR` | Precipitation Corrected | $\text{mm}/\text{day}$ | VALIDATED |

---

## 4. Multi-Year Climatological Aggregations

Overall 11-Year Baseline Metrics:
- **Mean Temperature ($T_{2\text{m}}$)**: $27.30^\circ\text{C}$
- **Mean Relative Humidity ($RH_{2\text{m}}$)**: $46.84\%$
- **Mean Wind Speed ($WS_{2\text{m}}$)**: $3.27\text{ m}/\text{s}$
- **Mean Solar Irradiance**: $19.66\text{ MJ}/\text{m}^2/\text{day}$
- **Annual Average Rainfall**: $317.64\text{ mm}$

### Monthly Climatology Table

| Month | $T_{\text{mean}}\ (^{\circ}\text{C})$ | $T_{\text{max}}\ (^{\circ}\text{C})$ | $T_{\text{min}}\ (^{\circ}\text{C})$ | Heat Days $\ge 40^{\circ}\text{C}$ | Rain ($\text{mm}$) | $RH$ ($\%$) | Wind ($\text{m}/\text{s}$) | Solar ($\text{MJ}/\text{m}^2/\text{day}$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Jan** | 18.06 | 25.41 | 10.98 | 0.0 | 4.88 | 39.51 | 2.50 | 14.86 |
| **Feb** | 21.68 | 30.16 | 13.56 | 0.0 | 3.52 | 34.25 | 2.65 | 18.01 |
| **Mar** | 26.69 | 34.98 | 18.57 | 3.3 | 2.92 | 30.93 | 2.91 | 21.57 |
| **Apr** | 31.81 | 40.36 | 23.63 | 17.9 | 1.95 | 32.18 | 3.26 | 24.36 |
| **May** | 34.78 | 42.51 | 27.67 | 27.1 | 5.37 | 44.52 | 4.70 | 25.32 |
| **Jun** | 35.12 | 41.21 | 29.80 | 21.8 | 14.28 | 54.34 | 5.17 | 24.38 |
| **Jul** | 33.36 | 38.46 | 29.21 | 9.5 | 88.08 | 63.85 | 4.67 | 20.89 |
| **Aug** | 31.87 | 36.73 | 27.99 | 1.5 | 114.94 | 67.57 | 4.41 | 19.34 |
| **Sep** | 31.60 | 37.30 | 26.79 | 3.5 | 60.91 | 61.27 | 3.39 | 20.31 |
| **Oct** | 29.74 | 36.82 | 23.11 | 3.2 | 10.14 | 47.96 | 2.12 | 18.84 |
| **Nov** | 24.89 | 31.79 | 18.17 | 0.0 | 3.65 | 42.41 | 2.06 | 15.19 |
| **Dec** | 19.46 | 27.00 | 12.35 | 0.0 | 7.00 | 41.49 | 2.21 | 13.91 |

---

## 5. Limitations & Caveats

1. **Spatial Scale**: NASA POWER data represents a $0.5^\circ \times 0.625^\circ$ grid cell average ($\approx 50\text{ km} \times 60\text{ km}$); local microclimates or farm-level topography can deviate.
2. **Reanalysis Source**: Values derive from numerical assimilation (MERRA-2) and satellite radiative transfer models, not physical ground station thermometers.
