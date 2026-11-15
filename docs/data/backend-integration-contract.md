# AgriShift AI — Backend Integration Contract (Step 2A -> Step 1 Integration)

## 1. Overview & Parallel Work Hand-off

This contract defines the exact interface, file schemas, serialization formats, and integration instructions for the primary backend agent (**Codex**) to integrate Step 2A data engineering and unsupervised ML deliverables into the stabilized AgriShift AI FastAPI application.

> [!IMPORTANT]
> Step 2A strictly respected ownership boundaries. No backend (`apps/api/`), frontend (`apps/web/`), or rotation engine files were modified. All data assets, map overlays, ML artifacts, and schemas described below are validated, fully calculated, and ready for clean integration.

---

## 2. Deliverable File Manifest & Locations

| Deliverable | Path | Format | Status |
| :--- | :--- | :--- | :--- |
| **Real Feature Catalog** | `data/features/features.json` | JSON | Validated (149 spatial points) |
| **Pilot Feature Table** | `data/processed/features/pilot_feature_table.csv` | CSV | Validated tabular observations |
| **Map Overlays** | `data/layers/*.png` (`ndvi`, `ndmi`, `bsi`, `slope`) | RGBA PNG | Generated with transparent NoData |
| **Map Layer Metadata** | `data/layers/metadata.json` | JSON | Validated geographic bounds & scales |
| **Daily Weather Summary**| `data/processed/weather/meteomatics_daily.json` | JSON | 7-day daily forecast aggregations |
| **Hourly Weather Table** | `data/processed/weather/meteomatics_hourly.csv` | CSV | 169 normalized hourly timesteps |
| **Monthly Climate Climatology** | `data/processed/climate/power_monthly_summary.csv` | CSV | 11-year monthly averages |
| **Climate Indicators** | `data/processed/climate/power_summary.json` | JSON | Monthly distributions & means |
| **SMAP Regional Summary**| `data/processed/regional/smap_summary.json` | JSON | Regional surface & root-zone means |
| **GPM Regional Summary** | `data/processed/regional/gpm_summary.json` | JSON | Regional precipitation totals & rainy days |
| **K-Means Model Pipeline**| `ml/clustering/artifacts/kmeans.joblib` | Scikit-Learn | Fitted KMeans ($k=3$, random_state=42) |
| **StandardScaler** | `ml/clustering/artifacts/scaler.joblib` | Scikit-Learn | Fitted StandardScaler pipeline |
| **Cluster Profiles** | `ml/clustering/artifacts/cluster_profile.json` | JSON | Physical cluster center metrics |
| **Model Metrics** | `ml/clustering/artifacts/metrics.json` | JSON | Silhouette & Davies-Bouldin metrics |

---

## 3. Data Schemas

### 3.1 `data/features/features.json`

Top-level object containing spatial metadata and an array of individual observation points:

```json
{
  "meta": {
    "data_mode": "<string: 'real' | 'demo'>",
    "feature_schema_version": "<string: '1.0'>",
    "processing_version": "<string: '1.0'>",
    "generated_at": "<ISO-8601 UTC timestamp>",
    "pilot_bounds": {
      "west": "<float: west longitude>",
      "south": "<float: south latitude>",
      "east": "<float: east longitude>",
      "north": "<float: north latitude>",
      "crs": "<string: 'EPSG:4326'>",
      "region_name": "<string: region identifier>"
    },
    "source_dates": {
      "landsat_9": "<string: YYYY-MM-DD>",
      "srtm_dem": "<string: YYYY-MM-DD>",
      "nasa_power_climate": "<string: YYYY-MM-DD to YYYY-MM-DD>",
      "nasa_smap": "<string: YYYY-MM-DD to YYYY-MM-DD>",
      "nasa_gpm_imerg": "<string: YYYY-MM-DD to YYYY-MM-DD>",
      "meteomatics_weather": "<string: YYYY-MM-DD to YYYY-MM-DD>"
    },
    "source_resolutions": {
      "landsat_9": "<string: resolution in meters>",
      "srtm_dem": "<string: resolution in meters>",
      "nasa_power_climate": "<string: grid resolution>",
      "nasa_smap": "<string: grid resolution>",
      "nasa_gpm_imerg": "<string: grid resolution>",
      "meteomatics_weather": "<string: temporal resolution>"
    },
    "temporal_alignment": {
      "landsat_vs_gpm": "<string: alignment description>",
      "landsat_vs_smap": "<string: alignment description>",
      "landsat_vs_power": "<string: alignment description>",
      "landsat_vs_meteomatics": "<string: alignment description>"
    },
    "limitations": [
      "<string: mandatory scientific limitation notice>"
    ]
  },
  "points": [
    {
      "id": "<string: unique point ID e.g. hyd_001>",
      "lat": "<float: decimal latitude>",
      "lon": "<float: decimal longitude>",
      "analysis_radius_m": "<int: buffer radius in meters e.g. 150>",
      "analysis_method": "<string: 'local_zonal_summary'>",
      "cluster_id": "<int: 0 | 1 | 2>",
      "cluster_label": "<string: 'Relatively vegetated' | 'Intermediate condition' | 'Higher bare/thermal exposure'>",
      "cluster_distance": "<float: Euclidean distance to centroid in scaled space>",
      "features": {
        "ndvi_mean": "<float: mean NDVI [-1.0, 1.0]>",
        "ndmi_mean": "<float: mean NDMI [-1.0, 1.0]>",
        "bsi_mean": "<float: mean BSI [-1.0, 1.0]>",
        "surface_temp_c": "<float: land surface temperature in deg C>",
        "cloud_free_fraction": "<float: fraction [0.0, 1.0]>",
        "elevation_m": "<float: elevation in meters>",
        "slope_deg": "<float: slope in degrees>",
        "low_lying_flag": "<boolean: true | false>",
        "heat_days_40c_by_month": {
          "<month_str 1..12>": "<float: days count>"
        },
        "tmax_mean_by_month": {
          "<month_str 1..12>": "<float: deg C>"
        },
        "rain_mm_by_month": {
          "<month_str 1..12>": "<float: mm total>"
        },
        "rh_mean": "<float: percent>",
        "wind_mean": "<float: m/s>",
        "solar_radiation_mean": "<float: MJ/m^2/day>"
      },
      "clustering": {
        "cluster_id": "<int: 0 | 1 | 2>",
        "cluster_label": "<string: neutral cluster name>",
        "cluster_distance": "<float: distance>"
      },
      "regional_context": {
        "smap_surface_mean": "<float: m^3/m^3>",
        "smap_rootzone_mean": "<float: m^3/m^3>",
        "gpm_total_mm": "<float: mm>",
        "gpm_rainy_days": "<int: days count>",
        "gpm_max_daily_mm": "<float: mm/day>"
      },
      "data_quality": {
        "core_sources_valid": "<boolean: true | false>",
        "cloud_free_fraction": "<float: fraction>",
        "temporal_alignment_score": "<float: score e.g. 0.85>",
        "warnings": [
          "<string: quality warning>"
        ]
      }
    }
  ]
}
```

---

### 3.2 `data/layers/metadata.json`

Web-mapping layer registration schema (for Leaflet/Mapbox image overlays):

```json
{
  "bounds": {
    "west": "<float: 68.20>",
    "south": "<float: 25.20>",
    "east": "<float: 68.55>",
    "north": "<float: 25.55>"
  },
  "layers": {
    "<layer_key: 'ndvi' | 'ndmi' | 'bsi' | 'slope'>": {
      "file": "<string: filename.png>",
      "provider": "<string: provider name>",
      "product": "<string: product name>",
      "observation_date": "<string: YYYY-MM-DD>",
      "source_resolution_m": "<int: resolution>",
      "unit": "<string: index | degrees | C>",
      "minimum": "<float: observed min>",
      "maximum": "<float: observed max>",
      "color_scale": "<string: color scale description>",
      "limitation": "<string: layer limitation notice>"
    }
  }
}
```

---

### 3.3 `data/processed/weather/meteomatics_daily.json`

Short-range 7-day daily forecast summary schema:

```json
{
  "metadata": {
    "source": "Meteomatics Weather API",
    "is_sample": false,
    "is_live": false,
    "generated_at": "<ISO-8601 UTC timestamp>",
    "valid_from": "<ISO-8601 UTC timestamp>",
    "valid_until": "<ISO-8601 UTC timestamp>",
    "expired": "<boolean: true | false>",
    "coordinates": {
      "latitude": "<float>",
      "longitude": "<float>"
    },
    "location_name": "<string>",
    "parameters": ["t_2m:C", "precip_1h:mm", "relative_humidity_2m:p", "wind_speed_10m:ms"]
  },
  "daily_forecast": [
    {
      "date": "<string: YYYY-MM-DD>",
      "tmax_c": "<float>",
      "tmin_c": "<float>",
      "rain_total_mm": "<float>",
      "rh_mean": "<float>",
      "wind_max_ms": "<float>",
      "hours_count": "<int: e.g. 24>"
    }
  ]
}
```

---

### 3.4 `ml/clustering/artifacts/cluster_profile.json`

```json
{
  "<cluster_id: '0' | '1' | '2'>": {
    "cluster_id": "<int>",
    "cluster_label": "<string: neutral label>",
    "sample_count": "<int>",
    "sample_fraction": "<float>",
    "center_original_units": {
      "ndvi_mean": "<float>",
      "ndmi_mean": "<float>",
      "bsi_mean": "<float>",
      "surface_temp_c": "<float>",
      "elevation_m": "<float>",
      "slope_deg": "<float>"
    },
    "std_original_units": {
      "ndvi_mean": "<float>",
      "ndmi_mean": "<float>",
      "bsi_mean": "<float>",
      "surface_temp_c": "<float>",
      "elevation_m": "<float>",
      "slope_deg": "<float>"
    },
    "interpretation": "<string>"
  }
}
```

---

## 4. Integration Instructions for Codex

### 4.1 FeatureStore Integration
- Update `apps/api/app/features.py` (or FeatureStore adapter) to read from `data/features/features.json` when `AGRISHIFT_DATA_MODE=real`.
- Implement a nearest-neighbor spatial lookup:
  Given target field coordinates `(user_lat, user_lon)`:
  1. Check if `(user_lat, user_lon)` falls within `meta.pilot_bounds`.
  2. If inside, compute Euclidean or Haversine distance to all points in `points`.
  3. Select point with minimum distance $\le 5\text{ km}$ threshold.
  4. Return that point's `features`, `clustering`, and `regional_context`.
  5. If outside pilot bounds or nearest point $> 5\text{ km}$, attach warning: `"Location outside pilot validation bounds; using nearest representative regional pilot point."`

### 4.2 K-Means Clustering Integration
- In the analysis API endpoint response (`/api/v1/analyze`), populate:
  - `cluster_id = point["cluster_id"]`
  - `cluster_label = point["cluster_label"]`
  - `cluster_distance = point["cluster_distance"]`
- In UI explainability, surface `cluster_label` (e.g. "Relatively vegetated") along with `cluster_profile.json` interpretation. Never replace these neutral labels with medical/diagnostic crop assertions.

### 4.3 Static Map Overlays
- Mount `data/layers/` as a static file directory in FastAPI (`app.mount("/static/layers", StaticFiles(directory="data/layers"), name="layers")`).
- Provide an endpoint `/api/v1/layers` returning `data/layers/metadata.json` with URLs pointing to `/static/layers/ndvi.png`, etc.
- In frontend Leaflet map, display layers using `L.imageOverlay('/static/layers/ndvi.png', [[25.20, 68.20], [25.55, 68.55]], {opacity: 0.7})`.

### 4.4 Weather Integration
- If Meteomatics live API credentials are unset or live call fails, fallback cleanly to `data/processed/weather/meteomatics_daily.json` and flag `is_live: false, is_sample: false, source: "Saved provider response"`.
- Check `expired` field and surface `valid_until` in response payload.
