# Meteomatics saved-response compatibility

The inspected saved JSON response was generated at `2026-11-15T07:20:04Z`, has status `OK`, and contains these four hourly parameters:

| Provider key | Normalized field | Unit |
|---|---|---|
| `t_2m:C` | `temperature_c` | °C |
| `precip_1h:mm` | `precipitation_mm` | mm per hour interval |
| `relative_humidity_2m:p` | `relative_humidity_percent` | percent |
| `wind_speed_10m:ms` | `wind_speed_ms` | m/s |

The response has one Hyderabad-area coordinate near 25.3966°N, 68.3574°E. The supplied sequence covers hourly timestamps from 2026-11-15 through 2026-11-22. The adapter joins records on normalized UTC timestamps, permits missing values as `null`, and summarizes each day as maximum/minimum temperature, accumulated hourly precipitation, mean humidity, and maximum wind speed.

The saved response is never marked live. It returns `is_live=false`, `is_sample=true`, and an expiry flag based on `valid_until` and the current UTC time. In real mode, missing credentials or a failed live request returns unavailable; it does not fall through to a saved sample. In explicit demo mode the sanitized `demo_sample.example.json` copy may be used. The shareable copy omits the provider response's account identifier. Do not distribute the unsanitized original response.
