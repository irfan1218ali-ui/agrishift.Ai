# AgriShift AI ZIP — Detailed Project and Complete Code Reference

> Source archive: `Downloads/agrishift.zip`
> Archive root: agrishift/
> Review date: 2026-11-15 (Asia/Karachi)
> This document describes the ZIP as supplied. It does not merge, execute, validate, or activate its code.

## What this document contains

This guide records the archive layout, runtime design, API surface, data and placeholder status, module responsibilities, test names, risks, and the complete text of every file in the ZIP. All code listings are copied from the archive contents; line endings are normalized for Markdown display.

## Handling and provenance

- The ZIP was read in place; it was not extracted or modified.
- README commands and comments inside the archive are documented as project content, not followed as instructions for this review.
- No Python module, HTML, test, API client, or script from the archive was executed.
- No provider API was called and no dataset was processed.
- This is an archive-only code snapshot. It is not the active six-source architecture in the surrounding repository and is not automatically approved for integration.

## Archive inventory

| Measure | Value |
|---|---|
| Files | 25 |
| Uncompressed bytes | 118484 |
| Archive SHA-256 | 1f0383ed884a6934f086e30d5a7f0d0d0435b3e811431be6ab9b5e237958884b |

### File tree

~~~text
agrishift/.env.example
agrishift/.gitignore
agrishift/README.md
agrishift/apps/api/app/__init__.py
agrishift/apps/api/app/config.py
agrishift/apps/api/app/features.py
agrishift/apps/api/app/main.py
agrishift/apps/api/app/power.py
agrishift/apps/api/app/schemas.py
agrishift/apps/api/app/service.py
agrishift/apps/api/app/weather.py
agrishift/apps/api/requirements.txt
agrishift/apps/api/tests/conftest.py
agrishift/apps/api/tests/test_clients.py
agrishift/apps/api/tests/test_service.py
agrishift/apps/web/index.html
agrishift/data/api-samples/meteomatics_sample.json
agrishift/data/cache/.gitignore
agrishift/data/features/features.example.json
agrishift/data/layers/.gitkeep
agrishift/knowledge/crops.csv
agrishift/services/rotation-engine/rotation_engine/__init__.py
agrishift/services/rotation-engine/rotation_engine/crops.py
agrishift/services/rotation-engine/rotation_engine/engine.py
agrishift/services/rotation-engine/tests/test_engine.py
~~~

### File index

| Archive path | Bytes | Lines | Purpose | SHA-256 |
|---|---:|---:|---|---|
| agrishift/.env.example | 195 | 6 | Environment-variable template. Values are blank placeholders; no secrets are present. | 346ac38b9cabcb024fdc534b2c49e9261ede103e98bccf4116373c40eee05e43 |
| agrishift/.gitignore | 60 | 7 | Ignore rules for Python caches, local environment, raw data and TIFF files. | b46b8b69cc7e0b02abddae063060439583c036a69f01c717da37dd56b88e01f1 |
| agrishift/README.md | 3227 | 53 | Project overview, run instructions, endpoints, safety claims, template IDs and tunable starting points. | f4fe5f5f2c8d3b7bb133b014e563d465fd14e4b321de0f938f0dc3a08bf7d2ef |
| agrishift/apps/api/app/__init__.py | 0 | 0 | Empty Python package marker. | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| agrishift/apps/api/app/config.py | 2355 | 62 | Environment-backed application settings. | 2cb083910b477bcc4687e3c2b6b20e6a3daea48fa88514b0004212c76607cc27 |
| agrishift/apps/api/app/features.py | 6993 | 190 | Feature normalization, spatial nearest-point lookup and local feature-store access. | 2841c732eaeb74f16811a34b7ea11d0ab3a42379bddbc0cde8f9a9af92d20127 |
| agrishift/apps/api/app/main.py | 2299 | 68 | FastAPI application assembly and route definitions. | dced5e3027db567e6bddeb8a2377a8b47530b031124f68e1c6a68328828cac02 |
| agrishift/apps/api/app/power.py | 4977 | 115 | NASA POWER request construction, daily response validation and monthly climate feature summary. | 174e792f1b54652391a18837717f80a1ef39c3cdfe620d9cec61405a976f16bb |
| agrishift/apps/api/app/schemas.py | 730 | 18 | Pydantic request contract for the analysis endpoint. | 365ea20e51db265cd425fc2dfe0fa0f8f7360db56156277c83d0be24de89d34f |
| agrishift/apps/api/app/service.py | 6451 | 150 | Analysis orchestration, data sufficiency, pilot-area checks and response construction. | aa1518ecf509b27e6b0130e7751de9ba86d176f7caf843ec54cb56ad405565b9 |
| agrishift/apps/api/app/weather.py | 4615 | 103 | Meteomatics URL/response handling, optional saved-sample behavior and weather summary. | ec5c6103a653383401005ef4cbdda39c524e17118dc28c25bc85323d29afe240 |
| agrishift/apps/api/requirements.txt | 53 | 4 | Python API and test dependency version floors. | 87b8ce8962a3de185600105392debe5d49a4639387cde4ceaab2245af033094c |
| agrishift/apps/api/tests/conftest.py | 154 | 5 | Shared pytest configuration/fixtures. | 1c2c7907fc8fb1b6c346172eb56ec9c9e81476b5040ddfb5e6bdbcfcdfa88abc |
| agrishift/apps/api/tests/test_clients.py | 6102 | 142 | NASA POWER, Meteomatics, normalization, cache and feature-store client tests. | 28ea3ebbcfd106fa6e9e5ff68e6acc493a0ddec6f8faf90618807ae4d61b587d |
| agrishift/apps/api/tests/test_service.py | 5905 | 127 | API service contract and behavior tests using injected dependencies. | c0f091ee34137c39162762a85ff8a5052685e6aa509ad5193e4bd3cb69e79828 |
| agrishift/apps/web/index.html | 42047 | 644 | Single-file web interface containing HTML, CSS and JavaScript; README describes MapLibre loaded from a CDN. | 3a326cb858d7c213974e96262930e3a8d1e27304b6a3f7e6bb0e1884eae0def8 |
| agrishift/data/api-samples/meteomatics_sample.json | 339 | 17 | Archived Meteomatics sample file. README explicitly labels it a placeholder; authenticity is not established. | 43888d1a957f120cf9eb72a608b37530d15610e8608751392fb973a8618e37df |
| agrishift/data/cache/.gitignore | 12 | 2 | Local cache ignore rule. | 462bbe804758a6b9458df1763b2810e9ae413e69fe11a593e8776b01d2eff068 |
| agrishift/data/features/features.example.json | 1698 | 73 | Example feature payload. README explicitly labels its numbers as placeholders. | 2bece8c82f51898cc5410d5787d740b72e343a760320f2f918ba54b14e0c654c |
| agrishift/data/layers/.gitkeep | 0 | 0 | Empty placeholder marking a future layer-output folder; no overlay images are included. | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| agrishift/knowledge/crops.csv | 1834 | 13 | Starter crop-knowledge table. README says values remain unverified until agronomist confirmation. | a748eb61773a2908611987455f8c5073a830e1fc1ea45cbc6b262b00b5447384 |
| agrishift/services/rotation-engine/rotation_engine/__init__.py | 151 | 4 | Package marker for the pure-Python crop-rotation engine. | 604f13eff7c237eb28ea6be2baf08d3fec6c2f893b10f2cb169f9d02998deeb0 |
| agrishift/services/rotation-engine/rotation_engine/crops.py | 3810 | 96 | Loads crop rows from CSV, parses crop attributes and exposes crop records to the engine. | 6f3d13798659910aa349fce38a70c6bc88365fd261e6a0b80f3f64db248b2c8e |
| agrishift/services/rotation-engine/rotation_engine/engine.py | 14562 | 365 | Rule-based season selection, agronomic constraint checks, scoring, confidence and explanation generation. | beba9eb573b05901baeabec098270f7346f7ba8c5073ca2439d21cebd98e858b |
| agrishift/services/rotation-engine/tests/test_engine.py | 9915 | 237 | Rotation-engine test cases for constraints, ranking, confidence, explanations, determinism and input validation. | e61da611ee449f2e7b15e0ff1a6256c36affe13f57b3e166828ecc9f0ceddabb |

## Architecture and execution flow

At a high level, the archive describes a FastAPI backend that serves the single-file web interface, exposes versioned analysis/data routes, reads a local feature JSON file, combines available feature summaries with Meteomatics/NASA POWER clients, and calls a separate pure-Python rule engine. The engine is rule-based; the README explicitly says no trained ML model is included.

1. The browser renders apps/web/index.html, with a built-in mock/demo mode described in the README. MapLibre is loaded from a CDN according to the README.
2. API requests are routed through apps/api/app/main.py; request validation is defined in schemas.py.
3. service.py checks field/pilot-area applicability and feature availability, obtains optional weather/climate context and calls the rotation engine.
4. features.py reads/normalizes the local feature store; the README expects a later data/features/features.json file, but that file is not in this ZIP. Only features.example.json is present and explicitly marked placeholder.
5. rotation_engine/engine.py ranks candidate sequences with deterministic rules, reports confidence dots and explanation/reason IDs, and marks unverified crop knowledge for expert review.
6. API tests and engine tests are present in the archive, but were not run for this documentation task.

## Runtime and environment

The archived requirements list FastAPI, Uvicorn, Pydantic and pytest with lower-bound versions. .env.example contains DEMO_MODE, optional FEATURES_PATH, Meteomatics username/password placeholders, and CORS_ORIGINS=*. No credential values are supplied. The wildcard CORS setting should be treated as development-only and reviewed before any deployment.

The README documents a command using uvicorn app.main:app --app-dir apps/api with DEMO_MODE=1, and a separate real-data mode requiring a feature JSON. These are recorded as instructions contained in the archive; they were not executed.

## API surface recorded in the archive README

- POST /api/v1/analyze — analysis/rotation response. README documents statuses ok, insufficient_data, and not_applicable, with reason IDs; invalid input is described as HTTP 422.
- GET /api/v1/crops — crop table payload.
- GET /api/v1/weather?lat=&lon= — weather summary.
- GET /api/v1/health — health check.
- GET /api/v1/layers/{ndvi|ndmi|bsi|slope}.png — raster overlay response.
- The README says the same server serves the web application. Actual route definitions are included in the full main.py listing below.

## Data and honesty notes

- features.example.json is explicitly described in the archive README as containing placeholder numbers. Do not treat those values as observed environmental data.
- meteomatics_sample.json is explicitly described as a placeholder. Its authenticity as a provider response is not established.
- knowledge/crops.csv is a starter table; the README states every crop row has verified=false until an agronomist confirms it. Treat values as unverified and unsuitable for operational recommendations.
- data/layers/.gitkeep is empty. The PNG layers named in the README are not present in this ZIP.
- The README says SMAP/GPM/Meteomatics are shown but not scored; missing features lead to insufficient_data; cloudy Landsat below the stated cloud-free threshold is treated as missing. These are claims in the archive documentation, not independently validated behavior.
- The README describes fallback to a labelled saved Meteomatics sample if credentials exist but the API is down. Because the included sample is marked placeholder, this fallback must not be represented as a real provider observation.
- The README calls engine weights, thresholds and penalties UNVERIFIED starting points. Do not represent them as validated agronomic rules.

## Source-code symbols (static index)

The following Python names were read from the syntax tree without importing or executing the modules:

### agrishift/apps/api/app/__init__.py

### agrishift/apps/api/app/config.py

- class Settings
- def get_settings()
### agrishift/apps/api/app/features.py

- def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float)
- def _num(x)
- def _month_dict(d) — {'1': v, ...} -> {1: v, ...}; returns None unless all 12 months are numeric.
- def normalize(raw: dict, min_cloud_free: float, power_fallback: Optional[Callable[[], Optional[dict]]]=None) — Validate one point's raw features. Returns a dict with:
- class FeatureStore — Loads features.json lazily (re-reads if the file changes).
### agrishift/apps/api/app/main.py

- def deps()
- def health()
- def analyze(req: AnalyzeRequest)
- def crops()
- def weather(lat: float=Query(ge=-90, le=90), lon: float=Query(ge=-180, le=180))
- def layer(name: str)
### agrishift/apps/api/app/power.py

- def build_url(lat: float, lon: float, start: str='20150101', end: str='20251231')
- def fetch_daily(lat: float, lon: float, timeout: float=45.0) — Returns the 'parameter' block ({"T2M_MAX": {"20150101": 31.2, ...}, ...}) or None on any failure.
- def _valid(v)
- def summarize(param: dict, heat_threshold: float=HEAT_THRESHOLD_C) — Daily POWER data -> the climate features used by the backend.
- def get_monthly_features(lat: float, lon: float, cache_dir: Path, samples_dir: Path, fetcher=fetch_daily) — cache -> live fetch (then cache) -> saved real sample -> None.
### agrishift/apps/api/app/schemas.py

- class AnalyzeRequest(BaseModel) — POST /api/v1/analyze body (plan section 8.1).
### agrishift/apps/api/app/service.py

- class Deps
- def build_deps(settings: Optional[Settings]=None)
- def _insufficient(reason_id: str)
- def _in_pilot_area(s: Settings, lat: float, lon: float)
- def _regional_context(f: dict)
- def analyze(req: AnalyzeRequest, deps: Deps, today: Optional[date]=None) — Raises ValueError for an unknown crop id (HTTP 422). Everything else returns a response dict.
- def crops_payload(deps: Deps)
### agrishift/apps/api/app/weather.py

- def build_url(lat: float, lon: float, start: datetime, days: int=3)
- def parse_meteomatics(payload: dict) — Meteomatics JSON -> [{"date": "YYYY-MM-DD", "tmax_c": float|None, "rain_mm": float|None}]
- def fetch_meteomatics(lat: float, lon: float, user: str, password: str, now: datetime, timeout: float=6.0)
- def _load_sample(samples_dir: Path, today: date)
- def get_weather(lat: float, lon: float, *, user: str, password: str, samples_dir: Path, demo_mode: bool, now: Optional[datetime]=None, fetcher: Callable[..., List[dict]]=fetch_meteomatics, use_cache: bool=True)
### agrishift/apps/api/tests/conftest.py

### agrishift/apps/api/tests/test_clients.py

- def daily_fixture(years=(2023, 2024))
- def test_power_url_matches_plan()
- def test_power_summarize()
- def test_power_summarize_needs_all_months()
- def test_power_cache_and_failure(tmp_path)
- def test_meteomatics_url_and_parse()
- def kw(tmp_path, **o)
- def test_weather_no_credentials_means_unavailable(tmp_path)
- def test_weather_live(tmp_path)
- def test_weather_failure_uses_labelled_sample(tmp_path)
- def test_weather_failure_without_sample_is_unavailable(tmp_path)
- def test_weather_demo_mode_uses_sample_without_credentials(tmp_path)
- def test_haversine()
- def test_normalize_rejects_bad_values()
- def test_feature_store_nearest(tmp_path)
### agrishift/apps/api/tests/test_service.py

- def point_features(**over)
- def make_deps(tmp_path, features=None, weather=None, power=None, points=True)
- def req(**kw)
- def test_ok_response_matches_contract(tmp_path)
- def test_all_six_sources_gives_three_dots(tmp_path)
- def test_no_forecast_loses_a_dot(tmp_path)
- def test_sugarcane_and_banana_not_applicable(tmp_path)
- def test_out_of_area_pin(tmp_path)
- def test_no_features_file_is_insufficient(tmp_path)
- def test_pin_far_from_any_point_is_insufficient(tmp_path)
- def test_missing_core_data_is_insufficient(tmp_path, missing)
- def test_cloudy_landsat_is_treated_as_missing(tmp_path)
- def test_incomplete_heat_months_are_not_guessed(tmp_path)
- def test_power_fallback_fills_climate(tmp_path)
- def test_smap_gpm_missing_still_ok_but_fewer_dots(tmp_path)
### agrishift/services/rotation-engine/rotation_engine/__init__.py

### agrishift/services/rotation-engine/rotation_engine/crops.py

- class Crop
- def _level(table: Dict[str, int], value: str, field: str, crop_id: str)
- def _bool(value: str, field: str, crop_id: str)
- def _month(value: str, field: str, crop_id: str)
- def load_crops(path: str) — Load crops in file order. Raises ValueError on any invalid row (fail loudly).
### agrishift/services/rotation-engine/rotation_engine/engine.py

- def upcoming_seasons(today: date) — Next two growing seasons as [(type, code), (type, code)].
- class Ctx
- def _sow_window(c: Crop, first: Optional[Crop]) — Sowing window on one continuous month axis. The second crop is shifted by 12 if it falls in the next calendar year.
- def _heat_risk(c: Crop, ctx: Ctx)
- def _heat_exposure(c: Crop, ctx: Ctx) — risk * (1 - tolerance scale): 0 = no problem, 1 = worst.
- def hard_violations(c1: Crop, c2: Crop, ctx: Ctx)
- def _paani_fit(c: Crop, ctx: Ctx)
- def _tol_fit(tol: int)
- def _zameen_fit(c: Crop, ctx: Ctx)
- def _mausam_fit(c: Crop, ctx: Ctx)
- def _rotation_faida(c: Crop, prev: Crop)
- def _mean(xs)
- def score_sequence(c1: Crop, c2: Crop, ctx: Ctx, wkey: str) — Returns (score 0..100, late_sowing_flag).
- def confidence_dots(ctx: Ctx)
- def _explain(c1: Crop, c2: Crop, ctx: Ctx, violations: List[str], late: bool, is_existing: bool)
- def _option(opt_id: str, c1: Crop, c2: Crop, ctx: Ctx, wkey: str, dots: int, is_existing: bool)
- def _field_health(ndvi: float)
- def recommend(crops: Dict[str, Crop], request: dict, features: dict, today: Optional[date]=None) — Build the 3 options.
### agrishift/services/rotation-engine/tests/test_engine.py

- def feats(**kw)
- def req(**kw)
- def seq(o)
- def test_crops_table_loads()
- def test_upcoming_seasons()
- def test_three_distinct_options_in_order()
- def test_existing_option_is_farmers_way()
- def test_recommended_options_never_violate_hard_rules()
- def test_wheat_after_wheat_is_rejected_red_warning()
- def test_low_water_rejects_thirsty_crops()
- def test_rain_fed_is_more_restrictive_than_canal()
- def test_salinity_yes_rejects_low_tolerance()
- def test_waterlogging_or_low_lying_rejects_low_tolerance()
- def test_waterlogging_can_leave_no_safe_option()
- def test_overlap_rule()
- def test_season_mismatch_rule()
- def test_priority_changes_ranking()
- def test_save_water_priority_prefers_light_crops()
- def test_legume_gets_bonus_and_reason()
- def test_rice_then_wheat_is_not_rejected()
- def test_weak_field_flags_expert_and_boosts_legume()
- def test_confidence_dots_rules()
- def test_unverified_crops_always_need_expert()
- def test_heat_exposure_lowers_heat_sensitive_crops()
- def test_why_and_caution_limits_and_shape()
- def test_deterministic()
- def test_kharif_first_window()
- def test_bad_inputs_raise()

## Tests included in the archive (not executed)

### Rotation engine

- def test_crops_table_loads()
- def test_upcoming_seasons()
- def test_three_distinct_options_in_order()
- def test_existing_option_is_farmers_way()
- def test_recommended_options_never_violate_hard_rules()
- def test_wheat_after_wheat_is_rejected_red_warning()
- def test_low_water_rejects_thirsty_crops()
- def test_rain_fed_is_more_restrictive_than_canal()
- def test_salinity_yes_rejects_low_tolerance()
- def test_waterlogging_or_low_lying_rejects_low_tolerance()
- def test_waterlogging_can_leave_no_safe_option()
- def test_overlap_rule()
- def test_season_mismatch_rule()
- def test_priority_changes_ranking()
- def test_save_water_priority_prefers_light_crops()
- def test_legume_gets_bonus_and_reason()
- def test_rice_then_wheat_is_not_rejected()
- def test_weak_field_flags_expert_and_boosts_legume()
- def test_confidence_dots_rules()
- def test_unverified_crops_always_need_expert()
- def test_heat_exposure_lowers_heat_sensitive_crops()
- def test_why_and_caution_limits_and_shape()
- def test_deterministic()
- def test_kharif_first_window()
- def test_bad_inputs_raise()

### API service and clients

#### agrishift/apps/api/tests/test_clients.py
- def test_power_url_matches_plan()
- def test_power_summarize()
- def test_power_summarize_needs_all_months()
- def test_power_cache_and_failure(tmp_path)
- def test_meteomatics_url_and_parse()
- def test_weather_no_credentials_means_unavailable(tmp_path)
- def test_weather_live(tmp_path)
- def test_weather_failure_uses_labelled_sample(tmp_path)
- def test_weather_failure_without_sample_is_unavailable(tmp_path)
- def test_weather_demo_mode_uses_sample_without_credentials(tmp_path)
- def test_haversine()
- def test_normalize_rejects_bad_values()
- def test_feature_store_nearest(tmp_path)
#### agrishift/apps/api/tests/test_service.py
- def test_ok_response_matches_contract(tmp_path)
- def test_all_six_sources_gives_three_dots(tmp_path)
- def test_no_forecast_loses_a_dot(tmp_path)
- def test_sugarcane_and_banana_not_applicable(tmp_path)
- def test_out_of_area_pin(tmp_path)
- def test_no_features_file_is_insufficient(tmp_path)
- def test_pin_far_from_any_point_is_insufficient(tmp_path)
- def test_missing_core_data_is_insufficient(tmp_path, missing)
- def test_cloudy_landsat_is_treated_as_missing(tmp_path)
- def test_incomplete_heat_months_are_not_guessed(tmp_path)
- def test_power_fallback_fills_climate(tmp_path)
- def test_smap_gpm_missing_still_ok_but_fewer_dots(tmp_path)

These test names describe intended coverage only. No test result is claimed.

## Complete archived file contents

Each section below contains the full text of one archive member. The digest in the inventory is SHA-256 of the original uncompressed member bytes.

### agrishift/.env.example

**Bytes:** 195 · **Lines:** 6 · **SHA-256:** 346ac38b9cabcb024fdc534b2c49e9261ede103e98bccf4116373c40eee05e43

~~~text
# Copy to .env (never commit). Exported to the process env before starting uvicorn.
DEMO_MODE=0
# FEATURES_PATH=data/features/features.json
METEOMATICS_USER=
METEOMATICS_PASSWORD=
CORS_ORIGINS=*
~~~

### agrishift/.gitignore

**Bytes:** 60 · **Lines:** 7 · **SHA-256:** b46b8b69cc7e0b02abddae063060439583c036a69f01c717da37dd56b88e01f1

~~~text
__pycache__/
*.pyc
.env
data/cache/*
data/raw/
*.tif
*.tiff
~~~

### agrishift/README.md

**Bytes:** 3227 · **Lines:** 53 · **SHA-256:** f4fe5f5f2c8d3b7bb133b014e563d465fd14e4b321de0f938f0dc3a08bf7d2ef

~~~markdown
# AgriShift AI — MVP (frontend + backend)

Rule-based crop-rotation options for the Hyderabad (Sindh) pilot. **No trained ML model.**

```
apps/web/                     farmer app + expert view (single index.html, MapLibre via CDN)
apps/api/app/                 FastAPI (main.py), service.py, features.py, power.py, weather.py
services/rotation-engine/     pure-Python rules engine (rotation_engine/) + tests
knowledge/crops.csv           starter crop table (verified=false until an agronomist confirms)
data/features/                features.json from Member 4  (features.example.json = PLACEHOLDER numbers)
data/api-samples/             saved API samples (meteomatics_sample.json = PLACEHOLDER)
data/layers/                  overlay PNGs: ndvi.png ndmi.png bsi.png slope.png (Member 4)
```

## Run
```bash
pip install -r apps/api/requirements.txt
cp .env.example .env            # then export the variables (or set them in your shell)
DEMO_MODE=1 uvicorn app.main:app --app-dir apps/api --port 8000      # demo: uses EXAMPLE features
# real run: put Member 4's file at data/features/features.json and start WITHOUT DEMO_MODE
```
Open http://localhost:8000 — the web app is served by the same server and talks to `/api/v1/*`.
Open `apps/web/index.html` directly as a file (or add `?mock=1`) to use the built-in demo data without a backend.

## Tests
```bash
python -m pytest -q apps/api/tests services/rotation-engine/tests
```

## Endpoints
`POST /api/v1/analyze`, `GET /api/v1/crops`, `GET /api/v1/weather?lat=&lon=`, `GET /api/v1/health`, `GET /api/v1/layers/{ndvi|ndmi|bsi|slope}.png`

`analyze` statuses: `ok`, `insufficient_data` (+`reason_id`: `no_data_001`, `out_of_area`, `no_safe_option_001`),
`not_applicable` (+`reason_id`: `special_long` sugarcane, `special_perm` banana/orchard). Invalid input -> HTTP 422.

## Honesty rules built in
- Missing features -> `insufficient_data` (never guessed). Landsat with <50 % cloud-free pixels counts as missing.
- SMAP/GPM/Meteomatics are shown but **not scored**.
- Meteomatics: no credentials -> "not available"; credentials but API down -> labelled saved sample.
- NASA POWER fills climate features only from a real cache/live fetch/saved real response; never invented.
- All crop values are `verified=false` -> every card says "expert verification pending".

## Template IDs the engine can emit (Member 3: translations + audio `audio/<lang>/<id>.mp3`)
why_water_ok_001, why_known_crop_002, why_legume_001, why_water_save_001, why_soil_help_001, why_heat_ok_001,
caution_late_sowing_001, caution_waterlog_001, caution_heat_001, caution_rule_water_001, caution_rule_salt_001,
caution_rule_waterlog_001, caution_rule_repeat_001, caution_rule_overlap_001,
health_good_001, health_moderate_001, health_poor_001, no_data_001, no_safe_option_001, out_of_area,
special_long, special_perm, disclaimer_001, regional_note_001, regional_note_002.
Screen prompts: welcome, q_where, q_crop, q_water, q_amount, q_salinity, q_waterlog, q_priority, result_intro.

## Tunable numbers (all UNVERIFIED starting points)
`rotation_engine/engine.py`: WEIGHTS, AVAIL_LEVEL, NDVI_WEAK/GOOD, HEAT_DAYS_FULL_RISK, penalties, GREEN_MIN_SCORE.
`apps/api/app/power.py`: HEAT_THRESHOLD_C (40 °C).
~~~

### agrishift/apps/api/app/__init__.py

**Bytes:** 0 · **Lines:** 0 · **SHA-256:** e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

(Empty file.)

### agrishift/apps/api/app/config.py

**Bytes:** 2355 · **Lines:** 62 · **SHA-256:** 2cb083910b477bcc4687e3c2b6b20e6a3daea48fa88514b0004212c76607cc27

~~~python
"""Settings (environment driven). Also puts the rotation engine on sys.path."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]            # .../agrishift
ENGINE_DIR = ROOT / "services" / "rotation-engine"
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))


@dataclass(frozen=True)
class Settings:
    root: Path
    demo_mode: bool                 # DEMO_MODE=1 -> allow the EXAMPLE features file + saved weather sample
    features_path: Path
    crops_csv: Path
    samples_dir: Path
    cache_dir: Path
    layers_dir: Path
    web_dir: Path
    meteomatics_user: str
    meteomatics_password: str
    cors_origins: list
    # pilot area (Hyderabad, Sindh) - same box as the frontend
    min_lat: float = 25.1
    max_lat: float = 25.7
    min_lon: float = 68.1
    max_lon: float = 68.7
    features_max_km: float = 5.0    # nearest features point must be within this distance
    min_cloud_free: float = 0.5     # Landsat treated as unusable below this cloud-free fraction (unverified)
    default_satellite_window: str = "2025-09-01/2025-09-30"
    default_landsat_date: str = "2025-09-22"


def get_settings() -> Settings:
    env = os.environ.get
    root = Path(env("AGRISHIFT_ROOT", str(ROOT)))
    demo = env("DEMO_MODE", "0") == "1"
    if env("FEATURES_PATH"):
        features = Path(env("FEATURES_PATH"))
    else:
        real = root / "data" / "features" / "features.json"
        example = root / "data" / "features" / "features.example.json"
        features = example if (demo and not real.exists()) else real
    origins = [o.strip() for o in env("CORS_ORIGINS", "*").split(",") if o.strip()]
    return Settings(
        root=root,
        demo_mode=demo,
        features_path=features,
        crops_csv=Path(env("CROPS_CSV", str(root / "knowledge" / "crops.csv"))),
        samples_dir=root / "data" / "api-samples",
        cache_dir=Path(env("CACHE_DIR", str(root / "data" / "cache"))),
        layers_dir=Path(env("LAYERS_DIR", str(root / "data" / "layers"))),
        web_dir=Path(env("WEB_DIR", str(root / "apps" / "web"))),
        meteomatics_user=env("METEOMATICS_USER", ""),
        meteomatics_password=env("METEOMATICS_PASSWORD", ""),
        cors_origins=origins or ["*"],
    )
~~~

### agrishift/apps/api/app/features.py

**Bytes:** 6993 · **Lines:** 190 · **SHA-256:** 2841c732eaeb74f16811a34b7ea11d0ab3a42379bddbc0cde8f9a9af92d20127

~~~python
"""Feature reader: nearest pre-processed point from features.json (made by Member 4).

features.json format
--------------------
{
  "meta": {"satellite_window": "2025-09-01/2025-09-30", "landsat_date": "2025-09-22"},
  "points": [
    {"id": "hyd_001", "lat": 25.39, "lon": 68.37,
     "features": {
        "ndvi_mean": 0.41, "ndmi_mean": 0.12, "bsi_mean": 0.03, "surface_temp_c": 36.2, "cloud_free_fraction": 0.93,
        "elevation_m": 28.0, "slope_deg": 0.3, "low_lying_flag": false,
        "tmax_mean_by_month": {"1": 24.1, ... "12": 25.0},
        "heat_days_40c_by_month": {"1": 0, ... "12": 0},
        "rain_mm_by_month": {"1": 6, ...}, "rh_mean": 52.0, "wind_mean": 3.1,
        "smap_surface_mean": 0.21, "smap_rootzone_mean": 0.30,
        "gpm_total_mm": 18.2, "gpm_rainy_days": 3, "gpm_max_daily_mm": 9.0
     }}
  ]
}
Missing values: leave the key out or use null. NEVER fill with guesses.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _num(x) -> Optional[float]:
    if isinstance(x, bool) or x is None:
        return None
    if isinstance(x, (int, float)) and math.isfinite(x):
        return float(x)
    return None


def _month_dict(d) -> Optional[Dict[int, float]]:
    """{'1': v, ...} -> {1: v, ...}; returns None unless all 12 months are numeric."""
    if not isinstance(d, dict):
        return None
    out: Dict[int, float] = {}
    for k, v in d.items():
        try:
            m = int(k)
        except (TypeError, ValueError):
            return None
        n = _num(v)
        if n is None or not 1 <= m <= 12:
            return None
        out[m] = n
    return out if set(out) == set(range(1, 13)) else None


def normalize(raw: dict, min_cloud_free: float,
              power_fallback: Optional[Callable[[], Optional[dict]]] = None) -> dict:
    """Validate one point's raw features. Returns a dict with:
        values (only valid ones), sources (list of present source names), sources_present (int)
    A source counts as present only when its values are valid.
    """
    raw = raw or {}
    f: dict = {}
    sources = []

    # --- Landsat (unusable when too cloudy)
    ndvi = _num(raw.get("ndvi_mean"))
    cloud_free = _num(raw.get("cloud_free_fraction"))
    if ndvi is not None and (cloud_free is None or cloud_free >= min_cloud_free):
        f["ndvi_mean"] = ndvi
        for k in ("ndmi_mean", "bsi_mean", "surface_temp_c", "cloud_free_fraction"):
            if _num(raw.get(k)) is not None:
                f[k] = _num(raw[k])
        sources.append("landsat")

    # --- SRTM
    if isinstance(raw.get("low_lying_flag"), bool):
        f["low_lying_flag"] = raw["low_lying_flag"]
        for k in ("elevation_m", "slope_deg"):
            if _num(raw.get(k)) is not None:
                f[k] = _num(raw[k])
        sources.append("srtm")

    # --- NASA POWER (needs all 12 months of heat days)
    heat = _month_dict(raw.get("heat_days_40c_by_month"))
    power = raw
    if heat is None and power_fallback is not None:
        fb = power_fallback()
        if fb:
            power = fb
            heat = _month_dict(fb.get("heat_days_40c_by_month"))
    if heat is not None:
        f["heat_days_40c_by_month"] = heat
        for k in ("tmax_mean_by_month", "rain_mm_by_month"):
            md = _month_dict(power.get(k))
            if md is not None:
                f[k] = md
        for k in ("rh_mean", "wind_mean"):
            if _num(power.get(k)) is not None:
                f[k] = _num(power[k])
        sources.append("power")

    # --- SMAP / GPM (regional context only, not scored)
    if _num(raw.get("smap_surface_mean")) is not None:
        f["smap_surface_mean"] = _num(raw["smap_surface_mean"])
        if _num(raw.get("smap_rootzone_mean")) is not None:
            f["smap_rootzone_mean"] = _num(raw["smap_rootzone_mean"])
        sources.append("smap")
    if _num(raw.get("gpm_total_mm")) is not None:
        f["gpm_total_mm"] = _num(raw["gpm_total_mm"])
        for k in ("gpm_rainy_days", "gpm_max_daily_mm"):
            if _num(raw.get(k)) is not None:
                f[k] = _num(raw[k])
        sources.append("gpm")

    f["sources"] = sources
    f["sources_present"] = len(sources)
    return f


class FeatureStore:
    """Loads features.json lazily (re-reads if the file changes)."""

    def __init__(self, path: Path, max_km: float = 5.0, min_cloud_free: float = 0.5):
        self.path = Path(path)
        self.max_km = max_km
        self.min_cloud_free = min_cloud_free
        self._mtime: Optional[float] = None
        self._data: Optional[dict] = None

    def _load(self) -> Optional[dict]:
        try:
            mtime = self.path.stat().st_mtime
        except OSError:
            self._data, self._mtime = None, None
            return None
        if self._data is None or mtime != self._mtime:
            with open(self.path, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict) or not isinstance(data.get("points"), list):
                raise ValueError(f"{self.path}: expected an object with a 'points' list")
            self._data, self._mtime = data, mtime
        return self._data

    def available(self) -> bool:
        try:
            d = self._load()
        except Exception:
            return False
        return bool(d and d["points"])

    def meta(self) -> dict:
        d = self._load()
        return (d or {}).get("meta", {}) or {}

    def nearest(self, lat: float, lon: float) -> Optional[Tuple[dict, float]]:
        """(raw point dict, distance_km) of the closest point within max_km, else None."""
        d = self._load()
        if not d:
            return None
        best, best_km = None, None
        for p in d["points"]:
            plat, plon = _num(p.get("lat")), _num(p.get("lon"))
            if plat is None or plon is None:
                continue
            km = haversine_km(lat, lon, plat, plon)
            if best_km is None or km < best_km:
                best, best_km = p, km
        if best is None or best_km > self.max_km:
            return None
        return best, best_km

    def get(self, lat: float, lon: float,
            power_fallback: Optional[Callable[[], Optional[dict]]] = None) -> Optional[dict]:
        hit = self.nearest(lat, lon)
        if hit is None:
            return None
        point, km = hit
        feats = normalize(point.get("features") or {}, self.min_cloud_free, power_fallback)
        feats["_point_id"] = point.get("id")
        feats["_distance_km"] = round(km, 3)
        return feats
~~~

### agrishift/apps/api/app/main.py

**Bytes:** 2299 · **Lines:** 68 · **SHA-256:** dced5e3027db567e6bddeb8a2377a8b47530b031124f68e1c6a68328828cac02

~~~python
"""AgriShift AI - FastAPI app.   Run:  uvicorn app.main:app --app-dir apps/api --port 8000"""
from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .schemas import AnalyzeRequest
from . import service

LAYER_NAMES = {"ndvi", "ndmi", "bsi", "slope"}

app = FastAPI(title="AgriShift AI API", version="1.0.0",
              description="Rule-based crop rotation options for the Hyderabad (Sindh) pilot. No trained ML model.")

_settings = get_settings()
app.add_middleware(CORSMiddleware, allow_origins=_settings.cors_origins, allow_methods=["GET", "POST"],
                   allow_headers=["*"])


@lru_cache(maxsize=1)
def deps() -> service.Deps:
    return service.build_deps()


@app.get("/api/v1/health")
def health():
    d = deps()
    return {"status": "ok", "crops": len(d.crops), "features_available": d.store.available(),
            "demo_mode": d.settings.demo_mode,
            "meteomatics_configured": bool(d.settings.meteomatics_user and d.settings.meteomatics_password)}


@app.post("/api/v1/analyze")
def analyze(req: AnalyzeRequest):
    try:
        return service.analyze(req, deps())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/v1/crops")
def crops():
    return service.crops_payload(deps())


@app.get("/api/v1/weather")
def weather(lat: float = Query(ge=-90, le=90), lon: float = Query(ge=-180, le=180)):
    return deps().weather_fn(lat, lon)


@app.get("/api/v1/layers/{name}.png")
def layer(name: str):
    if name not in LAYER_NAMES:                       # whitelist = no path tricks
        raise HTTPException(status_code=404, detail="unknown layer")
    f = deps().settings.layers_dir / f"{name}.png"
    if not f.is_file():
        raise HTTPException(status_code=404, detail="layer not available")
    return FileResponse(str(f), media_type="image/png")


# Serve the farmer web app (and audio/) from the same server, last so API routes win.
if _settings.web_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(_settings.web_dir), html=True), name="web")
~~~

### agrishift/apps/api/app/power.py

**Bytes:** 4977 · **Lines:** 115 · **SHA-256:** 174e792f1b54652391a18837717f80a1ef39c3cdfe620d9cec61405a976f16bb

~~~python
"""NASA POWER client (daily point API) with disk cache.

Used only to fill in climate features when features.json lacks them.
There is NO invented fallback: a saved real response may be placed in
data/api-samples/power_sample.json (same shape as the API's "parameter" block);
if neither the network, the cache nor that file works, POWER counts as missing.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional

POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMS = "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN"
FILL = -999.0
HEAT_THRESHOLD_C = 40.0      # configurable, unverified (plan section 5.3)


def build_url(lat: float, lon: float, start: str = "20150101", end: str = "20251231") -> str:
    q = {"parameters": PARAMS, "community": "AG", "longitude": f"{lon}", "latitude": f"{lat}",
         "start": start, "end": end, "format": "JSON"}
    return POWER_URL + "?" + urllib.parse.urlencode(q, safe=",")


def fetch_daily(lat: float, lon: float, timeout: float = 45.0) -> Optional[dict]:
    """Returns the 'parameter' block ({"T2M_MAX": {"20150101": 31.2, ...}, ...}) or None on any failure."""
    try:
        req = urllib.request.Request(build_url(lat, lon), headers={"User-Agent": "AgriShiftAI/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            payload = json.loads(r.read().decode("utf-8"))
        param = payload["properties"]["parameter"]
        return param if isinstance(param, dict) and param else None
    except Exception:
        return None


def _valid(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v != FILL and v == v


def summarize(param: dict, heat_threshold: float = HEAT_THRESHOLD_C) -> Optional[dict]:
    """Daily POWER data -> the climate features used by the backend.

    heat_days_40c_by_month[m]  = average over years of (days with T2M_MAX >= threshold) in month m
    tmax_mean_by_month[m]      = mean T2M_MAX in month m
    rain_mm_by_month[m]        = average over years of the monthly PRECTOTCORR total
    rh_mean, wind_mean         = overall means of RH2M and WS2M
    Missing-value days (-999) are skipped. Returns None unless T2M_MAX covers all 12 months.
    """
    tmax = param.get("T2M_MAX") or {}
    heat_by_ym: Dict[tuple, int] = defaultdict(int)
    tmax_vals: Dict[int, list] = defaultdict(list)
    for date_s, v in tmax.items():
        if not _valid(v) or len(date_s) != 8:
            continue
        y, m = int(date_s[:4]), int(date_s[4:6])
        tmax_vals[m].append(float(v))
        heat_by_ym[(y, m)] += 1 if v >= heat_threshold else 0
    if set(tmax_vals) != set(range(1, 13)):
        return None
    heat_years: Dict[int, list] = defaultdict(list)
    for (y, m), n in heat_by_ym.items():
        heat_years[m].append(n)
    heat = {m: sum(heat_years[m]) / len(heat_years[m]) for m in range(1, 13)}
    tmax_mean = {m: sum(tmax_vals[m]) / len(tmax_vals[m]) for m in range(1, 13)}

    rain_ym: Dict[tuple, float] = defaultdict(float)
    for date_s, v in (param.get("PRECTOTCORR") or {}).items():
        if _valid(v) and len(date_s) == 8:
            rain_ym[(int(date_s[:4]), int(date_s[4:6]))] += float(v)
    rain_years: Dict[int, list] = defaultdict(list)
    for (y, m), total in rain_ym.items():
        rain_years[m].append(total)
    out = {"heat_days_40c_by_month": heat, "tmax_mean_by_month": tmax_mean}
    if set(rain_years) == set(range(1, 13)):
        out["rain_mm_by_month"] = {m: sum(rain_years[m]) / len(rain_years[m]) for m in range(1, 13)}

    for key, name in (("RH2M", "rh_mean"), ("WS2M", "wind_mean")):
        vals = [float(v) for v in (param.get(key) or {}).values() if _valid(v)]
        if vals:
            out[name] = sum(vals) / len(vals)
    return out


def get_monthly_features(lat: float, lon: float, cache_dir: Path, samples_dir: Path,
                         fetcher=fetch_daily) -> Optional[dict]:
    """cache -> live fetch (then cache) -> saved real sample -> None."""
    cache_dir = Path(cache_dir)
    cache_file = cache_dir / f"power_{lat:.2f}_{lon:.2f}.json"
    param = None
    if cache_file.exists():
        try:
            param = json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            param = None
    if param is None:
        param = fetcher(lat, lon)
        if param:
            try:
                cache_dir.mkdir(parents=True, exist_ok=True)
                cache_file.write_text(json.dumps(param), encoding="utf-8")
            except OSError:
                pass
    if param is None:
        sample = Path(samples_dir) / "power_sample.json"
        if sample.exists():
            try:
                param = json.loads(sample.read_text(encoding="utf-8"))
            except Exception:
                param = None
    return summarize(param) if param else None
~~~

### agrishift/apps/api/app/schemas.py

**Bytes:** 730 · **Lines:** 18 · **SHA-256:** 365ea20e51db265cd425fc2dfe0fa0f8f7360db56156277c83d0be24de89d34f

~~~python
from typing import Literal, Optional

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """POST /api/v1/analyze body (plan section 8.1)."""
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    radius_m: int = Field(default=150, ge=10, le=5000)
    current_crop: str = Field(min_length=1, max_length=40)
    previous_crop: Optional[str] = "unknown"
    water_source: Literal["canal", "tubewell", "rain"]
    water_amount: Literal["low", "medium", "high"]
    salinity: Literal["yes", "no", "unknown"]
    waterlogging: Literal["yes", "no", "unknown"]
    priority: Literal["save_water", "improve_soil", "balanced"] = "balanced"
    language: Literal["sd", "ur", "en"] = "en"
~~~

### agrishift/apps/api/app/service.py

**Bytes:** 6451 · **Lines:** 150 · **SHA-256:** aa1518ecf509b27e6b0130e7751de9ba86d176f7caf843ec54cb56ad405565b9

~~~python
"""Glue between HTTP, data readers and the rotation engine. No web framework imports here (easy to test)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Dict, Optional

from .config import Settings, get_settings
from .features import FeatureStore
from . import power as power_mod
from . import weather as weather_mod
from .schemas import AnalyzeRequest

from rotation_engine import load_crops, recommend  # noqa: E402  (path set in config.py)

SPECIAL = {"sugarcane": "special_long", "banana": "special_perm"}   # recognised, never recommended
CORE_SOURCES = ("landsat", "srtm", "power")                         # scoring needs these three
DISCLAIMER_ID = "disclaimer_001"


@dataclass
class Deps:
    settings: Settings
    crops: dict
    store: FeatureStore
    weather_fn: Callable[[float, float], dict]
    power_fn: Callable[[float, float], Optional[dict]]


def build_deps(settings: Optional[Settings] = None) -> Deps:
    s = settings or get_settings()
    crops = load_crops(str(s.crops_csv))          # fails loudly at start-up if the table is broken
    store = FeatureStore(s.features_path, max_km=s.features_max_km, min_cloud_free=s.min_cloud_free)

    def weather_fn(lat: float, lon: float) -> dict:
        return weather_mod.get_weather(lat, lon, user=s.meteomatics_user, password=s.meteomatics_password,
                                       samples_dir=s.samples_dir, demo_mode=s.demo_mode)

    def power_fn(lat: float, lon: float) -> Optional[dict]:
        return power_mod.get_monthly_features(lat, lon, s.cache_dir, s.samples_dir)

    return Deps(settings=s, crops=crops, store=store, weather_fn=weather_fn, power_fn=power_fn)


def _insufficient(reason_id: str) -> dict:
    return {"status": "insufficient_data", "reason_id": reason_id}


def _in_pilot_area(s: Settings, lat: float, lon: float) -> bool:
    return s.min_lat <= lat <= s.max_lat and s.min_lon <= lon <= s.max_lon


def _regional_context(f: dict) -> dict:
    ctx: Dict[str, dict] = {}
    if "smap_surface_mean" in f:
        ctx["soil_moisture"] = {"value": round(f["smap_surface_mean"], 3), "unit": "m3/m3",
                                "resolution_km": 9, "note_id": "regional_note_001"}
    if "gpm_total_mm" in f:
        ctx["rainfall"] = {"total_mm": round(f["gpm_total_mm"], 1), "resolution_km": 10,
                           "note_id": "regional_note_002"}
    return ctx


def analyze(req: AnalyzeRequest, deps: Deps, today: Optional[date] = None) -> dict:
    """Raises ValueError for an unknown crop id (HTTP 422). Everything else returns a response dict."""
    s = deps.settings
    known = set(deps.crops) | set(SPECIAL)
    if req.current_crop not in known:
        raise ValueError(f"unknown current_crop '{req.current_crop}'")
    if req.previous_crop not in (None, "", "unknown") and req.previous_crop not in known:
        raise ValueError(f"unknown previous_crop '{req.previous_crop}'")

    # 1) permanent / long crops: recognised, not a rotation case
    if req.current_crop in SPECIAL:
        return {"status": "not_applicable", "reason_id": SPECIAL[req.current_crop]}

    # 2) pilot area only
    if not _in_pilot_area(s, req.lat, req.lon):
        return _insufficient("out_of_area")

    # 3) pre-processed features (nearest point) - never guessed
    try:
        feats = deps.store.get(req.lat, req.lon, power_fallback=lambda: deps.power_fn(req.lat, req.lon))
    except Exception:
        feats = None
    if feats is None or not all(src in feats["sources"] for src in CORE_SOURCES):
        return _insufficient("no_data_001")

    # 4) forecast is context only (counts as the 6th data source for confidence)
    try:
        forecast = deps.weather_fn(req.lat, req.lon)
    except Exception:
        forecast = {"available": False, "source": "meteomatics", "is_sample": False}
    forecast_ok = bool(forecast.get("available"))
    sources_present = feats["sources_present"] + (1 if forecast_ok else 0)

    engine_features = {
        "ndvi_mean": feats["ndvi_mean"],
        "low_lying_flag": feats["low_lying_flag"],
        "heat_days_40c_by_month": feats["heat_days_40c_by_month"],
        "sources_present": sources_present,
    }
    engine_request = {
        "current_crop": req.current_crop, "water_source": req.water_source, "water_amount": req.water_amount,
        "salinity": req.salinity, "waterlogging": req.waterlogging, "priority": req.priority,
    }
    try:
        result = recommend(deps.crops, engine_request, engine_features, today or date.today())
    except ValueError:
        return _insufficient("no_data_001")

    if result["status"] != "ok":
        return {"status": "insufficient_data", "reason_id": result["reason_id"],
                "field_health": result.get("field_health")}

    meta = deps.store.meta()
    return {
        "status": "ok",
        "is_demo": deps.store.path.name.endswith("example.json"),
        "data_snapshot": {
            "satellite_window": str(meta.get("satellite_window") or s.default_satellite_window),
            "landsat_date": str(meta.get("landsat_date") or s.default_landsat_date),
        },
        "field_health": result["field_health"],
        "regional_context": _regional_context(feats),
        "forecast": {"available": forecast_ok, "source": "meteomatics",
                     "is_sample": bool(forecast.get("is_sample"))},
        "options": result["options"],
        "disclaimer_id": DISCLAIMER_ID,
    }


def crops_payload(deps: Deps) -> list:
    web_crops = deps.settings.web_dir / "static" / "crops"
    out = []
    for c in deps.crops.values():
        pic = web_crops / f"{c.id}.png"
        out.append({
            "id": c.id, "season": c.season,
            "names": {"en": c.name_en, "ur": c.name_ur, "sd": c.name_sd},
            "picture_url": f"/static/crops/{c.id}.png" if pic.exists() else None,
            "verified": c.verified,
        })
    for cid, (en, ur, sd) in {"sugarcane": ("Sugarcane", "گنا", "ڪمند"),
                              "banana": ("Banana / orchard", "کیلا / باغ", "ڪيلو / باغ")}.items():
        pic = web_crops / f"{cid}.png"
        out.append({"id": cid, "season": None, "names": {"en": en, "ur": ur, "sd": sd},
                    "picture_url": f"/static/crops/{cid}.png" if pic.exists() else None,
                    "verified": False, "special": SPECIAL[cid]})
    return out
~~~

### agrishift/apps/api/app/weather.py

**Bytes:** 4615 · **Lines:** 103 · **SHA-256:** ec5c6103a653383401005ef4cbdda39c524e17118dc28c25bc85323d29afe240

~~~python
"""Meteomatics forecast proxy (credentials stay on the server).

Behaviour (plan section 7):
- credentials + API ok            -> live data (is_sample False), cached 3 h in memory
- credentials, but API/network fails -> saved sample (is_sample True) if data/api-samples/meteomatics_sample.json exists
- no credentials                  -> {"available": False}  (we never show made-up data)... unless DEMO_MODE=1,
                                     then the saved sample is shown, labelled is_sample True
The forecast is NOT part of the rotation score.
"""
from __future__ import annotations

import base64
import json
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

API = "https://api.meteomatics.com"
PARAMS = "t_max_2m_24h:C,precip_24h:mm"
TTL_SECONDS = 3 * 3600
_cache: Dict[Tuple[float, float], Tuple[float, dict]] = {}


def build_url(lat: float, lon: float, start: datetime, days: int = 3) -> str:
    s = start.strftime("%Y-%m-%dT00:00:00Z")
    e = (start + timedelta(days=days - 1)).strftime("%Y-%m-%dT00:00:00Z")
    return f"{API}/{s}--{e}:P1D/{PARAMS}/{lat},{lon}/json"


def parse_meteomatics(payload: dict) -> List[dict]:
    """Meteomatics JSON -> [{"date": "YYYY-MM-DD", "tmax_c": float|None, "rain_mm": float|None}]"""
    by_date: Dict[str, dict] = {}
    for item in payload.get("data", []):
        name = item.get("parameter", "")
        key = "tmax_c" if name.startswith("t_max_2m_24h") else ("rain_mm" if name.startswith("precip_24h") else None)
        if key is None:
            continue
        coords = item.get("coordinates") or []
        if not coords:
            continue
        for d in coords[0].get("dates", []):
            day = str(d.get("date", ""))[:10]
            val = d.get("value")
            if len(day) != 10 or isinstance(val, bool) or not isinstance(val, (int, float)):
                continue
            by_date.setdefault(day, {"date": day, "tmax_c": None, "rain_mm": None})[key] = float(val)
    days = [by_date[k] for k in sorted(by_date) if by_date[k]["tmax_c"] is not None or by_date[k]["rain_mm"] is not None]
    return days


def fetch_meteomatics(lat: float, lon: float, user: str, password: str, now: datetime, timeout: float = 6.0) -> List[dict]:
    url = build_url(lat, lon, now)
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    req = urllib.request.Request(url, headers={"Authorization": f"Basic {token}", "User-Agent": "AgriShiftAI/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        payload = json.loads(r.read().decode("utf-8"))
    return parse_meteomatics(payload)


def _load_sample(samples_dir: Path, today: date) -> Optional[List[dict]]:
    f = Path(samples_dir) / "meteomatics_sample.json"
    if not f.exists():
        return None
    try:
        raw = json.loads(f.read_text(encoding="utf-8"))
        out = []
        for i, d in enumerate(raw["days"]):
            out.append({"date": (today + timedelta(days=i)).isoformat(),
                        "tmax_c": d.get("tmax_c"), "rain_mm": d.get("rain_mm")})
        return out or None
    except Exception:
        return None


def get_weather(lat: float, lon: float, *, user: str, password: str, samples_dir: Path, demo_mode: bool,
                now: Optional[datetime] = None,
                fetcher: Callable[..., List[dict]] = fetch_meteomatics,
                use_cache: bool = True) -> dict:
    now = now or datetime.now(timezone.utc)
    key = (round(lat, 2), round(lon, 2))
    if user and password:
        if use_cache and key in _cache and time.time() - _cache[key][0] < TTL_SECONDS:
            return _cache[key][1]
        try:
            days = fetcher(lat, lon, user, password, now)
            if days:
                info = {"available": True, "source": "meteomatics", "is_sample": False, "days": days}
                if use_cache:
                    _cache[key] = (time.time(), info)
                return info
        except Exception:
            pass
        sample = _load_sample(samples_dir, now.date())
        if sample:
            return {"available": True, "source": "meteomatics", "is_sample": True, "days": sample}
        return {"available": False, "source": "meteomatics", "is_sample": False}
    if demo_mode:
        sample = _load_sample(samples_dir, now.date())
        if sample:
            return {"available": True, "source": "meteomatics", "is_sample": True, "days": sample}
    return {"available": False, "source": "meteomatics", "is_sample": False}
~~~

### agrishift/apps/api/requirements.txt

**Bytes:** 53 · **Lines:** 4 · **SHA-256:** 87b8ce8962a3de185600105392debe5d49a4639387cde4ceaab2245af033094c

~~~text
fastapi>=0.110
uvicorn>=0.29
pydantic>=2.5
pytest>=8
~~~

### agrishift/apps/api/tests/conftest.py

**Bytes:** 154 · **Lines:** 5 · **SHA-256:** 1c2c7907fc8fb1b6c346172eb56ec9c9e81476b5040ddfb5e6bdbcfcdfa88abc

~~~python
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))          # apps/api  (package "app")
~~~

### agrishift/apps/api/tests/test_clients.py

**Bytes:** 6102 · **Lines:** 142 · **SHA-256:** 28ea3ebbcfd106fa6e9e5ff68e6acc493a0ddec6f8faf90618807ae4d61b587d

~~~python
import json
from datetime import date, datetime, timezone

from app import power, weather
from app.features import FeatureStore, haversine_km, normalize


# ---------------------------------------------------------------- POWER
def daily_fixture(years=(2023, 2024)):
    tmax, rain, rh, ws = {}, {}, {}, {}
    for y in years:
        for m in range(1, 13):
            for d in (1, 2, 3, 4):
                key = f"{y}{m:02d}{d:02d}"
                tmax[key] = 41.0 if (m == 5 and d <= 2) else 30.0     # 2 hot days every May
                rain[key] = 1.0
                rh[key] = 50.0
                ws[key] = 2.0
    tmax["20230601"] = -999.0                                          # fill value must be skipped
    return {"T2M_MAX": tmax, "PRECTOTCORR": rain, "RH2M": rh, "WS2M": ws}


def test_power_url_matches_plan():
    u = power.build_url(25.39, 68.37)
    assert u.startswith("https://power.larc.nasa.gov/api/temporal/daily/point?")
    assert "parameters=T2M,T2M_MAX,T2M_MIN,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN" in u
    assert "community=AG" in u and "longitude=68.37" in u and "latitude=25.39" in u
    assert "start=20150101" in u and "end=20251231" in u and "format=JSON" in u


def test_power_summarize():
    out = power.summarize(daily_fixture())
    assert out["heat_days_40c_by_month"][5] == 2.0
    assert out["heat_days_40c_by_month"][1] == 0.0
    assert out["tmax_mean_by_month"][1] == 30.0
    assert out["rain_mm_by_month"][1] == 4.0           # 4 days x 1 mm
    assert out["rh_mean"] == 50.0 and out["wind_mean"] == 2.0
    assert set(out["heat_days_40c_by_month"]) == set(range(1, 13))


def test_power_summarize_needs_all_months():
    d = daily_fixture()
    d["T2M_MAX"] = {k: v for k, v in d["T2M_MAX"].items() if k[4:6] != "02"}
    assert power.summarize(d) is None


def test_power_cache_and_failure(tmp_path):
    calls = []

    def fetcher(lat, lon):
        calls.append(1)
        return daily_fixture()

    a = power.get_monthly_features(25.39, 68.37, tmp_path, tmp_path, fetcher=fetcher)
    b = power.get_monthly_features(25.39, 68.37, tmp_path, tmp_path, fetcher=fetcher)
    assert a == b and len(calls) == 1                   # second call came from the cache
    other = power.get_monthly_features(25.5, 68.5, tmp_path, tmp_path, fetcher=lambda a, b: None)
    assert other is None                                # no network, no cache, no sample -> missing (never invented)


# ---------------------------------------------------------------- Meteomatics
MM = {"data": [
    {"parameter": "t_max_2m_24h:C", "coordinates": [{"lat": 25.39, "lon": 68.37, "dates": [
        {"date": "2026-11-15T00:00:00Z", "value": 31.2}, {"date": "2026-11-16T00:00:00Z", "value": 32.0}]}]},
    {"parameter": "precip_24h:mm", "coordinates": [{"lat": 25.39, "lon": 68.37, "dates": [
        {"date": "2026-11-15T00:00:00Z", "value": 0.0}, {"date": "2026-11-16T00:00:00Z", "value": 2.5}]}]},
]}
NOW = datetime(2026, 11, 15, 8, 0, tzinfo=timezone.utc)


def test_meteomatics_url_and_parse():
    u = weather.build_url(25.39, 68.37, NOW)
    assert u == "https://api.meteomatics.com/2026-11-15T00:00:00Z--2026-11-17T00:00:00Z:P1D/t_max_2m_24h:C,precip_24h:mm/25.39,68.37/json"
    assert weather.parse_meteomatics(MM) == [
        {"date": "2026-11-15", "tmax_c": 31.2, "rain_mm": 0.0},
        {"date": "2026-11-16", "tmax_c": 32.0, "rain_mm": 2.5}]
    assert weather.parse_meteomatics({}) == []


def kw(tmp_path, **o):
    base = dict(user="", password="", samples_dir=tmp_path, demo_mode=False, now=NOW, use_cache=False)
    base.update(o)
    return base


def test_weather_no_credentials_means_unavailable(tmp_path):
    out = weather.get_weather(25.39, 68.37, **kw(tmp_path))
    assert out == {"available": False, "source": "meteomatics", "is_sample": False}


def test_weather_live(tmp_path):
    fetcher = lambda *a, **k: weather.parse_meteomatics(MM)
    out = weather.get_weather(25.39, 68.37, **kw(tmp_path, user="u", password="p", fetcher=fetcher))
    assert out["available"] and not out["is_sample"] and len(out["days"]) == 2


def test_weather_failure_uses_labelled_sample(tmp_path):
    (tmp_path / "meteomatics_sample.json").write_text(json.dumps({"days": [{"tmax_c": 30, "rain_mm": 0}, {"tmax_c": 31, "rain_mm": 1}]}))

    def boom(*a, **k):
        raise OSError("offline")

    out = weather.get_weather(25.39, 68.37, **kw(tmp_path, user="u", password="p", fetcher=boom))
    assert out["available"] and out["is_sample"] is True
    assert out["days"][0]["date"] == "2026-11-15" and out["days"][1]["date"] == "2026-11-16"


def test_weather_failure_without_sample_is_unavailable(tmp_path):
    def boom(*a, **k):
        raise OSError("offline")

    out = weather.get_weather(25.39, 68.37, **kw(tmp_path, user="u", password="p", fetcher=boom))
    assert out["available"] is False


def test_weather_demo_mode_uses_sample_without_credentials(tmp_path):
    (tmp_path / "meteomatics_sample.json").write_text(json.dumps({"days": [{"tmax_c": 30, "rain_mm": 0}]}))
    out = weather.get_weather(25.39, 68.37, **kw(tmp_path, demo_mode=True))
    assert out["is_sample"] is True


# ---------------------------------------------------------------- features
def test_haversine():
    assert abs(haversine_km(25.39, 68.37, 25.39, 68.37)) < 1e-9
    assert 100 < haversine_km(25.39, 68.37, 24.86, 67.01) < 160     # Hyderabad -> Karachi


def test_normalize_rejects_bad_values():
    f = normalize({"ndvi_mean": "0.4", "low_lying_flag": 1, "heat_days_40c_by_month": {"1": 1}}, 0.5)
    assert f["sources"] == [] and f["sources_present"] == 0


def test_feature_store_nearest(tmp_path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps({"points": [
        {"id": "a", "lat": 25.39, "lon": 68.37, "features": {}},
        {"id": "b", "lat": 25.50, "lon": 68.50, "features": {}}]}))
    st = FeatureStore(p, max_km=5)
    assert st.nearest(25.391, 68.371)[0]["id"] == "a"
    assert st.nearest(25.499, 68.499)[0]["id"] == "b"
    assert st.nearest(25.2, 68.2) is None
    assert FeatureStore(tmp_path / "missing.json").available() is False
~~~

### agrishift/apps/api/tests/test_service.py

**Bytes:** 5905 · **Lines:** 127 · **SHA-256:** c0f091ee34137c39162762a85ff8a5052685e6aa509ad5193e4bd3cb69e79828

~~~python
import json
import shutil
from datetime import date
from pathlib import Path

import pytest

from app.config import Settings, get_settings
from app.features import FeatureStore, haversine_km, normalize
from app import service
from app.schemas import AnalyzeRequest

ROOT = get_settings().root
NOV = date(2026, 11, 15)
HEAT = {str(m): 0 for m in range(1, 13)}
HEAT.update({"4": 4, "5": 12, "6": 10, "7": 3, "9": 3})


def point_features(**over):
    f = {"ndvi_mean": 0.45, "ndmi_mean": 0.1, "bsi_mean": 0.05, "surface_temp_c": 35, "cloud_free_fraction": 0.9,
         "elevation_m": 28, "slope_deg": 0.3, "low_lying_flag": False,
         "heat_days_40c_by_month": dict(HEAT), "rh_mean": 50, "wind_mean": 3,
         "smap_surface_mean": 0.21, "gpm_total_mm": 18.2}
    f.update(over)
    return {k: v for k, v in f.items() if v is not None}


def make_deps(tmp_path, features=None, weather=None, power=None, points=True):
    fp = tmp_path / "features.json"
    if points:
        fp.write_text(json.dumps({"meta": {"satellite_window": "2025-09-01/2025-09-30", "landsat_date": "2025-09-22"},
                                  "points": [{"id": "p1", "lat": 25.39, "lon": 68.37,
                                              "features": features if features is not None else point_features()}]}))
    s = get_settings()
    settings = Settings(root=ROOT, demo_mode=False, features_path=fp, crops_csv=ROOT / "knowledge" / "crops.csv",
                        samples_dir=tmp_path, cache_dir=tmp_path, layers_dir=tmp_path, web_dir=tmp_path,
                        meteomatics_user="", meteomatics_password="", cors_origins=["*"])
    d = service.build_deps(settings)
    d.weather_fn = weather or (lambda lat, lon: {"available": True, "source": "meteomatics", "is_sample": False, "days": []})
    d.power_fn = power or (lambda lat, lon: None)
    return d


def req(**kw):
    base = dict(lat=25.39, lon=68.37, radius_m=150, current_crop="cotton", previous_crop="unknown",
                water_source="canal", water_amount="medium", salinity="no", waterlogging="no",
                priority="balanced", language="sd")
    base.update(kw)
    return AnalyzeRequest(**base)


def test_ok_response_matches_contract(tmp_path):
    out = service.analyze(req(), make_deps(tmp_path), NOV)
    assert out["status"] == "ok"
    assert out["data_snapshot"] == {"satellite_window": "2025-09-01/2025-09-30", "landsat_date": "2025-09-22"}
    assert out["field_health"]["template_id"].startswith("health_")
    assert out["forecast"] == {"available": True, "source": "meteomatics", "is_sample": False}
    assert out["disclaimer_id"] == "disclaimer_001"
    assert [o["id"] for o in out["options"]] == ["existing", "balanced", "priority"]
    assert out["regional_context"]["soil_moisture"]["note_id"] == "regional_note_001"
    assert out["regional_context"]["rainfall"]["total_mm"] == 18.2
    json.dumps(out)                      # must be JSON serialisable


def test_all_six_sources_gives_three_dots(tmp_path):
    out = service.analyze(req(), make_deps(tmp_path), NOV)
    assert out["options"][1]["confidence_dots"] == 3


def test_no_forecast_loses_a_dot(tmp_path):
    d = make_deps(tmp_path, weather=lambda a, b: {"available": False, "source": "meteomatics", "is_sample": False})
    out = service.analyze(req(), d, NOV)
    assert out["forecast"]["available"] is False
    assert out["options"][1]["confidence_dots"] == 2


def test_sugarcane_and_banana_not_applicable(tmp_path):
    d = make_deps(tmp_path)
    assert service.analyze(req(current_crop="sugarcane"), d, NOV) == {"status": "not_applicable", "reason_id": "special_long"}
    assert service.analyze(req(current_crop="banana"), d, NOV) == {"status": "not_applicable", "reason_id": "special_perm"}


def test_out_of_area_pin(tmp_path):
    out = service.analyze(req(lat=24.86, lon=67.01), make_deps(tmp_path), NOV)     # Karachi
    assert out == {"status": "insufficient_data", "reason_id": "out_of_area"}


def test_no_features_file_is_insufficient(tmp_path):
    d = make_deps(tmp_path, points=False)
    assert service.analyze(req(), d, NOV) == {"status": "insufficient_data", "reason_id": "no_data_001"}


def test_pin_far_from_any_point_is_insufficient(tmp_path):
    out = service.analyze(req(lat=25.60, lon=68.60), make_deps(tmp_path), NOV)     # inside box, >5 km from point
    assert out["status"] == "insufficient_data" and out["reason_id"] == "no_data_001"


@pytest.mark.parametrize("missing", ["ndvi_mean", "low_lying_flag", "heat_days_40c_by_month"])
def test_missing_core_data_is_insufficient(tmp_path, missing):
    d = make_deps(tmp_path, features=point_features(**{missing: None}))
    assert service.analyze(req(), d, NOV) == {"status": "insufficient_data", "reason_id": "no_data_001"}


def test_cloudy_landsat_is_treated_as_missing(tmp_path):
    d = make_deps(tmp_path, features=point_features(cloud_free_fraction=0.2))
    assert service.analyze(req(), d, NOV)["reason_id"] == "no_data_001"


def test_incomplete_heat_months_are_not_guessed(tmp_path):
    bad = dict(HEAT)
    del bad["2"]
    d = make_deps(tmp_path, features=point_features(heat_days_40c_by_month=bad))
    assert service.analyze(req(), d, NOV)["reason_id"] == "no_data_001"


def test_power_fallback_fills_climate(tmp_path):
    fb = {"heat_days_40c_by_month": {m: 0.0 for m in range(1, 13)}, "rh_mean": 40.0}
    d = make_deps(tmp_path, features=point_features(heat_days_40c_by_month=None), power=lambda a, b: fb)
    assert service.analyze(req(), d, NOV)["status"] == "ok"


def test_smap_gpm_missing_still_ok_but_fewer_dots(tmp_path):
    d = make_deps(tmp_path, features=point_features(smap_surface_mean=None, gpm_total_mm=None))
    out = service.analyze(req(), d, NOV)
    assert out["status"] == "ok"
    assert out["regional_context"] == {}
    assert out["options"][1]["confidence_dots"] == 2      # 4 of 6 sources: 2 missing -> one dot lost
~~~

### agrishift/apps/web/index.html

**Bytes:** 42047 · **Lines:** 644 · **SHA-256:** 3a326cb858d7c213974e96262930e3a8d1e27304b6a3f7e6bb0e1884eae0def8

~~~html
<!doctype html>
<html lang="ur" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#14532d">
<title>AgriShift AI</title>
<link rel="stylesheet" href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Naskh+Arabic:wght@500;700&display=swap">
<style>
:root{--g:#166534;--gd:#14532d;--bg:#f7faf5;--tx:#111;--bd:#cfd8c9;--y:#facc15;--r:#dc2626;--gr:#16a34a}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;background:var(--bg);color:var(--tx);font-family:"Noto Naskh Arabic",system-ui,-apple-system,Segoe UI,Roboto,sans-serif;font-size:20px;line-height:1.5}
body{min-height:100vh;display:flex;flex-direction:column}
header{position:sticky;top:0;z-index:5;background:var(--gd);color:#fff;display:flex;align-items:center;gap:8px;padding:8px 12px}
header .title{font-weight:700;flex:1;text-align:center}
.hbtn{min-width:48px;min-height:48px;border:0;border-radius:12px;background:rgba(255,255,255,.18);color:#fff;font-size:22px;cursor:pointer}
.hbtn[hidden]{visibility:hidden;display:block}
.dots{display:flex;gap:6px;justify-content:center;padding:8px;background:#e8f0e3}
.dots i{width:12px;height:12px;border-radius:50%;background:#b8c7b0}
.dots i.on{background:var(--g)}
main{flex:1;width:100%;max-width:720px;margin:0 auto;padding:12px}
.screen{display:none}.screen.active{display:block}
h2{font-size:1.45rem;margin:8px 0 14px;text-align:center}
.big{width:100%;min-height:64px;border:3px solid var(--g);border-radius:16px;background:#fff;color:var(--tx);font:inherit;font-weight:700;font-size:1.15rem;padding:10px 14px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:10px}
.big.primary{background:var(--g);color:#fff}
.big.sel{background:var(--g);color:#fff;outline:4px solid var(--y)}
.big:disabled{opacity:.45;cursor:not-allowed}
.stack{display:flex;flex-direction:column;gap:12px}
.row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.row .big{flex-direction:column;font-size:1rem;min-height:84px;padding:8px 4px}
.row .big .ic{font-size:2rem}
.qlabel{font-weight:700;margin:16px 0 8px;text-align:center}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.grid .big{flex-direction:column;min-height:104px;padding:6px 2px;font-size:.95rem}
.grid .big .ic{font-size:2.4rem}
#map,#xmap{width:100%;height:46vh;min-height:280px;border-radius:16px;border:3px solid var(--g);margin:12px 0}
.note{background:#fff7d6;border:2px solid var(--y);border-radius:12px;padding:8px 12px;margin:8px 0;font-size:.95rem}
.note.err{background:#fee2e2;border-color:var(--r)}
.card{background:#fff;border:3px solid var(--bd);border-radius:18px;padding:12px;margin:14px 0}
.card.green{border-color:var(--gr)}.card.yellow{border-color:var(--y)}.card.red{border-color:var(--r)}
.card h3{margin:0 0 8px;font-size:1.2rem}
.seasons{display:flex;align-items:center;justify-content:center;gap:10px;margin:8px 0}
.crop{flex:1;text-align:center;background:#f1f6ee;border-radius:14px;padding:8px 4px}
.crop .ic{font-size:3.2rem;line-height:1.1}.crop .cn{font-weight:700}.crop .sn{font-size:.85rem;color:#444}
.arrow{font-size:1.8rem}html[dir=rtl] .arrow{transform:scaleX(-1)}
.meta{display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;margin:8px 0}
.chip{border-radius:999px;padding:2px 12px;font-weight:700;font-size:.95rem;border:2px solid #999}
.chip.green{background:#dcfce7;border-color:var(--gr)}.chip.yellow{background:#fef9c3;border-color:var(--y)}.chip.red{background:#fee2e2;border-color:var(--r)}
.why{margin:6px 0;padding-inline-start:20px}.why li{margin:3px 0}
.caution{color:#7a4b00;font-weight:700}
.expert{font-weight:800;color:#b91c1c}
.acts{display:flex;gap:8px;margin-top:10px}.acts .big{min-height:56px;font-size:1rem}
.foot{font-size:.9rem;color:#333;text-align:center;margin:10px 0}
.badge{display:inline-block;background:#e0e7ff;border:2px solid #6366f1;border-radius:8px;padding:0 8px;font-size:.85rem;font-weight:700}
.spin{width:64px;height:64px;border:8px solid #cfe5d2;border-top-color:var(--g);border-radius:50%;margin:40px auto;animation:sp 1s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.fc{display:flex;gap:8px;justify-content:space-around;font-size:2.2rem;text-align:center}
.xbar{display:flex;flex-wrap:wrap;gap:8px}.xbar .big{min-height:48px;width:auto;font-size:.95rem;flex:1}
table{width:100%;border-collapse:collapse;font-size:.85rem;direction:ltr;text-align:left}
td,th{border:1px solid var(--bd);padding:4px 6px;vertical-align:top}th{background:#e8f0e3}
.xp{direction:ltr;text-align:left;font-size:.95rem}
footer{padding:10px;text-align:center;font-size:.85rem;color:#444}
footer a{color:var(--g)}
</style>
</head>
<body>
<header>
  <button class="hbtn" id="backBtn" data-act="back" hidden aria-label="back">◀</button>
  <div class="title">🌾 AgriShift AI</div>
  <button class="hbtn" id="replayBtn" data-act="replay" aria-label="listen again">🔊</button>
</header>
<div class="dots" id="dots"></div>

<main>
<!-- 0 language -->
<section class="screen active" id="s0">
  <h2>زبان / ٻولي / Language</h2>
  <div class="stack">
    <button class="big" data-act="lang" data-v="sd">🗣️ سنڌي</button>
    <button class="big" data-act="lang" data-v="ur">🗣️ اردو</button>
    <button class="big" data-act="lang" data-v="en">🗣️ English</button>
  </div>
</section>

<!-- 1 location -->
<section class="screen" id="s1">
  <h2 data-i="q_where"></h2>
  <button class="big primary" data-act="gps">📍 <span data-i="btn_here"></span></button>
  <div id="map"></div>
  <p class="foot" data-i="tap_map"></p>
  <div id="locNote" class="note err" style="display:none"></div>
  <button class="big primary" id="next1" data-act="next1" disabled>✅ <span data-i="btn_next"></span></button>
</section>

<!-- 2 crop -->
<section class="screen" id="s2">
  <h2 data-i="q_crop"></h2>
  <div class="grid" id="cropGrid"></div>
</section>

<!-- 3 water -->
<section class="screen" id="s3">
  <h2 data-i="q_water"></h2>
  <div class="row">
    <button class="big" data-act="src" data-v="canal"><span class="ic">🌊</span><span data-i="src_canal"></span></button>
    <button class="big" data-act="src" data-v="tubewell"><span class="ic">⛲</span><span data-i="src_tubewell"></span></button>
    <button class="big" data-act="src" data-v="rain"><span class="ic">🌧️</span><span data-i="src_rain"></span></button>
  </div>
  <div class="qlabel" data-i="q_amount"></div>
  <div class="row">
    <button class="big" data-act="amt" data-v="low"><span class="ic">💧</span><span data-i="amt_low"></span></button>
    <button class="big" data-act="amt" data-v="medium"><span class="ic">💧💧</span><span data-i="amt_med"></span></button>
    <button class="big" data-act="amt" data-v="high"><span class="ic">💧💧💧</span><span data-i="amt_high"></span></button>
  </div>
</section>

<!-- 4 salinity / waterlogging -->
<section class="screen" id="s4">
  <h2 data-i="q_salinity"></h2>
  <div class="row">
    <button class="big" data-act="sal" data-v="yes"><span class="ic">✅</span><span data-i="yes"></span></button>
    <button class="big" data-act="sal" data-v="no"><span class="ic">❌</span><span data-i="no"></span></button>
    <button class="big" data-act="sal" data-v="unknown"><span class="ic">❓</span><span data-i="unknown"></span></button>
  </div>
  <div class="qlabel" data-i="q_waterlog"></div>
  <div class="row">
    <button class="big" data-act="wl" data-v="yes"><span class="ic">✅</span><span data-i="yes"></span></button>
    <button class="big" data-act="wl" data-v="no"><span class="ic">❌</span><span data-i="no"></span></button>
    <button class="big" data-act="wl" data-v="unknown"><span class="ic">❓</span><span data-i="unknown"></span></button>
  </div>
</section>

<!-- 5 priority -->
<section class="screen" id="s5">
  <h2 data-i="q_priority"></h2>
  <div class="stack">
    <button class="big" data-act="prio" data-v="save_water">💧 <span data-i="pr_save_water"></span></button>
    <button class="big" data-act="prio" data-v="improve_soil">🌱 <span data-i="pr_improve_soil"></span></button>
    <button class="big" data-act="prio" data-v="balanced">⚖️ <span data-i="pr_balanced"></span></button>
  </div>
</section>

<!-- 6 results -->
<section class="screen" id="s6"><div id="results"></div></section>

<!-- loading -->
<section class="screen" id="sl"><div class="spin"></div><h2 data-i="loading"></h2></section>

<!-- error / message -->
<section class="screen" id="se">
  <div class="note err" id="errMsg" style="font-size:1.2rem;text-align:center"></div>
  <div class="stack">
    <button class="big primary" id="retryBtn" data-act="retry">🔄 <span data-i="btn_retry"></span></button>
    <button class="big" data-act="restart">🏠 <span data-i="btn_restart"></span></button>
  </div>
</section>

<!-- special crops -->
<section class="screen" id="sp">
  <div class="note" id="spMsg" style="font-size:1.25rem;text-align:center"></div>
  <button class="big primary" data-act="restart">🏠 <span data-i="btn_restart"></span></button>
</section>

<!-- expert view -->
<section class="screen" id="sx">
  <div class="xp">
    <h2 style="text-align:left">Expert / Extension officer view</h2>
    <div class="xbar">
      <button class="big sel" data-act="layer" data-v="none">Base map</button>
      <button class="big" data-act="layer" data-v="ndvi">NDVI</button>
      <button class="big" data-act="layer" data-v="ndmi">NDMI</button>
      <button class="big" data-act="layer" data-v="bsi">BSI</button>
      <button class="big" data-act="layer" data-v="slope">Slope</button>
    </div>
    <div id="xmap"></div>
    <div id="xnote" class="note" style="display:none"></div>
    <div id="xinfo"></div>
    <button class="big" data-act="exitx">◀ Farmer view</button>
  </div>
</section>
</main>

<footer>
  <div id="snap"></div>
  <a href="#/expert">Expert view</a>
</footer>

<script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>
<script>
/* ================= CONFIG ================= */
const CONFIG = {
  API_BASE: "",            // e.g. "https://your-api.onrender.com" (empty = same origin)
  USE_MOCK: (new URLSearchParams(location.search).get("mock") === "1") || location.protocol === "file:", // demo data when opened as a file or with ?mock=1; otherwise the real API
  RADIUS_M: 150,
  PILOT: {lat: 25.39, lon: 68.37},
  BOUNDS: {minLat: 25.1, maxLat: 25.7, minLon: 68.1, maxLon: 68.7},          // pilot area check
  LAYER_BOUNDS: {w: 68.17, s: 25.19, e: 68.57, n: 25.59},                      // TODO Member 4: real overlay PNG bounds
  AUDIO_DIR: "audio"       // audio/<lang>/<id>.mp3
};

/* ============ TRANSLATIONS (sd / ur need native-speaker check) ============ */
const I18N = {
en:{
 pick_lang:"Choose language", q_where:"Where is your field?", btn_here:"I am here", tap_map:"Or tap on the map",
 q_crop:"Current or last crop?", q_water:"Where does your water come from?", q_amount:"How much water do you get?",
 src_canal:"Canal", src_tubewell:"Tubewell", src_rain:"Rain", amt_low:"Little", amt_med:"Medium", amt_high:"A lot",
 q_salinity:"Is there salt in the soil?", q_waterlog:"Does water stay standing in the field?",
 yes:"Yes", no:"No", unknown:"Don't know", q_priority:"What do you want?",
 pr_save_water:"Save water", pr_improve_soil:"Better soil", pr_balanced:"Both",
 loading:"Checking your field…", opt_existing:"Your current way", opt_balanced:"Balanced option", opt_priority:"Save water + better soil",
 season_rabi:"Rabi", season_kharif:"Kharif", btn_listen:"Listen", btn_whatsapp:"WhatsApp", btn_restart:"Start again", btn_retry:"Try again", btn_next:"Next",
 snapshot:"Satellite data: September 2025 snapshot.", ask_expert:"Please ask your local agriculture expert.",
 expert_pending:"Expert verification pending.", expert_must:"Definitely ask an expert!", confidence:"Confidence", water_need:"Water need",
 warn_red:"Warning – not recommended", mock_badge:"Demo data",
 disclaimer_001:"AgriShift AI only gives data-based possibilities and risk signals. It does not replace field inspection, soil tests, farmer experience, or advice from agriculture experts.",
 special_long:"Your field is busy with a long-duration crop. Rotation advice is not suitable now. Try again after harvest.",
 special_perm:"This is a permanent crop. Rotation does not apply.",
 out_of_area:"Right now only the Hyderabad area is covered.", gps_fail:"Could not get location. Tap the map.",
 err_data:"Data not found right now.", no_data_001:"Not enough data for this place. We do not guess.",
 health_good_001:"Your field looks healthy.", health_moderate_001:"Your field's health is moderate.", health_poor_001:"Your field looks weak.",
 why_water_ok_001:"Water need fits the water you have.", why_known_crop_002:"You already know this crop well.",
 why_legume_001:"A legume crop puts nitrogen back into the soil.", why_water_save_001:"It needs less water.",
 why_soil_help_001:"It is good for the soil.", why_heat_ok_001:"It handles heat well.",
 caution_late_sowing_001:"Sowing may get late.", caution_waterlog_001:"If rain is heavy, water may stand in the field.",
 caution_heat_001:"It may face very hot days.", caution_rule_water_001:"It needs more water than you have.", caution_rule_salt_001:"It does not handle salty soil.", caution_rule_waterlog_001:"It does not like standing water.", caution_rule_repeat_001:"The same crop again is not good for the soil.", caution_rule_overlap_001:"Sowing would clash with the earlier harvest.", no_safe_option_001:"No safe option found for this field. Please ask an expert.",
 fc_title:"Today's forecast", fc_sample:"Saved sample", fc_none:"Not available now",
 regional_note_001:"Soil moisture is regional (about 9 km), not your field.", regional_note_002:"Rainfall is regional (about 10 km), not your field.",
 crop_cotton:"Cotton", crop_rice:"Rice", crop_mung_bean:"Mung bean", crop_sorghum:"Sorghum", crop_millet:"Millet", crop_sesame:"Sesame",
 crop_maize:"Maize", crop_sunflower:"Sunflower", crop_wheat:"Wheat", crop_chickpea:"Chickpea", crop_mustard:"Mustard", crop_berseem:"Berseem",
 crop_sugarcane:"Sugarcane", crop_banana:"Banana / orchard"
},
ur:{
 pick_lang:"زبان چنیں", q_where:"آپ کا کھیت کہاں ہے؟", btn_here:"میں یہاں ہوں", tap_map:"یا نقشے پر انگلی رکھیں",
 q_crop:"ابھی یا پچھلی فصل کون سی تھی؟", q_water:"پانی کہاں سے آتا ہے؟", q_amount:"کتنا پانی ملتا ہے؟",
 src_canal:"نہر", src_tubewell:"ٹیوب ویل", src_rain:"بارش", amt_low:"کم", amt_med:"درمیانہ", amt_high:"زیادہ",
 q_salinity:"کیا زمین میں کھارا پن ہے؟", q_waterlog:"کیا کھیت میں پانی کھڑا رہتا ہے؟",
 yes:"ہاں", no:"نہیں", unknown:"پتہ نہیں", q_priority:"آپ کیا چاہتے ہیں؟",
 pr_save_water:"پانی بچائیں", pr_improve_soil:"زمین بہتر کریں", pr_balanced:"دونوں ٹھیک",
 loading:"آپ کے کھیت کا جائزہ لیا جا رہا ہے…", opt_existing:"آپ کا طریقہ", opt_balanced:"متوازن آپشن", opt_priority:"پانی بچائیں + زمین بہتر",
 season_rabi:"ربیع", season_kharif:"خریف", btn_listen:"سنیں", btn_whatsapp:"واٹس ایپ", btn_restart:"دوبارہ شروع کریں", btn_retry:"دوبارہ کوشش کریں", btn_next:"آگے",
 snapshot:"سیٹلائٹ ڈیٹا: ستمبر 2025 کا اسنیپ شاٹ۔", ask_expert:"اپنے علاقے کے زرعی ماہر سے ضرور پوچھیں۔",
 expert_pending:"ماہر سے تصدیق باقی۔", expert_must:"ماہر سے ضرور پوچھیں!", confidence:"بھروسہ", water_need:"پانی کی ضرورت",
 warn_red:"خبردار – مشورہ نہیں", mock_badge:"ڈیمو ڈیٹا",
 disclaimer_001:"ایگری شفٹ اے آئی صرف ڈیٹا پر مبنی امکانات اور خطرے کے اشارے دیتا ہے۔ یہ کھیت کے معائنے، مٹی کے ٹیسٹ، کسان کے تجربے یا زرعی ماہرین کے مشورے کی جگہ نہیں لیتا۔",
 special_long:"آپ کا کھیت لمبے عرصے کے لیے مصروف ہے۔ ابھی روٹیشن کا مشورہ مناسب نہیں۔ گنا کاٹنے کے بعد دوبارہ کوشش کریں۔",
 special_perm:"یہ دائمی فصل ہے۔ روٹیشن لاگو نہیں۔",
 out_of_area:"ابھی صرف حیدرآباد کا علاقہ شامل ہے۔", gps_fail:"جگہ نہیں ملی۔ نقشے پر انگلی رکھیں۔",
 err_data:"ڈیٹا ابھی نہیں ملا۔", no_data_001:"اس جگہ کا ڈیٹا کافی نہیں۔ ہم اندازہ نہیں لگاتے۔",
 health_good_001:"آپ کا کھیت صحت مند لگتا ہے۔", health_moderate_001:"آپ کے کھیت کی صحت درمیانی ہے۔", health_poor_001:"آپ کا کھیت کمزور لگتا ہے۔",
 why_water_ok_001:"پانی کی ضرورت آپ کے دستیاب پانی کے مطابق ہے۔", why_known_crop_002:"یہ فصل آپ پہلے سے جانتے ہیں۔",
 why_legume_001:"دال والی فصل زمین میں نائٹروجن واپس ڈالتی ہے۔", why_water_save_001:"اس میں پانی کم لگتا ہے۔",
 why_soil_help_001:"یہ زمین کے لیے فائدہ مند ہے۔", why_heat_ok_001:"یہ گرمی برداشت کر لیتی ہے۔",
 caution_late_sowing_001:"بوائی میں دیر ہو سکتی ہے۔", caution_waterlog_001:"بارش زیادہ ہو تو کھیت میں پانی کھڑا ہو سکتا ہے۔",
 caution_heat_001:"اس میں بہت گرم دنوں کا خطرہ ہو سکتا ہے۔", caution_rule_water_001:"اسے آپ کے پانی سے زیادہ پانی چاہیے۔", caution_rule_salt_001:"یہ کھارا پن برداشت نہیں کرتی۔", caution_rule_waterlog_001:"اسے کھڑا پانی پسند نہیں۔", caution_rule_repeat_001:"وہی فصل دوبارہ لگانا زمین کے لیے اچھا نہیں۔", caution_rule_overlap_001:"بوائی پچھلی فصل کی کٹائی سے ٹکرا جائے گی۔", no_safe_option_001:"اس کھیت کے لیے کوئی محفوظ آپشن نہیں ملا۔ ماہر سے پوچھیں۔",
 fc_title:"آج کا فورکاسٹ", fc_sample:"محفوظ نمونہ", fc_none:"ابھی دستیاب نہیں",
 crop_cotton:"کپاس", crop_rice:"چاول", crop_mung_bean:"مونگ", crop_sorghum:"جوار", crop_millet:"باجرہ", crop_sesame:"تل",
 crop_maize:"مکئی", crop_sunflower:"سورج مکھی", crop_wheat:"گندم", crop_chickpea:"چنا", crop_mustard:"سرسوں", crop_berseem:"برسیم",
 crop_sugarcane:"گنا", crop_banana:"کیلا / باغ"
},
sd:{
 pick_lang:"ٻولي چونڊيو", q_where:"توهان جو ٻنو ڪٿي آهي؟", btn_here:"مان هتي آهيان", tap_map:"يا نقشي تي آڱر رکو",
 q_crop:"هاڻوڪو يا پوئين فصل ڪهڙو هو؟", q_water:"پاڻي ڪٿان ٿو اچي؟", q_amount:"ڪيترو پاڻي ملي ٿو؟",
 src_canal:"واهه", src_tubewell:"ٽيوب ويل", src_rain:"برسات", amt_low:"گهٽ", amt_med:"وچولو", amt_high:"گهڻو",
 q_salinity:"ڇا زمين ۾ کاراڻ آهي؟", q_waterlog:"ڇا ٻني ۾ پاڻي بيٺل رهي ٿو؟",
 yes:"ها", no:"نه", unknown:"خبر ناهي", q_priority:"توهان ڇا ٿا چاهيو؟",
 pr_save_water:"پاڻي بچايو", pr_improve_soil:"زمين بهتر ڪريو", pr_balanced:"ٻئي ٺيڪ",
 loading:"توهان جي ٻني جو جائزو ورتو پيو وڃي…", opt_existing:"توهان جو طريقو", opt_balanced:"متوازن چونڊ", opt_priority:"پاڻي بچايو + زمين بهتر",
 season_rabi:"ربيع", season_kharif:"خريف", btn_listen:"ٻڌو", btn_whatsapp:"واٽس ايپ", btn_restart:"ٻيهر شروع ڪريو", btn_retry:"ٻيهر ڪوشش ڪريو", btn_next:"اڳتي",
 snapshot:"سيٽلائيٽ ڊيٽا: سيپٽمبر 2025 جو اسنيپ شاٽ.", ask_expert:"پنهنجي علائقي جي زرعي ماهر کان ضرور پڇو.",
 expert_pending:"ماهر کان تصديق باقي.", expert_must:"ماهر کان ضرور پڇو!", confidence:"ڀروسو", water_need:"پاڻي جي ضرورت",
 warn_red:"خبردار – صلاح ناهي", mock_badge:"ڊيمو ڊيٽا",
 disclaimer_001:"ايگري شفٽ اي آئي صرف ڊيٽا تي ٻڌل امڪان ۽ خطري جا اشارا ڏئي ٿو. هي ٻني جي معائني، مٽيءَ جي ٽيسٽ، هاريءَ جي تجربي يا زرعي ماهرن جي صلاح جي جاءِ نٿو وٺي.",
 special_long:"توهان جي ٻني ڊگهي عرصي لاءِ مصروف آهي. هينئر روٽيشن جي صلاح مناسب ناهي. ڪمند ڪٽڻ کانپوءِ ٻيهر ڪوشش ڪريو.",
 special_perm:"هيءَ دائمي فصل آهي. روٽيشن لاڳو ناهي.",
 out_of_area:"هينئر صرف حيدرآباد جو علائقو شامل آهي.", gps_fail:"جاءِ ڪانه ملي. نقشي تي آڱر رکو.",
 err_data:"ڊيٽا هينئر نه ملي.", no_data_001:"هن جاءِ جو ڊيٽا ڪافي ناهي. اسان اندازو نٿا لڳايون.",
 health_good_001:"توهان جي ٻني صحتمند لڳي ٿي.", health_moderate_001:"توهان جي ٻنيءَ جي صحت وچولي آهي.", health_poor_001:"توهان جي ٻني ڪمزور لڳي ٿي.",
 why_water_ok_001:"پاڻيءَ جي ضرورت توهان وٽ موجود پاڻيءَ مطابق آهي.", why_known_crop_002:"هي فصل توهان اڳ ۾ ئي ڄاڻو ٿا.",
 why_legume_001:"ڏاڻن واري فصل زمين ۾ نائٽروجن موٽائي ٿي.", why_water_save_001:"ان ۾ پاڻي گهٽ لڳندو.",
 why_soil_help_001:"هي زمين لاءِ فائديمند آهي.", why_heat_ok_001:"هيءَ گرمي برداشت ڪري ٿي.",
 caution_late_sowing_001:"پوکي ۾ دير ٿي سگهي ٿي.", caution_waterlog_001:"برسات گهڻي ٿئي ته ٻني ۾ پاڻي بيهي سگهي ٿو.",
 caution_heat_001:"ان کي تمام گرم ڏينهن جو خطرو ٿي سگهي ٿو.", caution_rule_water_001:"ان کي توهان وٽ موجود پاڻي کان وڌيڪ پاڻي گهرجي.", caution_rule_salt_001:"هيءَ کاراڻ برداشت نٿي ڪري.", caution_rule_waterlog_001:"ان کي بيٺل پاڻي نه وڻي.", caution_rule_repeat_001:"ساڳيو فصل ٻيهر پوکڻ زمين لاءِ سٺو ناهي.", caution_rule_overlap_001:"پوکي اڳئين فصل جي لاباري سان ٽڪرائجي ويندي.", no_safe_option_001:"هن ٻني لاءِ ڪا محفوظ چونڊ نه ملي. ماهر کان پڇو.",
 fc_title:"اڄ جو فورڪاسٽ", fc_sample:"محفوظ نمونو", fc_none:"هينئر موجود ناهي",
 crop_cotton:"ڪپهه", crop_rice:"چانور", crop_mung_bean:"مُنگ", crop_sorghum:"جوار", crop_millet:"ٻاجهري", crop_sesame:"ٽل",
 crop_maize:"مڪئي", crop_sunflower:"سج مکي", crop_wheat:"ڪڻڪ", crop_chickpea:"چڻا", crop_mustard:"سرنهن", crop_berseem:"برسيم",
 crop_sugarcane:"ڪمند", crop_banana:"ڪيلو / باغ"
}};

const CROPS = [
 ["cotton","☁️"],["rice","🍚"],["mung_bean","🫘"],["sorghum","🌾"],["millet","🌾"],["sesame","🌱"],
 ["maize","🌽"],["sunflower","🌻"],["wheat","🌾"],["chickpea","🫛"],["mustard","🌼"],["berseem","🍀"],
 ["sugarcane","🎋"],["banana","🍌"]
];
const SPECIAL = {sugarcane:"special_long", banana:"special_perm"};
const SPECIAL_IDS = Object.values(SPECIAL);
const CROP_ICON = Object.fromEntries(CROPS);
const ORDER = ["s0","s1","s2","s3","s4","s5","s6"];
const SCREEN_AUDIO = {s0:["welcome"], s1:["q_where"], s2:["q_crop"], s3:["q_water","q_amount"], s4:["q_salinity","q_waterlog"], s5:["q_priority"], s6:["result_intro"]};
const LIGHT_EMOJI = {green:"🟢", yellow:"🟡", red:"🔴"};

/* ================= STATE ================= */
const S = {lang:null, lat:null, lon:null, inArea:false, currentCrop:null, waterSource:null, waterAmount:null,
           salinity:null, waterlogging:null, priority:null, result:null, cur:"s0", touched:false};

const $ = (id) => document.getElementById(id);
const t = (k) => (I18N[S.lang] && I18N[S.lang][k]) || I18N.en[k] || "";

/* ================= AUDIO (pre-recorded files only, no TTS) ================= */
let audioToken = 0, audioEl = null;
function stopAudio(){ audioToken++; if(audioEl){ try{audioEl.pause();}catch(e){} audioEl=null; } }
function playSeq(ids){
  if(!S.touched || !S.lang) return;
  stopAudio();
  const my = audioToken, q = ids.slice();
  (function next(){
    if(my !== audioToken || !q.length) return;
    const a = new Audio(CONFIG.AUDIO_DIR + "/" + S.lang + "/" + q.shift() + ".mp3");
    audioEl = a;
    a.onended = next; a.onerror = next;
    const p = a.play(); if(p && p.catch) p.catch(next);
  })();
}

/* ================= UI helpers ================= */
function applyI18n(){
  document.documentElement.lang = S.lang || "ur";
  document.documentElement.dir = (S.lang === "en") ? "ltr" : "rtl";
  document.querySelectorAll("[data-i]").forEach(el => { el.textContent = t(el.dataset.i); });
  $("snap").textContent = S.lang ? t("snapshot") : "";
  buildCropGrid();
}
function buildCropGrid(){
  $("cropGrid").innerHTML = CROPS.map(([id,ic]) =>
    `<button class="big${S.currentCrop===id?" sel":""}" data-act="crop" data-v="${id}"><span class="ic">${ic}</span><span>${t("crop_"+id)}</span></button>`).join("");
}
function buildDots(){
  $("dots").innerHTML = ORDER.map(()=>"<i></i>").join("");
}
function show(id){
  S.cur = id;
  document.querySelectorAll(".screen").forEach(s => s.classList.toggle("active", s.id === id));
  const idx = ORDER.indexOf(id);
  $("dots").style.display = idx >= 0 ? "flex" : "none";
  [...$("dots").children].forEach((d,i)=>d.classList.toggle("on", i<=idx));
  $("backBtn").hidden = !(idx >= 1);
  window.scrollTo(0,0);
}
function go(id){
  show(id);
  if(id === "s1") initMap();
  if(SCREEN_AUDIO[id]) playSeq(SCREEN_AUDIO[id]);
}
function mark(act, v){
  document.querySelectorAll(`[data-act="${act}"]`).forEach(b => b.classList.toggle("sel", b.dataset.v === v));
}
function showMsg(msg, canRetry){
  $("errMsg").textContent = msg;
  $("retryBtn").style.display = canRetry ? "flex" : "none";
  show("se");
}

/* ================= MAP (farmer) ================= */
let map = null, marker = null;
function baseStyle(){
  return {version:8, sources:{osm:{type:"raster", tileSize:256, attribution:"© OpenStreetMap",
    tiles:["https://tile.openstreetmap.org/{z}/{x}/{y}.png"]}}, layers:[{id:"osm", type:"raster", source:"osm"}]};
}
function initMap(){
  if(map){ setTimeout(()=>map.resize(),50); return; }
  if(typeof maplibregl === "undefined"){ $("map").innerHTML = '<div class="note err">Map not loaded (internet?). Use the 📍 button.</div>'; return; }
  map = new maplibregl.Map({container:"map", style:baseStyle(), center:[CONFIG.PILOT.lon, CONFIG.PILOT.lat], zoom:10});
  map.addControl(new maplibregl.NavigationControl({showCompass:false}));
  map.on("click", e => setPin(e.lngLat.lat, e.lngLat.lng, false));
}
function inArea(lat, lon){
  const b = CONFIG.BOUNDS; return lat>=b.minLat && lat<=b.maxLat && lon>=b.minLon && lon<=b.maxLon;
}
function setPin(lat, lon, fly){
  S.lat = lat; S.lon = lon; S.inArea = inArea(lat, lon);
  if(map){
    if(!marker){
      marker = new maplibregl.Marker({color:"#dc2626", draggable:true}).setLngLat([lon,lat]).addTo(map);
      marker.on("dragend", () => { const p = marker.getLngLat(); setPin(p.lat, p.lng, false); });
    } else marker.setLngLat([lon,lat]);
    if(fly) map.flyTo({center:[lon,lat], zoom:15});
  }
  const n = $("locNote");
  if(S.inArea){ n.style.display = "none"; }
  else { n.textContent = t("out_of_area"); n.style.display = "block"; }
  $("next1").disabled = !S.inArea;
}
function useGps(){
  const n = $("locNote");
  if(!navigator.geolocation){ n.textContent = t("gps_fail"); n.style.display = "block"; return; }
  navigator.geolocation.getCurrentPosition(
    p => setPin(p.coords.latitude, p.coords.longitude, true),
    () => { n.textContent = t("gps_fail"); n.style.display = "block"; },
    {enableHighAccuracy:true, timeout:10000});
}

/* ================= API ================= */
function today(offset){ const d = new Date(); d.setDate(d.getDate()+offset); return d.toISOString().slice(0,10); }
function mockAnalyze(){
  return {
    status:"ok",
    data_snapshot:{satellite_window:"2025-09-01/2025-09-30", landsat_date:"2025-09-22"},
    field_health:{light:"yellow", template_id:"health_moderate_001"},
    regional_context:{soil_moisture:{value:0.21, unit:"m3/m3", resolution_km:9, note_id:"regional_note_001"},
                      rainfall:{total_mm:18.2, resolution_km:10, note_id:"regional_note_002"}},
    forecast:{available:true, source:"meteomatics", is_sample:true},
    options:[
      {id:"existing", seasons:[{season:"rabi_2026_27",crop:"wheat"},{season:"kharif_2027",crop:"cotton"}], light:"yellow", water_drops:2, score:61, confidence_dots:2,
       why_ids:["why_water_ok_001","why_known_crop_002"], caution_ids:["caution_late_sowing_001"], expert_needed:true, crop_verified:false},
      {id:"balanced", seasons:[{season:"rabi_2026_27",crop:"mustard"},{season:"kharif_2027",crop:"mung_bean"}], light:"green", water_drops:1, score:74, confidence_dots:2,
       why_ids:["why_water_save_001","why_legume_001"], caution_ids:["caution_waterlog_001"], expert_needed:true, crop_verified:false},
      {id:"priority", seasons:[{season:"rabi_2026_27",crop:"chickpea"},{season:"kharif_2027",crop:"sesame"}], light:"green", water_drops:1, score:79, confidence_dots:1,
       why_ids:["why_water_save_001","why_soil_help_001"], caution_ids:[], expert_needed:true, crop_verified:false}
    ],
    disclaimer_id:"disclaimer_001"
  };
}
function mockWeather(){
  return {available:true, source:"meteomatics", is_sample:true,
    days:[{date:today(0),tmax_c:31,rain_mm:0},{date:today(1),tmax_c:32,rain_mm:0},{date:today(2),tmax_c:30,rain_mm:3}]};
}
async function fetchJson(url, opts, ms){
  const ac = new AbortController(); const to = setTimeout(()=>ac.abort(), ms || 15000);
  try{
    const r = await fetch(url, Object.assign({signal:ac.signal}, opts||{}));
    if(!r.ok) throw new Error("HTTP "+r.status);
    return await r.json();
  } finally { clearTimeout(to); }
}
function payload(){
  return {lat:S.lat, lon:S.lon, radius_m:CONFIG.RADIUS_M, current_crop:S.currentCrop, previous_crop:"unknown",
    water_source:S.waterSource, water_amount:S.waterAmount, salinity:S.salinity, waterlogging:S.waterlogging,
    priority:S.priority, language:S.lang};
}
async function analyze(){
  show("sl"); stopAudio();
  try{
    let res;
    if(CONFIG.USE_MOCK){ await new Promise(r=>setTimeout(r,700)); res = mockAnalyze(); }
    else res = await fetchJson(CONFIG.API_BASE + "/api/v1/analyze", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload())}, 20000);
    S.result = res;
    if(res.status === "ok" && Array.isArray(res.options) && res.options.length){ renderResults(res); go("s6"); }
    else if(res.status === "not_applicable" && SPECIAL_IDS.includes(res.reason_id)){ $("spMsg").textContent = t(res.reason_id); show("sp"); playSeq([res.reason_id]); }
    else if(res.status === "insufficient_data"){ showMsg(t(res.reason_id) || t("no_data_001"), false); }
    else showMsg(t("err_data"), true);
  } catch(e){ showMsg(t("err_data"), true); }
}
async function getWeather(){
  try{
    if(CONFIG.USE_MOCK) return mockWeather();
    const lat = S.lat ?? CONFIG.PILOT.lat, lon = S.lon ?? CONFIG.PILOT.lon;
    return await fetchJson(`${CONFIG.API_BASE}/api/v1/weather?lat=${lat}&lon=${lon}`, null, 10000);
  } catch(e){ return {available:false}; }
}

/* ================= RESULTS ================= */
function seasonLabel(code){
  const m = /^([a-z]+)_(.+)$/.exec(code || "");
  if(!m) return "";
  return (t("season_" + m[1]) || m[1]) + " " + m[2].replace("_","-");
}
function optTitle(id){ return t("opt_" + id) || ""; }
function sentences(ids){ return (ids||[]).map(i => t(i)).filter(Boolean); }
function drops(n){ return "💧".repeat(Math.max(1, Math.min(3, n|0))); }
function dots(n){ n = Math.max(0, Math.min(3, n|0)); return "●".repeat(n) + "○".repeat(3-n); }

function cardHtml(o, idx){
  const why = sentences(o.why_ids), cau = sentences(o.caution_ids);
  const seasons = (o.seasons||[]).map(s =>
    `<div class="crop"><div class="ic">${CROP_ICON[s.crop]||"🌿"}</div><div class="cn">${t("crop_"+s.crop)}</div><div class="sn">${seasonLabel(s.season)}</div></div>`
  ).join('<div class="arrow">➜</div>');
  return `<div class="card ${o.light}">
    <h3>${LIGHT_EMOJI[o.light]||""} ${optTitle(o.id)}</h3>
    ${seasons}
    <div class="meta">
      <span class="chip ${o.light}">${LIGHT_EMOJI[o.light]||""}${o.light==="red" ? " "+t("warn_red") : ""}</span>
      <span title="${t("water_need")}">${drops(o.water_drops)}</span>
      <span title="${t("confidence")}" style="direction:ltr">${dots(o.confidence_dots)}</span>
    </div>
    ${why.length ? `<ul class="why">${why.map(s=>`<li>${s}</li>`).join("")}</ul>` : ""}
    ${cau.length ? `<div class="caution">⚠️ ${cau.join(" ")}</div>` : ""}
    ${o.crop_verified === false ? `<div class="foot">🔬 ${t("expert_pending")}</div>` : ""}
    ${(o.expert_needed || (o.confidence_dots|0) <= 1) ? `<div class="expert">👨‍🌾 ${t("expert_must")}</div>` : ""}
    <div class="acts">
      <button class="big" data-act="listen" data-i="${idx}">🔊 ${t("btn_listen")}</button>
      <button class="big" data-act="wa" data-i="${idx}">📲 ${t("btn_whatsapp")}</button>
    </div>
    <div class="foot">${t("ask_expert")}</div>
  </div>`;
}
function fcHtml(w){
  let body;
  if(!w || !w.available || !Array.isArray(w.days)) body = `<div class="foot">${t("fc_none")}</div>`;
  else body = `<div class="fc">${w.days.slice(0,3).map(d => (d.rain_mm>=1 ? "🌧️" : (d.tmax_c>=40 ? "🔥" : "☀️"))).map(x=>`<span>${x}</span>`).join("")}</div>`
              + (w.is_sample ? `<div class="foot"><span class="badge">${t("fc_sample")}</span></div>` : "");
  return `<div class="card"><h3>🌤️ ${t("fc_title")}</h3>${body}</div>`;
}
async function renderResults(res){
  const h = res.field_health || {};
  const hs = t(h.template_id);
  let html = "";
  if(CONFIG.USE_MOCK || res.is_demo) html += `<div style="text-align:center"><span class="badge">${t("mock_badge")}</span></div>`;
  if(hs) html += `<div class="card ${h.light||""}"><h3>${LIGHT_EMOJI[h.light]||""} ${hs}</h3></div>`;
  html += res.options.map(cardHtml).join("");
  html += `<div id="fcBox"></div>`;
  html += `<div class="note">${t(res.disclaimer_id) || t("disclaimer_001")}</div>`;
  html += `<div class="foot">${t("snapshot")}</div>`;
  html += `<button class="big primary" data-act="restart">🏠 ${t("btn_restart")}</button>`;
  $("results").innerHTML = html;
  const w = await getWeather();
  const box = $("fcBox"); if(box) box.innerHTML = fcHtml(w);
}
function waText(o){
  const lines = [];
  lines.push("🌾 AgriShift AI – " + optTitle(o.id));
  lines.push((o.seasons||[]).map(s => (CROP_ICON[s.crop]||"") + " " + t("crop_"+s.crop) + " (" + seasonLabel(s.season) + ")").join("  ➜  "));
  lines.push((LIGHT_EMOJI[o.light]||"") + " " + drops(o.water_drops));
  sentences(o.why_ids).forEach(s => lines.push("• " + s));
  sentences(o.caution_ids).forEach(s => lines.push("⚠️ " + s));
  lines.push("👨‍🌾 " + t("ask_expert"));
  lines.push(t("snapshot"));
  return lines.join("\n");
}

/* ================= EXPERT VIEW ================= */
let xmap = null, xLayer = null;
function xNote(msg){ const n = $("xnote"); n.textContent = msg || ""; n.style.display = msg ? "block" : "none"; }
function initXMap(){
  if(xmap){ setTimeout(()=>xmap.resize(),50); return; }
  if(typeof maplibregl === "undefined"){ $("xmap").innerHTML = '<div class="note err">Map not loaded.</div>'; return; }
  xmap = new maplibregl.Map({container:"xmap", style:baseStyle(), center:[CONFIG.PILOT.lon, CONFIG.PILOT.lat], zoom:10});
  xmap.addControl(new maplibregl.NavigationControl({showCompass:false}));
  xmap.on("error", () => { if(xLayer) xNote("Layer '" + xLayer + "' not available (API/PNG missing)."); });
}
function setLayer(name){
  mark("layer", name);
  if(!xmap) return;
  xNote("");
  if(xmap.getLayer("ov")) xmap.removeLayer("ov");
  if(xmap.getSource("ov")) xmap.removeSource("ov");
  xLayer = null;
  if(name === "none") return;
  xLayer = name;
  const b = CONFIG.LAYER_BOUNDS;
  const add = () => {
    xmap.addSource("ov", {type:"image", url:`${CONFIG.API_BASE}/api/v1/layers/${name}.png`,
      coordinates:[[b.w,b.n],[b.e,b.n],[b.e,b.s],[b.w,b.s]]});
    xmap.addLayer({id:"ov", type:"raster", source:"ov", paint:{"raster-opacity":0.75}});
  };
  if(xmap.isStyleLoaded()) add(); else xmap.once("load", add);
}
async function renderExpert(){
  const r = S.result || (CONFIG.USE_MOCK ? mockAnalyze() : null);
  const w = await getWeather();
  const snap = r && r.data_snapshot ? r.data_snapshot : null;
  let html = `<h3>Data dates</h3>` + (snap
    ? `<p>Satellite window: <b>${snap.satellite_window}</b> · Landsat scene: <b>${snap.landsat_date}</b></p>`
    : `<p>Run an analysis first to load the data snapshot.</p>`);
  html += `<h3>Regional context (not used in scoring)</h3>`;
  if(r && r.regional_context){
    const sm = r.regional_context.soil_moisture, rf = r.regional_context.rainfall;
    html += `<table><tr><th>Item</th><th>Value</th><th>Resolution</th><th>Note</th></tr>`
      + (sm ? `<tr><td>SMAP soil moisture</td><td>${sm.value} ${sm.unit}</td><td>~${sm.resolution_km} km</td><td>${I18N.en[sm.note_id]||""}</td></tr>` : "")
      + (rf ? `<tr><td>GPM IMERG rainfall (Sep)</td><td>${rf.total_mm} mm</td><td>~${rf.resolution_km} km</td><td>${I18N.en[rf.note_id]||""}</td></tr>` : "")
      + `</table>`;
  } else html += `<p>—</p>`;
  html += `<h3>Today's forecast</h3>`;
  if(w && w.available && Array.isArray(w.days)){
    html += (w.is_sample ? `<p><span class="badge">saved sample</span></p>` : "")
      + `<table><tr><th>Date</th><th>Tmax °C</th><th>Rain mm</th></tr>`
      + w.days.map(d=>`<tr><td>${d.date}</td><td>${d.tmax_c}</td><td>${d.rain_mm}</td></tr>`).join("") + `</table>`;
  } else html += `<p>Not available now.</p>`;
  html += `<h3>Sources &amp; limitations</h3><table>
   <tr><th>Source</th><th>Date</th><th>Resolution</th><th>Limitation</th></tr>
   <tr><td>Landsat 8 L2SP (NDVI, NDMI, BSI, surface temp)</td><td>22 Sep 2025</td><td>30 m</td><td>Single-date snapshot; cloud/shadow masked</td></tr>
   <tr><td>SRTM 1 arc-sec (slope, low-lying)</td><td>static</td><td>~30 m</td><td>Old terrain model</td></tr>
   <tr><td>NASA POWER (climate)</td><td>2015–2025 daily</td><td>~0.5°</td><td>Gridded, not a field measurement</td></tr>
   <tr><td>SMAP SPL4SMGP</td><td>1–30 Sep 2025</td><td>~9 km</td><td>Regional only; 1 month, no anomaly; not in score</td></tr>
   <tr><td>GPM IMERG</td><td>1–30 Sep 2025</td><td>~10 km</td><td>Regional only; 1 month; not in score</td></tr>
   <tr><td>Meteomatics</td><td>live</td><td>—</td><td>Not in rotation score</td></tr></table>
   <p>Engine is rule-based (no trained ML). Crop table is <b>unverified</b> until an agronomist confirms. Layers: NDVI / NDMI / BSI / slope overlays come from <code>/api/v1/layers/{name}.png</code>.</p>`;
  $("xinfo").innerHTML = html;
}
function openExpert(){
  show("sx"); $("backBtn").hidden = true; stopAudio();
  initXMap(); renderExpert();
}

/* ================= EVENTS ================= */
document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-act]"); if(!b) return;
  S.touched = true;
  const v = b.dataset.v, act = b.dataset.act;
  switch(act){
    case "lang": S.lang = v; applyI18n(); go("s1"); break;
    case "gps": useGps(); break;
    case "next1": if(S.inArea) go("s2"); break;
    case "crop":
      S.currentCrop = v; buildCropGrid();
      if(SPECIAL[v]){ $("spMsg").textContent = t(SPECIAL[v]); show("sp"); playSeq([SPECIAL[v]]); }
      else go("s3");
      break;
    case "src": S.waterSource = v; mark("src", v); maybe(3); break;
    case "amt": S.waterAmount = v; mark("amt", v); maybe(3); break;
    case "sal": S.salinity = v; mark("sal", v); maybe(4); break;
    case "wl": S.waterlogging = v; mark("wl", v); maybe(4); break;
    case "prio": S.priority = v; mark("prio", v); analyze(); break;
    case "back": { const i = ORDER.indexOf(S.cur); if(i > 0) go(ORDER[i-1]); break; }
    case "replay": if(SCREEN_AUDIO[S.cur]) playSeq(SCREEN_AUDIO[S.cur]); break;
    case "listen": { const o = S.result.options[+b.dataset.i]; playSeq([].concat(o.why_ids||[], o.caution_ids||[])); break; }
    case "wa": { const o = S.result.options[+b.dataset.i]; window.open("https://wa.me/?text=" + encodeURIComponent(waText(o)), "_blank"); break; }
    case "retry": analyze(); break;
    case "restart": restart(); break;
    case "layer": setLayer(v); break;
    case "exitx": location.hash = ""; break;
  }
});
function maybe(step){
  if(step === 3 && S.waterSource && S.waterAmount) setTimeout(()=>go("s4"), 250);
  if(step === 4 && S.salinity && S.waterlogging) setTimeout(()=>go("s5"), 250);
}
function restart(){
  stopAudio();
  Object.assign(S, {currentCrop:null, waterSource:null, waterAmount:null, salinity:null, waterlogging:null, priority:null, result:null});
  ["src","amt","sal","wl","prio"].forEach(a => mark(a, null));
  buildCropGrid();
  go("s1");
}
function route(){
  if(location.hash === "#/expert") openExpert();
  else if(S.cur === "sx") go(S.lang ? "s1" : "s0");
}
window.addEventListener("hashchange", route);

/* ================= INIT ================= */
buildDots(); show("s0"); applyI18n(); route();
</script>
</body>
</html>
~~~

### agrishift/data/api-samples/meteomatics_sample.json

**Bytes:** 339 · **Lines:** 17 · **SHA-256:** 43888d1a957f120cf9eb72a608b37530d15610e8608751392fb973a8618e37df

~~~json
{
  "_note": "PLACEHOLDER SAMPLE (not a real saved Meteomatics response). Replace days[] with a real saved response. Shown only labelled 'saved sample'.",
  "days": [
    {
      "tmax_c": 30.0,
      "rain_mm": 0.0
    },
    {
      "tmax_c": 31.0,
      "rain_mm": 0.0
    },
    {
      "tmax_c": 30.0,
      "rain_mm": 0.0
    }
  ]
}
~~~

### agrishift/data/cache/.gitignore

**Bytes:** 12 · **Lines:** 2 · **SHA-256:** 462bbe804758a6b9458df1763b2810e9ae413e69fe11a593e8776b01d2eff068

~~~text
*
!.gitkeep
~~~

### agrishift/data/features/features.example.json

**Bytes:** 1698 · **Lines:** 73 · **SHA-256:** 2bece8c82f51898cc5410d5787d740b72e343a760320f2f918ba54b14e0c654c

~~~json
{
  "meta": {
    "_WARNING": "EXAMPLE / PLACEHOLDER NUMBERS - NOT REAL SATELLITE DATA. Replace with Member 4's real features.json. Used only when DEMO_MODE=1 and data/features/features.json is absent.",
    "satellite_window": "2025-09-01/2025-09-30",
    "landsat_date": "2025-09-22"
  },
  "points": [
    {
      "id": "example_hyderabad",
      "lat": 25.39,
      "lon": 68.37,
      "features": {
        "ndvi_mean": 0.38,
        "ndmi_mean": 0.12,
        "bsi_mean": 0.05,
        "surface_temp_c": 36.0,
        "cloud_free_fraction": 0.92,
        "elevation_m": 28.0,
        "slope_deg": 0.3,
        "low_lying_flag": false,
        "tmax_mean_by_month": {
          "1": 24.5,
          "2": 27.5,
          "3": 33.0,
          "4": 38.0,
          "5": 40.5,
          "6": 39.5,
          "7": 36.5,
          "8": 34.5,
          "9": 35.5,
          "10": 36.0,
          "11": 31.0,
          "12": 26.0
        },
        "heat_days_40c_by_month": {
          "1": 0,
          "2": 0,
          "3": 1,
          "4": 4,
          "5": 12,
          "6": 10,
          "7": 3,
          "8": 1,
          "9": 3,
          "10": 1,
          "11": 0,
          "12": 0
        },
        "rain_mm_by_month": {
          "1": 4,
          "2": 5,
          "3": 4,
          "4": 3,
          "5": 2,
          "6": 8,
          "7": 60,
          "8": 50,
          "9": 20,
          "10": 2,
          "11": 1,
          "12": 2
        },
        "rh_mean": 50.0,
        "wind_mean": 3.0,
        "smap_surface_mean": 0.21,
        "smap_rootzone_mean": 0.3,
        "gpm_total_mm": 18.2,
        "gpm_rainy_days": 3,
        "gpm_max_daily_mm": 9.0
      }
    }
  ]
}
~~~

### agrishift/data/layers/.gitkeep

**Bytes:** 0 · **Lines:** 0 · **SHA-256:** e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

(Empty file.)

### agrishift/knowledge/crops.csv

**Bytes:** 1834 · **Lines:** 13 · **SHA-256:** a748eb61773a2908611987455f8c5073a830e1fc1ea45cbc6b262b00b5447384

~~~csv
id,name_en,name_ur,name_sd,season,sow_start_m,sow_end_m,duration_min_m,duration_max_m,water_need,heat_tol,salinity_tol,waterlog_tol,family,n_fixing,source,verified,verified_by
cotton,Cotton,کپاس,ڪپهه,kharif,4,6,5,7,high,good,medium,low,fibre,false,MVP plan section 4.3 (starter estimate),false,
rice,Rice,چاول,چانور,kharif,6,7,4,5,very_high,medium,low_medium,good,cereal,false,MVP plan section 4.3 (starter estimate),false,
mung_bean,Mung bean,مونگ,مُنگ,kharif,7,7,2,3,low,good,low,low,legume,true,MVP plan section 4.3 (starter estimate),false,
sorghum,Sorghum,جوار,جوار,kharif,6,7,3,4,low_medium,good,medium,medium,cereal,false,MVP plan section 4.3 (starter estimate),false,
millet,Millet,باجرہ,ٻاجهري,kharif,6,7,3,3,low,good,medium,low,cereal,false,MVP plan section 4.3 (starter estimate),false,
sesame,Sesame,تل,ٽل,kharif,6,7,3,4,low,good,low_medium,low,oilseed,false,MVP plan section 4.3 (starter estimate),false,
maize,Maize,مکئی,مڪئي,kharif,7,8,3,4,medium_high,medium,low,low,cereal,false,MVP plan section 4.3 (starter estimate; Jul-Aug sowing only),false,
sunflower,Sunflower,سورج مکھی,سج مکي,kharif,7,8,3,4,medium,medium,medium,low,oilseed,false,MVP plan section 4.3 (starter estimate; Jul-Aug sowing only),false,
wheat,Wheat,گندم,ڪڻڪ,rabi,11,12,4,5,medium,low,medium,low,cereal,false,MVP plan section 4.3 (starter estimate),false,
chickpea,Chickpea,چنا,چڻا,rabi,10,11,4,5,very_low,low,low,very_low,legume,true,MVP plan section 4.3 (starter estimate),false,
mustard,Mustard,سرسوں,سرنهن,rabi,10,11,4,5,low_medium,low,medium,low,oilseed,false,MVP plan section 4.3 (starter estimate),false,
berseem,Berseem,برسیم,برسيم,rabi,10,11,5,6,medium_high,low_medium,medium,low,legume,true,MVP plan section 4.3 (starter estimate),false,
~~~

### agrishift/services/rotation-engine/rotation_engine/__init__.py

**Bytes:** 151 · **Lines:** 4 · **SHA-256:** 604f13eff7c237eb28ea6be2baf08d3fec6c2f893b10f2cb169f9d02998deeb0

~~~python
from .crops import Crop, load_crops
from .engine import recommend, upcoming_seasons

__all__ = ["Crop", "load_crops", "recommend", "upcoming_seasons"]
~~~

### agrishift/services/rotation-engine/rotation_engine/crops.py

**Bytes:** 3810 · **Lines:** 96 · **SHA-256:** 6f3d13798659910aa349fce38a70c6bc88365fd261e6a0b80f3f64db248b2c8e

~~~python
"""Crop table loader (knowledge/crops.csv). Pure Python, no dependencies."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from typing import Dict

# Ordinal scales. The CSV keeps human-readable words; the engine uses these numbers.
WATER_LEVELS = {"very_low": 1, "low": 2, "low_medium": 3, "medium": 4,
                "medium_high": 5, "high": 6, "very_high": 7}
TOL_LEVELS = {"very_low": 1, "low": 2, "low_medium": 3, "medium": 4, "good": 5}
SEASONS = ("rabi", "kharif")


@dataclass(frozen=True)
class Crop:
    id: str
    name_en: str
    name_ur: str
    name_sd: str
    season: str
    sow_start: int          # calendar month 1-12
    sow_end: int            # calendar month 1-12
    dur_min: int            # months
    dur_max: int            # months
    water_need: int         # 1..7
    heat_tol: int           # 1..5
    salinity_tol: int       # 1..5
    waterlog_tol: int       # 1..5
    family: str
    n_fixing: bool
    source: str
    verified: bool
    verified_by: str


def _level(table: Dict[str, int], value: str, field: str, crop_id: str) -> int:
    key = (value or "").strip().lower()
    if key not in table:
        raise ValueError(f"crops.csv: crop '{crop_id}' has invalid {field} '{value}'")
    return table[key]


def _bool(value: str, field: str, crop_id: str) -> bool:
    v = (value or "").strip().lower()
    if v not in ("true", "false"):
        raise ValueError(f"crops.csv: crop '{crop_id}' has invalid {field} '{value}'")
    return v == "true"


def _month(value: str, field: str, crop_id: str) -> int:
    m = int(value)
    if not 1 <= m <= 12:
        raise ValueError(f"crops.csv: crop '{crop_id}' {field} must be 1-12")
    return m


def load_crops(path: str) -> Dict[str, Crop]:
    """Load crops in file order. Raises ValueError on any invalid row (fail loudly)."""
    crops: Dict[str, Crop] = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cid = row["id"].strip()
            if not cid:
                raise ValueError("crops.csv: empty crop id")
            if cid in crops:
                raise ValueError(f"crops.csv: duplicate crop id '{cid}'")
            season = row["season"].strip().lower()
            if season not in SEASONS:
                raise ValueError(f"crops.csv: crop '{cid}' has invalid season '{season}'")
            c = Crop(
                id=cid,
                name_en=row["name_en"].strip(),
                name_ur=row["name_ur"].strip(),
                name_sd=row["name_sd"].strip(),
                season=season,
                sow_start=_month(row["sow_start_m"], "sow_start_m", cid),
                sow_end=_month(row["sow_end_m"], "sow_end_m", cid),
                dur_min=int(row["duration_min_m"]),
                dur_max=int(row["duration_max_m"]),
                water_need=_level(WATER_LEVELS, row["water_need"], "water_need", cid),
                heat_tol=_level(TOL_LEVELS, row["heat_tol"], "heat_tol", cid),
                salinity_tol=_level(TOL_LEVELS, row["salinity_tol"], "salinity_tol", cid),
                waterlog_tol=_level(TOL_LEVELS, row["waterlog_tol"], "waterlog_tol", cid),
                family=row["family"].strip().lower(),
                n_fixing=_bool(row["n_fixing"], "n_fixing", cid),
                source=row["source"].strip(),
                verified=_bool(row["verified"], "verified", cid),
                verified_by=row.get("verified_by", "").strip(),
            )
            if c.sow_start > c.sow_end or c.dur_min > c.dur_max or c.dur_min < 1:
                raise ValueError(f"crops.csv: crop '{cid}' has inconsistent sowing/duration values")
            crops[cid] = c
    if not crops:
        raise ValueError("crops.csv is empty")
    return crops
~~~

### agrishift/services/rotation-engine/rotation_engine/engine.py

**Bytes:** 14562 · **Lines:** 365 · **SHA-256:** beba9eb573b05901baeabec098270f7346f7ba8c5073ca2439d21cebd98e858b

~~~python
"""Rule-based rotation engine (MVP, NO machine learning).

Plan reference: section 5. Everything here is explainable rules. All numeric
thresholds below are STARTING POINTS (unverified) and must be reviewed by an
agronomist before being treated as final.

Scoring (0-100):
    score = 100 * (w1*paani_fit + w2*zameen_fit + w3*mausam_fit + w4*rotation_faida) - penalties
Heat (POWER) is expressed through mausam_fit; penalties are: late sowing, same family twice.
SMAP / GPM / Meteomatics are NOT used in scoring.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

from .crops import Crop

# ---------------------------------------------------------------- configuration
WEIGHTS = {  # (paani, zameen, mausam, rotation_faida) - plan section 5.4
    "save_water": (0.45, 0.15, 0.20, 0.20),
    "improve_soil": (0.15, 0.35, 0.15, 0.35),
    "balanced": (0.30, 0.25, 0.20, 0.25),
    # third card when the farmer chose "balanced": average of save_water and improve_soil
    "save_water_soil": (0.30, 0.25, 0.175, 0.275),
}
AVAIL_LEVEL = {"low": 3, "medium": 5, "high": 7}   # water the farmer has, same 1..7 scale as crop need
RAIN_FED_LEVEL_DROP = 1                             # rain-fed water is less reliable
NDVI_WEAK = 0.30                                    # unverified
NDVI_GOOD = 0.50                                    # unverified
HEAT_DAYS_FULL_RISK = 15.0                          # heat days (>=40C) in crop months that mean "full" risk; unverified
HEAT_TOL_SCALE = {1: 0.0, 2: 0.2, 3: 0.4, 4: 0.6, 5: 1.0}
HEAT_CAUTION_LEVEL = 0.30
PENALTY_LATE_SOWING = 4.0
PENALTY_SAME_FAMILY = 3.0
GREEN_MIN_SCORE = 70
TOTAL_SOURCES = 6                                   # landsat, srtm, power, smap, gpm, forecast
PARTNER = {"rabi": "wheat", "kharif": "cotton"}     # customary crop in the other season (for the "your way" card)

RULE_CAUTION = {
    "repeat": "caution_rule_repeat_001",
    "water": "caution_rule_water_001",
    "salinity": "caution_rule_salt_001",
    "waterlog": "caution_rule_waterlog_001",
    "overlap": "caution_rule_overlap_001",
}


# ---------------------------------------------------------------- seasons
def upcoming_seasons(today: date) -> List[Tuple[str, str]]:
    """Next two growing seasons as [(type, code), (type, code)].

    Sep-Dec -> rabi (this year/next) then kharif (next year)
    Jan-Aug -> kharif (this year) then rabi (this year/next)
    """
    y = today.year
    if today.month >= 9:
        return [("rabi", f"rabi_{y}_{(y + 1) % 100:02d}"), ("kharif", f"kharif_{y + 1}")]
    return [("kharif", f"kharif_{y}"), ("rabi", f"rabi_{y}_{(y + 1) % 100:02d}")]


# ---------------------------------------------------------------- context
@dataclass
class Ctx:
    crops: Dict[str, Crop]
    current: Crop
    water_source: str
    water_amount: str
    salinity: str
    waterlogging: str
    priority: str
    low_lying: bool
    ndvi: float
    heat_days: Dict[int, float]
    sources_present: int
    slots: List[Tuple[str, str]] = field(default_factory=list)

    @property
    def weak(self) -> bool:
        return self.ndvi < NDVI_WEAK

    @property
    def avail(self) -> int:
        a = AVAIL_LEVEL[self.water_amount]
        if self.water_source == "rain":
            a = max(1, a - RAIN_FED_LEVEL_DROP)
        return a


# ---------------------------------------------------------------- timing helpers
def _sow_window(c: Crop, first: Optional[Crop]) -> Tuple[int, int]:
    """Sowing window on one continuous month axis. The second crop is shifted by 12 if it falls in the next calendar year."""
    if first is None:
        return c.sow_start, c.sow_end
    shift = 12 if c.sow_start <= first.sow_end else 0
    return c.sow_start + shift, c.sow_end + shift


def _heat_risk(c: Crop, ctx: Ctx) -> float:
    months = [((c.sow_start - 1 + i) % 12) + 1 for i in range(c.dur_min)]
    days = sum(ctx.heat_days.get(m, 0.0) for m in months)
    return min(1.0, days / HEAT_DAYS_FULL_RISK)


def _heat_exposure(c: Crop, ctx: Ctx) -> float:
    """risk * (1 - tolerance scale): 0 = no problem, 1 = worst."""
    return _heat_risk(c, ctx) * (1.0 - HEAT_TOL_SCALE[c.heat_tol])


# ---------------------------------------------------------------- hard rules (section 5.2)
def hard_violations(c1: Crop, c2: Crop, ctx: Ctx) -> List[str]:
    v: List[str] = []
    if c1.season != ctx.slots[0][0] or c2.season != ctx.slots[1][0]:
        v.append("season")
    if c1.id == c2.id or c1.id == ctx.current.id:
        v.append("repeat")
    if any(c.water_need > ctx.avail + 1 for c in (c1, c2)):
        v.append("water")
    if ctx.salinity == "yes" and any(c.salinity_tol <= 2 for c in (c1, c2)):
        v.append("salinity")
    if (ctx.waterlogging == "yes" or ctx.low_lying) and any(c.waterlog_tol <= 2 for c in (c1, c2)):
        v.append("waterlog")
    earliest_harvest = c1.sow_start + c1.dur_min
    _, second_sow_end = _sow_window(c2, c1)
    if earliest_harvest > second_sow_end:
        v.append("overlap")
    return v


# ---------------------------------------------------------------- scoring (section 5.4)
def _paani_fit(c: Crop, ctx: Ctx) -> float:
    if c.water_need <= ctx.avail:
        avail_fit = 1.0
    elif c.water_need == ctx.avail + 1:
        avail_fit = 0.5
    else:
        avail_fit = 0.0
    thrift = 1.0 - (c.water_need - 1) / 6.0
    return 0.5 * avail_fit + 0.5 * thrift


def _tol_fit(tol: int) -> float:
    return (tol - 1) / 4.0


def _zameen_fit(c: Crop, ctx: Ctx) -> float:
    if ctx.salinity == "yes":
        sal = _tol_fit(c.salinity_tol)
    elif ctx.salinity == "no":
        sal = 1.0
    else:
        sal = 0.5 + 0.5 * _tol_fit(c.salinity_tol)
    if ctx.waterlogging == "yes" or ctx.low_lying:
        wl = _tol_fit(c.waterlog_tol)
    elif ctx.waterlogging == "no":
        wl = 1.0
    else:
        wl = 0.5 + 0.5 * _tol_fit(c.waterlog_tol)
    fit = (sal + wl) / 2.0
    if ctx.weak and c.n_fixing:          # weak field -> soil-health crops get a bonus
        fit = min(1.0, fit + 0.10)
    return fit


def _mausam_fit(c: Crop, ctx: Ctx) -> float:
    return 1.0 - _heat_exposure(c, ctx)


def _rotation_faida(c: Crop, prev: Crop) -> float:
    if c.n_fixing and prev.family != "legume":
        return 1.0                        # nitrogen-fixing crop after a non-legume
    if c.family == prev.family:
        return 0.4
    return 0.7


def _mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs)


def score_sequence(c1: Crop, c2: Crop, ctx: Ctx, wkey: str) -> Tuple[float, bool]:
    """Returns (score 0..100, late_sowing_flag)."""
    w1, w2, w3, w4 = WEIGHTS[wkey]
    paani = _mean(_paani_fit(c, ctx) for c in (c1, c2))
    zameen = _mean(_zameen_fit(c, ctx) for c in (c1, c2))
    mausam = _mean(_mausam_fit(c, ctx) for c in (c1, c2))
    rot = _mean([_rotation_faida(c1, ctx.current), _rotation_faida(c2, c1)])
    penalties = 0.0
    for c, prev in ((c1, ctx.current), (c2, c1)):
        if c.family == prev.family:
            penalties += PENALTY_SAME_FAMILY
    latest_harvest = c1.sow_end + c1.dur_max
    second_sow_start, _ = _sow_window(c2, c1)
    late = latest_harvest > second_sow_start
    if late:
        penalties += PENALTY_LATE_SOWING
    total = 100.0 * (w1 * paani + w2 * zameen + w3 * mausam + w4 * rot) - penalties
    return max(0.0, min(100.0, total)), late


# ---------------------------------------------------------------- confidence (section 5.5)
def confidence_dots(ctx: Ctx) -> int:
    missing = TOTAL_SOURCES - ctx.sources_present
    dots = 3
    if missing >= 3:
        dots -= 2
    elif missing >= 1:
        dots -= 1
    unknown = sum(1 for x in (ctx.salinity, ctx.waterlogging) if x == "unknown")
    if unknown >= 2:
        dots -= 1
    return max(1, min(3, dots))


# ---------------------------------------------------------------- explanation templates (section 5.6)
def _explain(c1: Crop, c2: Crop, ctx: Ctx, violations: List[str], late: bool,
             is_existing: bool) -> Tuple[List[str], List[str]]:
    crops = (c1, c2)
    water_ok = all(c.water_need <= ctx.avail for c in crops)
    max_need = max(c.water_need for c in crops)
    legume = any(c.n_fixing and prev.family != "legume" for c, prev in ((c1, ctx.current), (c2, c1)))
    exposed = [c for c in crops if _heat_risk(c, ctx) >= HEAT_CAUTION_LEVEL]
    heat_ok = bool(exposed) and all(c.heat_tol == 5 for c in exposed)
    facts = {
        "why_known_crop_002": ctx.current.id in (c1.id, c2.id),
        "why_water_ok_001": water_ok,
        "why_water_save_001": max_need <= 3,
        "why_legume_001": legume,
        "why_soil_help_001": legume and ctx.weak,
        "why_heat_ok_001": heat_ok,
    }
    order_existing = ["why_known_crop_002", "why_water_ok_001", "why_heat_ok_001"]
    order_other = ["why_water_save_001", "why_legume_001", "why_soil_help_001", "why_heat_ok_001", "why_water_ok_001"]
    order = order_existing if is_existing else order_other
    if violations:
        order = ["why_known_crop_002"]   # a red card only states that this is what the farmer does
    why = [k for k in order if facts[k]][:2]

    cautions: List[str] = []
    for rule in violations:
        cid = RULE_CAUTION.get(rule)
        if cid:
            cautions.append(cid)
    if not violations:
        if ctx.waterlogging == "unknown" and any(c.waterlog_tol <= 2 for c in crops):
            cautions.append("caution_waterlog_001")
        if late:
            cautions.append("caution_late_sowing_001")
        if any(_heat_exposure(c, ctx) >= HEAT_CAUTION_LEVEL for c in crops):
            cautions.append("caution_heat_001")
    cap = 2 if violations else 1
    return why, cautions[:cap]


# ---------------------------------------------------------------- option builder
def _option(opt_id: str, c1: Crop, c2: Crop, ctx: Ctx, wkey: str, dots: int, is_existing: bool) -> dict:
    violations = hard_violations(c1, c2, ctx)
    score, late = score_sequence(c1, c2, ctx, wkey)
    if violations:
        light = "red"
    else:
        light = "green" if score >= GREEN_MIN_SCORE else "yellow"
    need = max(c1.water_need, c2.water_need)
    drops = 1 if need <= 3 else (2 if need <= 5 else 3)
    why, cautions = _explain(c1, c2, ctx, violations, late, is_existing)
    verified = c1.verified and c2.verified
    return {
        "id": opt_id,
        "seasons": [
            {"season": ctx.slots[0][1], "crop": c1.id},
            {"season": ctx.slots[1][1], "crop": c2.id},
        ],
        "light": light,
        "water_drops": drops,
        "score": int(round(score)),
        "confidence_dots": dots,
        "why_ids": why,
        "caution_ids": cautions,
        "expert_needed": (not verified) or dots <= 1 or light == "red",
        "crop_verified": verified,
    }


def _field_health(ndvi: float) -> dict:
    if ndvi >= NDVI_GOOD:
        return {"light": "green", "template_id": "health_good_001"}
    if ndvi >= NDVI_WEAK:
        return {"light": "yellow", "template_id": "health_moderate_001"}
    return {"light": "red", "template_id": "health_poor_001"}


# ---------------------------------------------------------------- public entry point
def recommend(crops: Dict[str, Crop], request: dict, features: dict, today: Optional[date] = None) -> dict:
    """Build the 3 options.

    request keys: current_crop, water_source, water_amount, salinity, waterlogging, priority
    features keys (all REQUIRED, caller must check first):
        ndvi_mean (float), low_lying_flag (bool), heat_days_40c_by_month ({1..12: float}),
        sources_present (int, 0..6)
    Returns {"status": "ok", "field_health":..., "options": [...]} or
            {"status": "insufficient_data", "reason_id": ..., "field_health":...}
    """
    today = today or date.today()
    current = crops.get(request["current_crop"])
    if current is None:
        raise ValueError(f"unknown current_crop '{request['current_crop']}'")

    ndvi = features.get("ndvi_mean")
    low_lying = features.get("low_lying_flag")
    heat_days = features.get("heat_days_40c_by_month")
    if not isinstance(ndvi, (int, float)) or isinstance(low_lying, bool) is False \
            or not isinstance(heat_days, dict) or set(heat_days) != set(range(1, 13)):
        raise ValueError("features missing or malformed (ndvi_mean, low_lying_flag, heat_days_40c_by_month)")

    ctx = Ctx(
        crops=crops, current=current,
        water_source=request["water_source"], water_amount=request["water_amount"],
        salinity=request["salinity"], waterlogging=request["waterlogging"],
        priority=request["priority"],
        low_lying=bool(low_lying), ndvi=float(ndvi), heat_days={int(k): float(v) for k, v in heat_days.items()},
        sources_present=int(features.get("sources_present", 0)),
        slots=upcoming_seasons(today),
    )
    health = _field_health(ctx.ndvi)
    dots = confidence_dots(ctx)

    firsts = [c for c in crops.values() if c.season == ctx.slots[0][0]]
    seconds = [c for c in crops.values() if c.season == ctx.slots[1][0]]

    # --- card 1: the farmer's own way (may be red = warning, never a recommendation)
    def slot_crop(slot_type: str) -> Crop:
        if current.season == slot_type:
            return current
        return crops[PARTNER[slot_type]]
    existing_pair = (slot_crop(ctx.slots[0][0]), slot_crop(ctx.slots[1][0]))

    # --- all rule-valid sequences
    valid = [(a, b) for a in firsts for b in seconds if not hard_violations(a, b, ctx)]

    def ranked(wkey: str, exclude: set):
        pool = [p for p in valid if (p[0].id, p[1].id) not in exclude]
        return sorted(pool, key=lambda p: (-score_sequence(p[0], p[1], ctx, wkey)[0], p[0].id, p[1].id))

    if not valid:
        return {"status": "insufficient_data", "reason_id": "no_safe_option_001", "field_health": health}

    options = []
    used = {(existing_pair[0].id, existing_pair[1].id)}
    options.append(_option("existing", existing_pair[0], existing_pair[1], ctx, ctx.priority, dots, True))

    bal = ranked("balanced", used)
    if bal:
        p = bal[0]
        options.append(_option("balanced", p[0], p[1], ctx, "balanced", dots, False))
        used.add((p[0].id, p[1].id))

    third_key = ctx.priority if ctx.priority != "balanced" else "save_water_soil"
    third = ranked(third_key, used)
    if third:
        p = third[0]
        options.append(_option("priority", p[0], p[1], ctx, third_key, dots, False))

    return {"status": "ok", "field_health": health, "options": options}
~~~

### agrishift/services/rotation-engine/tests/test_engine.py

**Bytes:** 9915 · **Lines:** 237 · **SHA-256:** e61da611ee449f2e7b15e0ff1a6256c36affe13f57b3e166828ecc9f0ceddabb

~~~python
import os
import sys
from datetime import date

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from rotation_engine import load_crops, recommend, upcoming_seasons  # noqa: E402
from rotation_engine import engine as eng  # noqa: E402

CSV = os.path.join(HERE, "..", "..", "..", "knowledge", "crops.csv")
CROPS = load_crops(CSV)
NOV = date(2026, 11, 15)

HEAT = {m: 0.0 for m in range(1, 13)}
HEAT.update({4: 4.0, 5: 12.0, 6: 10.0, 7: 3.0, 8: 1.0, 9: 3.0})


def feats(**kw):
    f = {"ndvi_mean": 0.55, "low_lying_flag": False, "heat_days_40c_by_month": dict(HEAT), "sources_present": 6}
    f.update(kw)
    return f


def req(**kw):
    r = {"current_crop": "cotton", "water_source": "canal", "water_amount": "medium",
         "salinity": "no", "waterlogging": "no", "priority": "balanced"}
    r.update(kw)
    return r


def seq(o):
    return tuple(s["crop"] for s in o["seasons"])


def test_crops_table_loads():
    assert len(CROPS) == 12
    assert all(not c.verified for c in CROPS.values())      # nothing verified yet
    assert CROPS["wheat"].season == "rabi" and CROPS["cotton"].season == "kharif"


def test_upcoming_seasons():
    assert upcoming_seasons(date(2026, 11, 15)) == [("rabi", "rabi_2026_27"), ("kharif", "kharif_2027")]
    assert upcoming_seasons(date(2027, 3, 1)) == [("kharif", "kharif_2027"), ("rabi", "rabi_2027_28")]
    assert upcoming_seasons(date(2026, 12, 31))[0][1] == "rabi_2026_27"


def test_three_distinct_options_in_order():
    out = recommend(CROPS, req(), feats(), NOV)
    assert out["status"] == "ok"
    ids = [o["id"] for o in out["options"]]
    assert ids == ["existing", "balanced", "priority"]
    assert len({seq(o) for o in out["options"]}) == 3


def test_existing_option_is_farmers_way():
    out = recommend(CROPS, req(current_crop="cotton"), feats(), NOV)
    ex = out["options"][0]
    assert seq(ex) == ("wheat", "cotton")
    assert [s["season"] for s in ex["seasons"]] == ["rabi_2026_27", "kharif_2027"]


def test_recommended_options_never_violate_hard_rules():
    out = recommend(CROPS, req(), feats(), NOV)
    ctx_req = req()
    for o in out["options"][1:]:
        assert o["light"] in ("green", "yellow")


def test_wheat_after_wheat_is_rejected_red_warning():
    out = recommend(CROPS, req(current_crop="wheat"), feats(), NOV)
    ex = out["options"][0]
    assert seq(ex)[0] == "wheat"
    assert ex["light"] == "red"
    assert "caution_rule_repeat_001" in ex["caution_ids"]
    for o in out["options"][1:]:
        assert seq(o)[0] != "wheat"


def test_low_water_rejects_thirsty_crops():
    out = recommend(CROPS, req(water_amount="low", water_source="canal"), feats(), NOV)
    for o in out["options"][1:]:
        for crop in seq(o):
            assert CROPS[crop].water_need <= 4    # avail 3 -> need must be <= 4


def test_rain_fed_is_more_restrictive_than_canal():
    canal = recommend(CROPS, req(water_amount="low", water_source="canal"), feats(), NOV)
    rain = recommend(CROPS, req(water_amount="low", water_source="rain"), feats(), NOV)
    for o in rain["options"][1:]:
        for crop in seq(o):
            assert CROPS[crop].water_need <= 3
    assert canal["status"] == "ok"


def test_salinity_yes_rejects_low_tolerance():
    out = recommend(CROPS, req(salinity="yes"), feats(), NOV)
    for o in out["options"][1:]:
        for crop in seq(o):
            assert CROPS[crop].salinity_tol >= 3


def test_waterlogging_or_low_lying_rejects_low_tolerance():
    for out in (recommend(CROPS, req(waterlogging="yes"), feats(), NOV),
                recommend(CROPS, req(), feats(low_lying_flag=True), NOV)):
        if out["status"] == "ok":
            for o in out["options"][1:]:
                for crop in seq(o):
                    assert CROPS[crop].waterlog_tol >= 3


def test_waterlogging_can_leave_no_safe_option():
    # every rabi crop except none has waterlog tolerance >=3 -> no valid sequence
    out = recommend(CROPS, req(waterlogging="yes"), feats(), NOV)
    assert out["status"] == "insufficient_data"
    assert out["reason_id"] == "no_safe_option_001"
    assert "options" not in out


def test_overlap_rule():
    ctx = eng.Ctx(crops=CROPS, current=CROPS["cotton"], water_source="canal", water_amount="high",
                  salinity="no", waterlogging="no", priority="balanced", low_lying=False, ndvi=0.5,
                  heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    # berseem (sow Oct-Nov, 5-6 months) then mung (Jul) is fine; fabricate an impossible one:
    fake = CROPS["wheat"].__class__(**{**CROPS["wheat"].__dict__, "id": "slow", "dur_min": 9, "dur_max": 9})
    assert "overlap" in eng.hard_violations(fake, CROPS["mung_bean"], ctx)
    assert "overlap" not in eng.hard_violations(CROPS["wheat"], CROPS["mung_bean"], ctx)


def test_season_mismatch_rule():
    ctx = eng.Ctx(crops=CROPS, current=CROPS["cotton"], water_source="canal", water_amount="high",
                  salinity="no", waterlogging="no", priority="balanced", low_lying=False, ndvi=0.5,
                  heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    assert "season" in eng.hard_violations(CROPS["cotton"], CROPS["wheat"], ctx)


def test_priority_changes_ranking():
    water = recommend(CROPS, req(priority="save_water", water_amount="high"), feats(), NOV)["options"][2]
    soil = recommend(CROPS, req(priority="improve_soil", water_amount="high"), feats(), NOV)["options"][2]
    wsum = lambda o: sum(CROPS[c].water_need for c in seq(o))
    assert wsum(water) <= wsum(soil)
    assert seq(water) != seq(soil) or water["score"] != soil["score"]


def test_save_water_priority_prefers_light_crops():
    out = recommend(CROPS, req(priority="save_water", water_amount="high"), feats(), NOV)
    assert out["options"][2]["water_drops"] == 1


def test_legume_gets_bonus_and_reason():
    out = recommend(CROPS, req(priority="improve_soil", water_amount="high"), feats(), NOV)
    opt = out["options"][2]
    assert any(CROPS[c].n_fixing for c in seq(opt))
    assert "why_legume_001" in opt["why_ids"]


def test_rice_then_wheat_is_not_rejected():
    ctx = eng.Ctx(crops=CROPS, current=CROPS["rice"], water_source="canal", water_amount="high",
                  salinity="no", waterlogging="no", priority="balanced", low_lying=False, ndvi=0.5,
                  heat_days=dict(HEAT), sources_present=6, slots=upcoming_seasons(NOV))
    assert eng.hard_violations(CROPS["wheat"], CROPS["rice"], ctx) == []   # wheat -> rice allowed
    # rice (kharif) -> wheat (rabi) in a kharif-first window
    ctx2 = eng.Ctx(**{**ctx.__dict__, "current": CROPS["cotton"], "slots": upcoming_seasons(date(2027, 5, 1))})
    assert eng.hard_violations(CROPS["rice"], CROPS["wheat"], ctx2) == []


def test_weak_field_flags_expert_and_boosts_legume():
    weak = recommend(CROPS, req(), feats(ndvi_mean=0.2), NOV)
    assert weak["field_health"] == {"light": "red", "template_id": "health_poor_001"}
    good = recommend(CROPS, req(), feats(ndvi_mean=0.6), NOV)
    assert good["field_health"]["light"] == "green"
    ok = recommend(CROPS, req(), feats(ndvi_mean=0.4), NOV)
    assert ok["field_health"]["template_id"] == "health_moderate_001"


def test_confidence_dots_rules():
    base = recommend(CROPS, req(), feats(sources_present=6), NOV)["options"][1]["confidence_dots"]
    assert base == 3
    assert recommend(CROPS, req(), feats(sources_present=5), NOV)["options"][1]["confidence_dots"] == 2
    assert recommend(CROPS, req(), feats(sources_present=3), NOV)["options"][1]["confidence_dots"] == 1
    both_unknown = recommend(CROPS, req(salinity="unknown", waterlogging="unknown"),
                             feats(sources_present=6), NOV)["options"][1]["confidence_dots"]
    assert both_unknown == 2


def test_unverified_crops_always_need_expert():
    out = recommend(CROPS, req(), feats(), NOV)
    for o in out["options"]:
        assert o["crop_verified"] is False
        assert o["expert_needed"] is True


def test_heat_exposure_lowers_heat_sensitive_crops():
    hot = dict(HEAT)
    hot.update({3: 20.0, 4: 25.0, 5: 28.0})       # very hot spring
    cool = {m: 0.0 for m in range(1, 13)}
    a = recommend(CROPS, req(priority="balanced"), feats(heat_days_40c_by_month=hot), NOV)
    b = recommend(CROPS, req(priority="balanced"), feats(heat_days_40c_by_month=cool), NOV)
    ea = [o for o in a["options"] if o["id"] == "existing"][0]
    eb = [o for o in b["options"] if o["id"] == "existing"][0]
    assert ea["score"] <= eb["score"]


def test_why_and_caution_limits_and_shape():
    out = recommend(CROPS, req(salinity="unknown", waterlogging="unknown"), feats(), NOV)
    for o in out["options"]:
        assert len(o["why_ids"]) <= 2
        assert len(o["caution_ids"]) <= (2 if o["light"] == "red" else 1)
        assert 1 <= o["water_drops"] <= 3 and 0 <= o["score"] <= 100
        assert o["confidence_dots"] in (1, 2, 3)
        assert set(o) == {"id", "seasons", "light", "water_drops", "score", "confidence_dots",
                          "why_ids", "caution_ids", "expert_needed", "crop_verified"}


def test_deterministic():
    a = recommend(CROPS, req(), feats(), NOV)
    b = recommend(CROPS, req(), feats(), NOV)
    assert a == b


def test_kharif_first_window():
    out = recommend(CROPS, req(current_crop="wheat"), feats(), date(2027, 4, 1))
    assert out["status"] == "ok"
    for o in out["options"]:
        assert [s["season"] for s in o["seasons"]] == ["kharif_2027", "rabi_2027_28"]


def test_bad_inputs_raise():
    with pytest.raises(ValueError):
        recommend(CROPS, req(current_crop="nope"), feats(), NOV)
    with pytest.raises(ValueError):
        recommend(CROPS, req(), {"ndvi_mean": 0.5}, NOV)
    bad = dict(HEAT)
    del bad[3]
    with pytest.raises(ValueError):
        recommend(CROPS, req(), feats(heat_days_40c_by_month=bad), NOV)
~~~

## Integration boundary with the current repository

This document is an archive reference only. The current repository’s locked MVP remains SMAP, GPM IMERG, Landsat 8/9 C2 L2, SRTM/NASADEM, NASA POWER and Meteomatics. Before integrating any archived implementation, review API contracts, data provenance, dependencies, CORS/security settings, sample authenticity, crop verification status, and which archived behavior belongs in the current six-source design. Do not copy placeholder environmental values or unverified crop data into active catalogs/features.
