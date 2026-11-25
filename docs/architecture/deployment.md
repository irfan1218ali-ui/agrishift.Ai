# Deployment architecture (current and target)

The verified release runs locally: Next.js on loopback port 3000, FastAPI on loopback port 8000, and SQLite at `data/agrishift.db`. No Compose services, cloud resources, or remote deployment target are required by the MVP.

Do not deploy this checkout to a public host until TLS, a private expert `.env`, database backup/retention, restricted origins, and an approved hosting target are configured. No deployment credentials or target configuration are present in the current environment.

The earlier enterprise target below is a future option, not an implemented or deployed environment. Keep volumes ignored; use labeled software fixtures only; do not fabricate environmental outputs.

Staging uses separate Azure credentials/resource group; Vercel preview web; Azure Container Apps API/workers; managed PostgreSQL/PostGIS, Azure Cache for Redis, private Blob, managed identity, Key Vault, and Application Insights/Sentry. Use labeled software fixtures only; do not fabricate environmental outputs.

Production uses restricted web origins, isolated API/workers, private networking, TLS, managed identities, Key Vault, backup/restore drills, retention, and telemetry with sensitive geometry/credentials redacted. Public tile delivery must enforce authorization or publish reviewed generalized layers. GitHub Actions performs lint/schema/contract checks, dependency and secret scans, image builds, and gated deploys. Pin image digests and model versions; promote artifacts across environments. Roll back app and model independently. Set RPO/RTO and residency before production. No resources are provisioned here.
