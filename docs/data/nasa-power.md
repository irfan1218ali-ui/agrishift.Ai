# NASA POWER API

- **Purpose/variables:** historical Tmax/Tmin/Tmean, precipitation context, humidity, wind, solar radiation, growing degree days and heat indicators; parameter selection remains to be confirmed.
- **Resolution:** regional climate context; preserve parameter-specific temporal/spatial support from response metadata.
- **Access/status:** NASA POWER API; API access pending; no request made.
- **Storage:** sanitized response examples, if later approved, under `data/api-samples/nasa-power/`; raw API captures follow data policy and stay out of Git.
- **Processing/quality:** validate parameter names, units, fill values, dates, aggregation and API errors; retain request parameters and retrieval timestamp.
- **Limitations/model/map:** not a farm weather station. Candidate historical climate features and regional context layers, with source and period disclosed.
