Alembic migrations are intentionally not generated until Phase 1 entity scope and PostGIS deployment choices are reviewed. Avoid one oversized initial schema migration.

Owner: Backend (Area B).
Inputs: OpenAPI contracts, database repositories, and normalized source metadata.
Outputs: versioned APIs, jobs, and normalized business outputs.
Must not store: credentials, unreviewed private farmer data, or unrelated scientific data.
