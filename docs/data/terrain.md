# NASA SRTM or NASADEM

- **Purpose/variables:** elevation; future slope, aspect, flow direction/accumulation, terrain wetness and relative runoff/erosion context.
- **Product/resolution:** choice and resolution not selected; record actual product metadata before use.
- **Access/status:** pending; no data downloaded.
- **Storage:** expected `data/raw/terrain/NASA_SRTM_or_NASADEM_Hyderabad/original/`.
- **Processing/quality:** later validate CRS, vertical datum, void/NoData and source version; derive slope/flow with recorded algorithm/CRS and checksums. Cache terrain derivatives by version.
- **Limitations/model/map:** mostly static topographic context, not direct crop condition or measured erosion. Candidate model/map context only after validated coverage.
