# ADR 0008: Four data zones

Status: Accepted. Date: 2026-11-15.

Separate immutable raw inputs, reproducible interim products, validated processed outputs, and versioned model-ready features/labels. Scientific data stays out of Git; catalogs, manifests, schemas, README files and reviewed small fixtures remain trackable. Derivations never overwrite originals.
