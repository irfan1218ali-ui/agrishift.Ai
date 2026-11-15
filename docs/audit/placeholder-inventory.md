# Placeholder and sample inventory

| File or feature | Purpose and status | Real-mode reachability | Demo use and risk |
|---|---|---|---|
| `data/features/features.example.json` | Supplied example with an explicit warning that its environmental numbers are placeholders | No; real mode reads only `features.json` | Selected only by the explicit demo launcher or `DEMO_MODE=true`; persistent banner required |
| `data/features/features.json` | Required real feature product | Absent | Not substituted from the example; real analysis returns `insufficient_data` |
| `data/api-samples/meteomatics_sample.json` | Original ZIP compatibility sample | Not used by real mode | Legacy example response; not a live forecast |
| `data/api-samples/meteomatics/json.json` | Saved provider JSON response, generated 2026-11-15 | Not used by real mode | Sanitized copy is selected for demo; response includes `is_sample=true`, `is_live=false`, and calculated expiry |
| `data/api-samples/meteomatics/demo_sample.example.json` | Shareable sanitized copy of saved response; account `user` field omitted | Not used by real mode | Demo forecast source; still a saved sample, never live |
| `knowledge/crops.csv` | Existing crop rules; values are marked unverified unless source review is recorded | Used by the rotation engine, but unverified facts cannot independently hard-reject a crop | Recommendations are conditional and require expert review |
| `data/layers/.gitkeep` | Original placeholder for future raster layers | No data served from it | NDVI/NDMI/BSI unavailable until real Landsat processing |
| `LAYER_BOUNDS` | Earlier hardcoded frontend map bounds | Removed | Current expert overlay reads bounds from `data/layers/metadata.json` |
| Frontend `mockAnalyze` / `mockWeather` | Earlier inline fake responses | Removed | UI now calls API; demo data comes from explicit backend mode |
| K-Means `artifacts/` and `features.clustered.json` | Future model output locations | Absent | Trainer refuses missing/incomplete real feature rows and does not create metrics |
| `data/raw/landsat/.../README.md` and manifest | Instructions/placeholders for expected source organization | No imagery to read | Lists expected files; no values are derived from it |

Code comments or documentation mentioning `TODO`, `sample`, `example`, and `unverified` are treated according to the table above. These labels do not promote samples to real data.
