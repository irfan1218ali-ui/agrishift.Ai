# Demo and judging points

- Reuses the supplied project code and crop-rotation engine rather than introducing a replacement system.
- Keeps crop recommendations rule-based and reserves K-Means for unsupervised environmental grouping.
- Uses NASA POWER, SMAP, GPM, SRTM, and a saved Meteomatics response only for the roles supported by the actual data.
- Provides an operational multilingual interface, analysis persistence, regional context endpoint, source-aware slope map, and saved-analysis retrieval.
- Enforces real/demo separation, conspicuous demo wording, request trace IDs, local SQLite, and non-fabrication when critical features are missing.
- Clearly identifies data gaps: missing Landsat scene assets, coarse regional pixels, and mismatched observation periods.
- Does not claim that a passing UI demo proves real agronomic performance. The scientific readiness gate is explicit.
