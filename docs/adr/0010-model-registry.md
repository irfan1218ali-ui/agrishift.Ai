# ADR 0010: Model registry and versioning

Status: Accepted. Date: 2026-11-14.

Version immutable model artifacts alongside feature schemas, dataset manifests, metrics, calibration, and explanation metadata. Start with object storage plus relational metadata; adopt MLflow if lifecycle needs justify it. Never replace a deployed artifact in place.
