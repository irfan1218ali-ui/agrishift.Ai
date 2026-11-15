# Meteomatics Weather API

- **Observed response:** saved hourly JSON with `t_2m:C`, `precip_1h:mm`, `relative_humidity_2m:p`, and `wind_speed_10m:ms`; generated 2026-11-15 07:20:04 UTC for one Hyderabad-area coordinate.
- **Status:** parser and daily summaries validated. No live API request was made; credentials are absent. Sanitized demo copy removes the account identifier.
- **Processing:** joined by UTC timestamp and summarizes daily maximum/minimum temperature, rainfall sum, mean humidity, and maximum wind. Validity dates and expiry are returned.
- **Mode behavior:** a saved sample is available only in demo mode and has `is_sample=true`, `is_live=false`; real mode requires live success or reports unavailable.
- **Limitations:** forecast is time-bound, not historical climate truth, and is not part of crop-rotation scoring.
