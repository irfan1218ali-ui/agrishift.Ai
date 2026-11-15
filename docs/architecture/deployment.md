# Deployment architecture (target)

Local Compose provides PostGIS and Redis only. Run web/API locally during Phase 1. Keep volumes ignored; use local object storage during development and no real farmer data.

Staging uses separate Azure credentials/resource group; Vercel preview web; Azure Container Apps API/workers; managed PostgreSQL/PostGIS, Azure Cache for Redis, private Blob, managed identity, Key Vault, and Application Insights/Sentry. Use labeled software fixtures only; do not fabricate environmental outputs.

Production uses restricted web origins, isolated API/workers, private networking, TLS, managed identities, Key Vault, backup/restore drills, retention, and telemetry with sensitive geometry/credentials redacted. Public tile delivery must enforce authorization or publish reviewed generalized layers. GitHub Actions performs lint/schema/contract checks, dependency and secret scans, image builds, and gated deploys. Pin image digests and model versions; promote artifacts across environments. Roll back app and model independently. Set RPO/RTO and residency before production. No resources are provisioned here.
