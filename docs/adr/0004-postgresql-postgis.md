# ADR 0004: PostgreSQL and PostGIS

Status: Accepted. Date: 2026-11-14.

Use PostgreSQL for transactional entities and PostGIS for field boundaries/spatial queries. Keep large rasters in object storage with catalog metadata in PostgreSQL. Use explicit SRIDs and query-driven indexes.
