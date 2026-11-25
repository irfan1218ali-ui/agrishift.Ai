# SQLite data dictionary

The active SQLAlchemy Core table definitions are in `apps/api/app/db.py`. Initialization and migrations are additive: existing farmer analyses remain in place. The local SQLite database is ignored by Git and excluded from release ZIPs.

| Table | Key columns | Purpose |
|---|---|---|
| `analysis_requests` | `id`, location, crop history, water/soil inputs, priority, language, `created_at` | Farmer-submitted analysis inputs |
| `analysis_results` | `id`, `request_id`, nearest feature point, cluster, result JSON, confidence, status | Persisted public analysis response |
| `dataset_metadata` | provider, product, version, period, resolution, validation, checksum | Dataset provenance |
| `model_runs` | model name/version, metrics, artifact path/checksum | Existing K-Means run provenance |
| `expert_users` | `id`, unique email, password hash, fixed `EXPERT` role, active state, login/audit timestamps | The single configured expert account |
| `expert_reviews` | analysis/expert foreign keys, decision, comments, suggested rotation, soil-test flag, `reviewed_at`, audit timestamps | Expert review history |
| `expert_notes` | analysis/expert foreign keys, content, audit timestamps | Per-analysis server-side expert notes |
| `analysis_review_status` | analysis primary key, current status, latest review/user, `reviewed_at`, audit timestamps | Farmer-visible review state and dashboard filters |
| `rotation_score_components` | analysis/option/component, value, reason, rule ID, verification flag, source | Persisted eleven-factor score breakdown |

Review status is `not_reviewed`, `under_review`, or one of the four final decisions. The database stores only the password hash, never the plaintext password. Farmer analysis remains guest-accessible; the Expert Portal has no additional roles.
