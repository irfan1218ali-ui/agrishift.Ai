# SQLite data dictionary

The active ORM-free SQLAlchemy Core table definitions are in `apps/api/app/db.py`. All analysis rows are local pilot records; the app currently has guest access and does not store accounts or exact farmer identity.

| Table | Key columns | Purpose |
|---|---|---|
| `analysis_requests` | `id`, `latitude`, `longitude`, `radius_m`, `current_crop`, `previous_crop`, `water_source`, `water_level`, `salinity`, `waterlogging`, `priority`, `language`, `created_at` | Captures the user-provided analysis inputs |
| `analysis_results` | `id`, `request_id`, `feature_point_id`, `cluster_id`, `cluster_label`, `rotation_results_json`, `confidence_score`, `status`, `created_at` | Stores the complete response JSON and status; `request_id` is unique and references the request |
| `dataset_metadata` | `id`, `provider`, `product`, `version`, `observation_start`, `observation_end`, `source_resolution`, `validation_status`, `checksum`, `metadata_json` | Dataset provenance metadata; populated as validated sources are integrated |
| `model_runs` | `id`, `model_name`, `model_version`, `feature_schema_version`, `training_timestamp`, `metrics_json`, `artifact_path` | Model provenance; currently no trained K-Means run is present |

SQLite creates tables through `metadata.create_all()` at app startup and as needed on reads/writes. Database paths and files are ignored by Git and excluded from release ZIPs. There are no raster BLOBs or PostgreSQL/PostGIS dependencies in the active MVP database.
