# NASA GPM IMERG

- **Product:** GPM_3IMERGDF V07 Final Run.
- **Purpose/variable:** daily mean precipitation rate; derive rainfall totals, heavy-rain and wet/dry spell indicators only after unit/time checks.
- **Unit/temporal/spatial:** mm/day; daily; 0.1° (approximately 10 km), regional estimate.
- **Access/status:** NASA Giovanni; validation pending. Two export files are present at the root of `data/raw/gpm-imerg/`; their contents have not been inspected.
- **Storage:** keep current files and names untouched. Expected organized copy path, only after a documented verified copy: `data/raw/gpm-imerg/NASA_GPM_3IMERGDF_V07_Hyderabad_2025-09-01_2025-09-07/original/`.
- **Processing/quality:** later validate actual metadata, units, CRS, dates, NoData, Final Run identity and checksums; do not mix run types.
- **Limitations/model/map:** not an individual field rain gauge. Candidate regional rainfall feature/context layer with date, run and resolution disclosed. No validation result is claimed.
