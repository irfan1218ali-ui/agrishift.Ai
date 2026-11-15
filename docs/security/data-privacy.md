# Data privacy and security baseline

Field boundaries, precise location, ownership, crop history, soil tests, financial/market data, and feedback can identify or expose farmers. Collect only necessary fields with informed purpose/consent; explain retention/sharing; separate identity from analytical identifiers where feasible. Enforce tenant authorization on every query and object-store access. Never log precise boundary coordinates or credentials.

Encrypt in transit and at rest. Use managed identities/secret stores in cloud; least privilege and scoped provider credentials; rotate credentials. Keep raw science and farmer data out of Git and public map tiles. Review field-derived layers/reports before sharing. Audit access, edits, export, deletion, admin actions, data processing, and model/recommendation versions with tamper-resistant retention.

Use signed short-lived private-object access. Define residency, retention, backup, deletion propagation, legal basis, and breach response before launch. Minimize telemetry and redact inputs. Separate development/staging/production. Threat modeling precedes authentication and map publication.
