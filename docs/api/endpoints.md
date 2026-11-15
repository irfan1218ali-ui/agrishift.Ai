# Proposed API groups

| Group | Responsibility |
|---|---|
| `/auth`, `/users` | Identity, sessions, profile and consent |
| `/farms`, `/fields`, `/boundaries` | Tenant-scoped farm and geometry management |
| `/datasets`, `/providers` | Catalog, coverage, provider health and terms |
| `/environment`, `/weather`, `/imagery` | Normalized observations, forecasts, imagery metadata |
| `/map-layers` | Layer contract, legends, resolution, attribution, availability |
| `/processing-jobs` | Async job submission/status/cancel |
| `/models`, `/predictions` | Model metadata/version and inference requests/results |
| `/crops`, `/rotations`, `/scenarios` | Verified knowledge and rotation alternatives |
| `/reports`, `/feedback` | Evidence reports and reviewed feedback |
| `/admin` | Restricted catalog/operations workflows |
| `/health`, `/ready` | Liveness and dependency readiness |

Groups are proposals. Define authorization scopes and tenant ownership before implementation; admin paths need stronger controls. Long processing is asynchronous. Health must not expose credentials or internal topology.
