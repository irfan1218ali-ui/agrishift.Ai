Domain service boundaries: rotation engine, report service, notification service, and model inference. Keep agronomic rules separate from HTTP and storage; do not add placeholder executable services before the relevant phase.

Owner: Backend (Area B).
Inputs: OpenAPI contracts, database repositories, and normalized source metadata.
Outputs: versioned APIs, jobs, and normalized business outputs.
Must not store: credentials, unreviewed private farmer data, or unrelated scientific data.
