# Implemented repository structure

```text
agrishift-ai/
├── apps/
│   ├── api/app/                 FastAPI routes, schemas, services and adapters
│   └── web/index.html           Existing multilingual farmer and expert UI
├── data/
│   ├── api-samples/             Saved provider samples; only explicit demo mode uses weather sample
│   ├── features/                Supplied demo example; generated real features are absent
│   ├── layers/                  Runtime slope PNG and metadata; other Landsat layers unavailable
│   ├── manifests/               Checksummed source inventories
│   ├── processed/               Ignored local terrain and regional summary products
│   └── raw/                     User source files; ignored by Git and omitted from release ZIP
├── docs/
│   ├── archive/                 Original ZIP source inventory and code documentation
│   ├── audit/                   Discovery, results, placeholder and release audit
│   ├── data/                    Source-specific validation and limitations
│   ├── demo/                    Demo script, judging points and known limitations
│   ├── api/                     API contract and endpoint docs
│   ├── database/                SQLite model and data dictionary
│   └── architecture/            Existing architecture records
├── ml/clustering/               Guarded real-row K-Means utilities; artifacts absent
├── scripts/
│   ├── data/                    Validators, manifests, context and terrain processing
│   ├── build_real_features.py   Landsat/SRTM/POWER/context feature builder
│   └── start_demo.py            Local explicit demo startup
├── services/rotation-engine/    Existing rule-based crop recommendations
├── requirements.txt             Version ranges
└── requirements.lock.txt        Tested Python 3.11 package versions
```

The scientific raw data and model outputs remain local and ignored. `data/manifests/` documents their file names, checksums, metadata, and validation limits without storing a developer's absolute Downloads path.
