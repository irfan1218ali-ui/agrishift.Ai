# NASA POWER saved daily data

- **Observed file:** `data/api-samples/nasa-power/POWER_Point_Daily_20150101_20251231_025d40N_068d36E_LST (1).csv`.
- **Status:** saved provider CSV parsed locally; no live network request was made. Header covers 2015-01-01 through 2025-12-31 in local solar time at 25.396°N, 68.3578°E, with a 0.5° × 0.625° MERRA-2 source region and `-999` fill values.
- **Variables/units:** T2M, T2M_MAX, T2M_MIN in °C; PRECTOTCORR in mm/day; RH2M in percent; WS2M in m/s; ALLSKY_SFC_SW_DWN in MJ/m²/day.
- **Processing:** daily rows were parsed; monthly TMax/TMin, average days with TMax ≥40°C, average monthly precipitation totals, and whole-period humidity/wind/solar means are in `docs/data/source-inventory.md`.
- **Limitations:** regional climate context, not a farm weather station. The saved CSV is not included in the demo ZIP; real feature builder can read it when locally available.
