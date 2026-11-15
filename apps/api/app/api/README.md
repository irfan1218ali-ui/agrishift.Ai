Versioned HTTP routing boundary. Route handlers validate, authorize, call services, and serialize contracts; provider and domain logic stay out of route modules.

Owner: Backend (Area B).
Inputs: OpenAPI contracts, database repositories, and normalized source metadata.
Outputs: versioned APIs, jobs, and normalized business outputs.
Must not store: credentials, unreviewed private farmer data, or unrelated scientific data.
