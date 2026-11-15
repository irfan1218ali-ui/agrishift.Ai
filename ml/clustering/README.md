# Environmental condition clustering

K-Means is an optional environmental grouping tool. It does not recommend crops,
predict yield, or diagnose crop health. The crop-rotation service remains rule-based.

## Input and safeguards

The trainer reads only `data/features/features.json`; it never falls back to
`features.example.json` and never fills missing feature values. It requires at
least 20 complete observations at 20 distinct coordinates. Each observation must
have NDVI, NDMI, BSI, surface temperature, elevation, and slope.

The trainer standardizes those six features and evaluates k=2, 3, and 4 where the
sample supports them. It saves actual silhouette scores, Davies-Bouldin indices,
and cluster sizes only after a successful run. A candidate needs expert review.
Neutral cluster names are descriptive environmental labels, not agronomic verdicts.

## Commands

```powershell
python ml/clustering/train_kmeans.py
python ml/clustering/evaluate.py
python ml/clustering/predict.py
```

No model artifact is included until valid real feature rows exist and the model
has been trained and reviewed. At present, the expected Landsat scene bundle is
not available in the inspected workspace, so training correctly stops before
writing artifacts or metrics.

## Ownership

- Owner: Machine learning engineering
- Inputs: Validated real feature rows with complete six-feature observations.
- Outputs: Reproducible scaler, candidate clustering metrics, and neutral cluster labels after successful training.
- Must not store: Demo rows as real training data, fabricated metrics, credentials, or unreviewed agronomic claims.
