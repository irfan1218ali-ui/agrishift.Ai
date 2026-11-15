# workers

Idempotent bounded async tasks with safe retries and observable status.

Owner: Backend (Area B).
Inputs: OpenAPI contracts, database repositories, and normalized source metadata.
Outputs: versioned APIs, jobs, and normalized business outputs.
Must not store: credentials, unreviewed private farmer data, or unrelated scientific data.
