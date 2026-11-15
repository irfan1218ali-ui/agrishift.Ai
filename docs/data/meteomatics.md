# Meteomatics Weather API

- **Purpose/variables:** current conditions, hourly forecast, rain, temperature, humidity, wind and weather alerts; exact products/parameters to be selected.
- **Resolution/temporal:** provider/product-dependent; preserve forecast issue time, valid time, lead time, units and coverage.
- **Access/status:** Meteomatics Weather API; access pending; no request made. Credentials must remain backend-only and be stored in a secret manager outside Git.
- **Storage:** only sanitized samples under `data/api-samples/meteomatics/`; do not store credentials or private farmer requests.
- **Processing/quality:** validate response schema, units, timestamps/time zone, missingness, forecast lead and provider errors; record retrieval/issue times and cache expiry.
- **Limitations/model/map:** forecast uncertainty and provider terms apply. Candidate short-term risk input and farmer-facing forecast layer, not historical climate truth.
