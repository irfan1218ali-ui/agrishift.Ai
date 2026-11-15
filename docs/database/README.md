# SQLite runtime database

The hackathon runtime uses SQLAlchemy with local SQLite. The default database URL is `sqlite:///data/agrishift.db`; the database is created at startup and ignored by Git/package tooling. Raw rasters and provider source files are never stored in SQLite.

Table definitions are in `apps/api/app/db.py`:

- `analysis_requests`: location, crop, water, farmer observations, priority, language, timestamp.
- `analysis_results`: linked request, feature/cluster references, response JSON, confidence and status.
- `dataset_metadata`: provider/product/version, observation period, resolution, checksum and metadata JSON.
- `model_runs`: model/schema versions, training timestamp, metrics JSON, artifact path.

`GET /api/v1/analyses/{analysis_id}` reads back the saved request and response. Tests cover table creation and write/read behavior. The older `database/` directory and PostGIS-related ADRs are preserved architecture artifacts and are not used by the MVP runtime.

## Ownership

- Owner: Backend engineering
- Inputs: Validated analysis requests and application metadata.
- Outputs: Local SQLite runtime schema and data dictionary documentation.
- Must not store: Raw rasters, provider credentials, or unconsented personal data.
