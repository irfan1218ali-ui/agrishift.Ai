# ML and decision-support architecture

No model is trained here; no labels or performance values are claimed. Every model version links training manifest, feature schema, code/config, artifact checksum, metrics, evaluation split, calibration, limitations and approval state. Predictions are evidence inputs, never autonomous agronomic advice.

## Landsat segmentation

Candidate PyTorch U-Net with EfficientNet-B0 encoder. Inputs: Landsat blue/green/red/NIR/SWIR-1 plus NDVI/NDWI, aligned QA masks and metadata. Candidate classes: healthy vegetation, mild/severe stress, bare soil, water/waterlogging, possible salinity-related stress, cloud/NoData. Labels do not yet exist. Evaluate mean IoU, Dice, per-class precision/recall and confusion matrix with spatial/seasonal holdouts; report uncertainty and unsupported conditions.

## Crop suitability

Candidate XGBoost features include Landsat indicators/surface temperature, SMAP moisture context, GPM rainfall, POWER climate, terrain, farmer soil information, irrigation reliability, crop history and constraints. Candidate outputs are suitability/stress class and probability, confidence and SHAP explanation only after labels, calibration and expert review exist.

## Seasonal risk

Begin with transparent statistical or conventional ML baselines. GRU is conditional: build only with sufficient multi-year labeled sequences, missingness policy, temporal holdout and evidence that sequence modeling adds value. Do not create a fake GRU model or predictions.

## Rotation ranking and explainability

Apply evidence-backed agronomic hard constraints first, then soft risk penalties and farmer priority weights. Use a deterministic baseline until reviewed ranking labels/evaluation exist; consider XGBoost Ranker later. Explanation states source, date/resolution, benefit hypothesis, risk, limitation, confidence meaning and local review need. SHAP is attribution, not causality.
