# Final ZIP contents and exclusions

`python scripts/package_release.py` creates `agrishift-ai-hackathon-final.zip` in the parent workspace and writes a SHA-256 sidecar. The packager validates required runtime assets, a sanitized Meteomatics sample, blank example credentials, and refuses to overwrite an existing archive or checksum.

Included: application source, existing frontend, rotation engine, scripts, tests, documentation, dependency files, `.env.example`, manifests, supplied placeholder features for the explicit demo, sanitized saved-weather sample, real SRTM slope PNG/metadata, and sanitized regional context JSON.

Excluded: `.git`, virtual environments, caches, logs, databases, `.env`, credentials, raw Landsat/SMAP/GPM/SRTM files, source POWER CSV, unsanitized Meteomatics response, intermediate rasters, and model artifacts. Model artifacts are absent because no model was trained.

The package is a reviewable demo bundle, not a scientifically complete release. `README_FINAL_DEMO.md` and `docs/demo/known-limitations.md` state the `NOT READY` verdict and the exact Landsat blocker.
