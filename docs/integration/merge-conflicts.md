# Step 2B merge conflict record

The Step 2A branch was merged with `--no-ff` into `hackathon/step-2b-integration`. Git reported 14 conflicting paths. No application files conflicted.

| Paths | Conflict cause | Selected version and edits | Reason |
|---|---|---|---|
| `data/catalog/data-status.csv` | Step 1 recorded the initial six-source audit; Step 2A recorded the later Landsat 9 discovery and processed status. | Step 2A source evidence was retained, then normalized to one row per locked source. The actual Landsat 9 ID replaced the superseded Landsat 8 expectation. | Keep the validated scene and retain the six-source MVP boundary. |
| `data/layers/metadata.json` | Step 1 described a standalone slope layer; Step 2A added the three Landsat overlays and shared extent. | Step 2A metadata retained; API adds the shared extent to per-layer response metadata. | Serve the four real overlays with the Step 2A bounds and source metadata. |
| `data/manifests/{gpm-files,landsat-files,meteomatics-files,power-files,smap-files,terrain-files}.csv` | Step 2A supplied richer source inventories and actual Landsat 9 evidence. | Step 2A manifests retained. | Preserve checksums, observed source details, and processing evidence. |
| `docs/data/source-inventory.md` | Step 1 inventory predates the discovered Landsat 9 bundle and generated products. | Step 2A inventory retained; Step 1 reports remain historical. | Present current measured sources without erasing the earlier audit record. |
| `ml/clustering/{README.md,evaluate.py,predict.py,prepare_features.py,train_kmeans.py}` | Step 1 guarded trainer had no real feature inputs; Step 2A now supplies real features and fitted artifacts. | Step 2A model pipeline retained. The training code now records `sklearn.__version__` rather than the unrelated `joblib.__version__`. Artifact JSON files are stored byte-for-byte so their manifest checksums remain valid. | Use the trained real model and keep metadata/checksum provenance accurate. |

## Additional scientific corrections

- The Step 2A GPM summary inferred rainy days, peak daily rainfall, and a weekly total from one weekly mean-rate map. Those derived measures are unsupported; runtime data, feature generation, tests, and documentation now expose only the weekly mean daily rate and spatial cell-rate range.
- The first K-Means manifest mislabeled the installed Joblib version as the scikit-learn version. The artifacts deserialize as scikit-learn 1.9.1 / Joblib 1.6.0; the manifest and runtime pins now match those artifact versions.
- The relative low-lying indicator is described as terrain context and requires local drainage/field inspection. It is not flood-risk classification.
- No raw rasters or credentials are tracked in this merge.
