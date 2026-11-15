# Security policy

Do not disclose security issues publicly. Contact maintainers through a private channel established by the project owner; this repository currently has no published security contact.

Never commit credentials, tokens, private farmer data, raw Earth observation data, or model artifacts. Store local secrets in ignored environment files and deployed secrets in a managed secret store. Rotate credentials that are accidentally exposed and follow the repository owner's incident process for history cleanup.

Field boundaries and farmer records are sensitive. Apply least privilege, purpose limitation, encryption in transit and at rest, access logging, retention limits, and explicit consent before collecting or sharing them. See [data privacy](docs/security/data-privacy.md).

This is an architecture foundation; no deployed service or supported release exists yet.
