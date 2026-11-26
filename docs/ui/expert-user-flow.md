# AgriShift AI — Expert Portal & Evidence Review Flow

## 1. Design Philosophy: Professional Evidence Experience
The Expert Portal is designed for **agronomists, agricultural extension officers, and university researchers**.
- **What it IS**: A calm, authoritative **scientific evidence review workspace**—resembling modern clinical or geospatial research portals.
- **What it is NOT**:
  - **NOT a developer debug dashboard**: No raw JSON dumps as primary UI, no terminal logs, no API latency gauges.
  - **NOT a generic admin panel**: No noisy user-management CRUD tables, no dark-mode neon charts, no multi-level sidebars with 20 dead links.

```
[Public Header / Footer Link: "Expert Portal"]
   │
   ▼
[Screen E1: Expert Login] ──(Authenticated)──> [Screen E2: Expert Dashboard]
                                                  ├── Search by Analysis ID
                                                  ├── Filter: Unverified Rules / Salinity / Date
                                                  └── Recent Field Analyses Table
                                                          │
                                                          ▼
                                               [Screen E3: Expert Analysis Detail]
                                                  ├── Environmental Evidence (Landsat 9 / SRTM)
                                                  ├── Climate Summary (NASA POWER 2015–2025)
                                                  ├── K-Means Cluster Diagnostics (k=3)
                                                  ├── Rotation Rule Breakdown & Confidence Audit
                                                  ├── Expert Notes & Agronomic Verification Form
                                                  └── Review Actions (Approve / Flag / Export)
```

---

## 2. Screen E1: Expert Login (`/expert/login`)

### 2.1 Purpose & Layout
- **Purpose**: Gate access to detailed multi-spectral diagnostics, internal review queues, and agronomic verification notes.
- **Layout**: Centered single-card authentication layout (`max-width: 420px`) on `#F8FAFC` canvas.
- **Visible Elements**:
  - AgriShift AI crest + `"Agronomic Evidence Portal"` title.
  - Subtitle: *"Sign in to audit satellite evidence, K-Means cluster assignments, and field rotation rules."*
  - Email / Username input (`44px` height).
  - Password input with show/hide eye icon toggle.
  - Primary CTA: `"Sign In to Portal"`.
  - Secondary link: `"← Return to Public Farmer Tool"`.
- **Error & Security Behavior**:
  - Invalid credentials show calm inline risk alert: *"Invalid credentials. Please verify your extension officer ID."*
  - Never display hardcoded demo passwords or provider API credentials.

---

## 3. Screen E2: Expert Dashboard (`/expert/dashboard`)

### 3.1 Top Navigation Bar
- Clean `64px` white top bar:
  - Left: `"AgriShift AI • Expert Review"`
  - Center/Right: Quick Search input (`"Jump to Analysis ID (e.g. AGR-...)"`), `"Public Farmer View"` link, User badge + `"Sign Out"`.

### 3.2 Workspace Header & KPI Summary Row
4 quiet, high-clarity summary cards (`1px solid #E2E8F0`, `#FFFFFF`, no heavy shadows):
1. **Total Pilot Analyses** (count from SQLite persistence)
2. **Pending Expert Review** (analyses flagged by salinity/waterlogging unverified rules or capped confidence $\le 2$ dots)
3. **Pilot Feature Coverage** (`149 validated grid points • 2 km spacing`)
4. **Model & Weather Status** (`K-Means k=3 Active` + `Meteomatics Live / Sample`)

### 3.3 Filter & Search Toolbar
- Search by `Analysis ID` or `Crop`.
- Quick filter chips: `All Analyses` | `Needs Review (Unverified Rules)` | `Salinity Flagged` | `Waterlogging Flagged` | `Outside Pilot`.

### 3.4 Recent Field Analyses Table
Clean full-width SaaS table (converts to compact summary cards on mobile `< 768px`):
- Columns:
  1. `Analysis ID` (monospace link)
  2. `Timestamp`
  3. `Location & Match` (`25.396°N, 68.358°E • 0.4 km`)
  4. `Crop & Conditions` (`Cotton • Low Water • Salinity`)
  5. `Cluster` (neutral pill: `Relatively vegetated`)
  6. `Confidence` (`2/3 dots` + caution icon if capped)
  7. `Review Status` (`Pending Review` | `Verified` | `Flagged`)
  8. `Action` (`"Inspect Evidence →"`)

---

## 4. Screen E3: Expert Analysis Detail (`/expert/analyses/{analysis_id}`)

### 4.1 Sticky Header & Breadcrumb
- Breadcrumb: `Expert Dashboard / Analysis AGR-XXXX`
- Metadata strip: `Date`, `Data Mode (REAL / DEMO)`, `Farmer Language`, `Nearest Pilot Point ID (hyd_042, distance 0.42 km)`.
- Quick Action: `"Open Farmer View"` (to preview what the farmer sees).

### 4.2 Section Layout (2-Column Desktop `65% / 35%`, Single-Column Stacked Mobile)

#### Main Column (Left / Primary Evidence — `65%`)

1. **Section 1: Environmental Evidence (Satellite & Terrain)**
   - **Layout**: Side-by-side interactive Expert Map (`height: 360px`) + structured Data Attribution Table.
   - **Map Features**:
     - Shows both Farmer Pin and Nearest Validated Pilot Point (`150m` radius circle drawn on map).
     - Full layer toggles (`NDVI`, `NDMI`, `BSI`, `Slope`) with opacity slider (`0%–100%`) and full numeric color ramp legend.
   - **Attribution Card / Table**:
     - **Landsat 9 OLI/TIRS**: Scene `LC09_L2SP_151043_20250930_20251001_02_T1`, Acquired `2025-09-30`, `30 m` resolution, `98.76%` cloud-free swath. Values: `NDVI`, `NDMI`, `BSI`, `LST (°C)`.
     - **SRTM DEM**: `30 m` UTM Zone 42N metric slope (`degrees`), Elevation (`m`), Relative low-lying indicator (`Yes/No`, threshold $P_{15} = 18.77\text{ m}$).
     - **Regional Context (SMAP & GPM)**: Explicitly separated in a subtle `#E0F2FE` info sub-panel citing `9 km` SMAP (`0.0725 m³/m³` surface / `0.1413 m³/m³` root-zone, Oct 2026 offset noted) and `0.1°` GPM (`38.26 mm` 7-day accumulation, Sep 2025).

2. **Section 2: Climate Summary (NASA POWER 2015–2025)**
   - **Visual**: **Collapsible Section** (Expanded by default on desktop, collapsed on mobile).
   - **Chart**: Clean dual-axis or grouped **Monthly Climatology Chart** (12 months Jan–Dec) showing Mean Max/Min Temperature (`°C` line) vs. Monthly Precipitation (`mm` bar).
   - **Summary KPIs**: Annual Mean `28.16°C`, Summer Peak `44.97°C`, Extreme Heat Days ($\ge 40^\circ\text{C}$): `76.3 days/yr`, Annual Rain `234.33 mm`.
   - **Disclaimer tag**: *"Regional gridded climate reanalysis (0.5° × 0.625°); not an on-farm weather station."*

3. **Section 3: K-Means Environmental Cluster Breakdown**
   - **Visual**: **Collapsible Section** (Expanded by default).
   - **Cards**: Assigned Cluster Badge (`Cluster 0: Relatively vegetated`, `n=62, 41.6%` of pilot) + Distance to centroid.
   - **Chart**: Horizontal **Normalized Feature Radar or Grouped Bar Comparison** comparing this point's 6 standardized features (`NDVI`, `NDMI`, `BSI`, `Surface Temp`, `Elevation`, `Slope`) against the 3 cluster centroids.
   - **Model Integrity Metadata**: `k=3`, `Silhouette: 0.3546`, `Davies-Bouldin: 0.9780`. Explicit note: *"Unsupervised environmental pattern grouping; not a yield or disease classifier."*

4. **Section 4: Rotation Breakdown & Agronomic Rule Trace**
   - **Visual**: Structured Audit Table + **Collapsible Rule Details**.
   - Shows all 3 returned options (**Current**, **Balanced**, **Priority**) with:
     - Raw rule score, water penalty applied, salinity/waterlogging verification status (`Verified` vs `Unverified`).
     - Exact rule triggers explaining why a crop was penalized or boosted.
     - Confidence calculation breakdown (e.g., *"Base 3 dots -> Capped at 2 dots due to unverified salinity rule"*).

#### Side Column (Right / Agronomic Action Rail — `35%`)

5. **Section 5: Expert Notes**
   - Clean text area (`min-height: 120px`) for the extension officer to record local field verification notes (e.g., *"Verified tube-well salinity EC 2.4 dS/m; recommended Salt-tolerant Barley or Mustard"*).
   - Historical timestamped notes log below the input (read-only audit trail).

6. **Section 6: Review Actions**
   - **Status Selector**: `Mark as Locally Verified` | `Flag Agronomic Caution` | `Recommend Soil Test`.
   - **Primary CTA**: `"Save Expert Review"` (persists note and verification status).
   - **Secondary Actions**: `"Export Evidence Summary (PDF/Print)"`, `"Copy Shareable Advisory for Farmer"`.
   - **Collapse Behavior**: On mobile (`< 768px`), the Side Column (`Expert Notes` and `Review Actions`) stacks neatly at the bottom with a sticky `"Jump to Review Action"` quick-button at the top.
