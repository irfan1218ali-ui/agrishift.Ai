# Step 2: Data, features, K-Means, SQLite results

## Verdict: NOT READY

There are real validated inputs for SRTM-derived slope, regional SMAP/GPM context, a NASA POWER CSV, and a saved Meteomatics response. The expected Landsat scene bundle contains no SR, ST, QA_PIXEL, or MTL files. Because Landsat is required for the six model features and field-level remote-sensing evidence, the real point-feature product cannot be generated. K-Means must not be trained without those real feature rows.

## Commands and observed outcomes

| Command | Outcome |
|---|---|
| `python scripts/data/build_manifests.py` | Passed; SMAP 112, GPM 2, terrain 2, Landsat scene assets 0, POWER 7 variable records, Meteomatics 4 parameter records |
| `python scripts/data/build_regional_context.py` | Passed; validated context-only SMAP and GPM summary; source periods are not aligned |
| `python scripts/data/build_terrain_overlay.py` | Passed; produced slope raster/PNG/metadata with the measured values in `docs/data/source-inventory.md` |
| `python scripts/build_real_features.py` | Stopped safely; required Landsat `SR_B2` asset not found; no `features.json` written |
| `python ml/clustering/train_kmeans.py` | Stopped safely; real feature file absent; no artifacts or metrics written |
| `python -m pytest -q` | 69 passed, 1 third-party deprecation warning |
| `ruff check .` | Passed |
| `python -m compileall -q -x '\\.venv' .` | Passed |

The exact measured data, units, source periods, and missing inputs are in `docs/data/source-inventory.md`. The K-Means code requires at least 20 complete distinct real points and features NDVI, NDMI, BSI, surface temperature, elevation, and slope. It scales features, evaluates k=2, 3, and 4 where possible, and writes actual metrics only after successful evaluation. No k value, silhouette score, Davies-Bouldin score, or cluster profile is reported because no training run occurred.

SQLite tables `analysis_requests`, `analysis_results`, `dataset_metadata`, and `model_runs` are defined, initialized, and covered by persistence tests. A live demo request was saved and retrieved successfully. Model and dataset metadata tables remain available for later population; no model-run row is fabricated.

## Remaining critical tests

The test suite verifies Landsat math/QA helper formulas and missing-input behavior, but no real Landsat image could be run through raster QA, index, thermal, or overlay processing. No 20-point feature schema, reproducibility, cluster metrics, profile-label, or actual K-Means acceptance run is possible until the expected scene assets arrive. Thus passing software checks do not mean the Step 2 data/ML acceptance criteria passed.
