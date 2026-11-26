# AgriShift AI — Public Farmer Experience & User Flow

## 1. Journey Architecture Overview
The Public Farmer Experience requires **zero login or account creation**. A farmer opens the platform, optionally switches language (English, Urdu, Sindhi), enters a 5-step guided analysis wizard, and receives clear, explainable crop-rotation options backed by NASA Earth observations and local agronomic rules.

```
[Landing Page]
   ├──> [Language Switcher (EN / UR / SD)] (Top Navbar, persistent)
   ├──> [Reload Saved Analysis by ID] ───────────────┐
   └──> [Start Field Analysis (5-Step Wizard)]       │
           ├── Step 1: Location (GPS / Map Pin)      │
           ├── Step 2: Crop History                  │
           ├── Step 3: Farm Conditions               │
           ├── Step 4: Farmer Priority               │
           └── Step 5: Review & Submit               │
                   │                                 ▼
                   └──────────────> [Results Dashboard]
                                       ├── Analysis & Environmental Summary
                                       ├── 3 Rotation Recommendation Cards
                                       ├── Side-by-Side Comparison Table
                                       ├── Weather & Interactive Map Overlays
                                       ├── Explanation Timeline
                                       └── Next Actions (WhatsApp Share / Save ID)
```

---

## 2. Screen 1: Public Landing Page

### 2.1 Screen Purpose & Actions
- **Purpose**: Build immediate institutional trust, explain how NASA satellite evidence supports farmer rotation choices without replacing local expertise, and provide a frictionless entry into the analysis wizard.
- **Primary Action**: `"Start Field Analysis"` button (launches Step 1 of the Wizard).
- **Secondary Actions**:
  1. `"Open Saved Analysis"` (compact inline input/modal to reload an existing `analysis_id`).
  2. Language selector (`English` | `اردو` | `سنڌي`) in top bar.
  3. Subtle `"Expert Portal"` link in top navbar / footer (for agronomists only).

### 2.2 Exact Section Order, Spacing & Card Layouts
1. **Top Navigation Bar** (`height: 64px`, sticky, `#FFFFFF` with `1px solid #E2E8F0` bottom border):
   - Brand logo + `"AgriShift AI"` wordmark.
   - Right/End cluster: Language Segmented Control (`EN | اردو | سنڌي`), `"Expert Portal"` text link.
2. **Data Mode Status Strip** (conditional, slim `32px` bar below nav):
   - Only prominent if `DEMO_MODE=true` (`#FEF3C7` warning strip: *"Demo Mode Active — Using sample environmental records"*). In Real Mode, shows a subtle verified pill inside the Hero.
3. **Hero Section** (`padding: 48px 16px` mobile, `72px 24px` desktop):
   - **Left/Start**: Pilot badge (`"Hyderabad, Sindh Pilot • Free Public Access"`), Display headline (*"Evidence-Backed Crop Rotation Planning"*), 2-line value proposition, Primary CTA (`"Start Field Analysis"`), Secondary inline lookup (`"Have an Analysis ID? Enter code"`).
   - **Right/End (Desktop only; stacked compact preview on Mobile)**: Clean illustrative preview card showing the Hyderabad satellite overlay thumbnail + 3 sample rotation summary pills.
4. **Problem Statement Strip** (`padding: 32px 16px`, `#F8FAFC` subtle band):
   - 3 concise horizontal cards on desktop (1-col stack on mobile):
     1. *Heat & Water Stress* (44°C+ summer peaks, variable canal supply)
     2. *Soil Salinity & Drainage* (Unmonitored salinity and low-lying ponding risks)
     3. *Blind Rotation Choices* (Repeating water-heavy sequences without seasonal context)
5. **How It Works** (`padding: 48px 16px`):
   - 4 numbered step cards (`1. Pin Your Field` $\rightarrow$ `2. Share Water & Soil Reality` $\rightarrow$ `3. Satellite & ML Context` $\rightarrow$ `4. Compare 3 Rotations`).
6. **Data Sources Transparency Grid** (`padding: 32px 16px`, `#F8FAFC`):
   - 6 clean source cards in a `3x2` desktop grid (`2x3` tablet, `1-col` mobile):
     - **Landsat 9 (30m)**: Vegetation & surface heat snapshot
     - **SRTM DEM (30m)**: Elevation & slope gradient
     - **NASA POWER**: 11-year historical climate baseline
     - **NASA SMAP (~9km)**: Regional soil-moisture context
     - **NASA GPM (0.1°)**: Regional satellite rainfall context
     - **Meteomatics**: 7-day weather context (live or saved sample)
7. **Farmer Benefits & Responsible AI Callout** (`padding: 40px 16px`):
   - Clear 3-bullet benefit list + boxed Responsible AI statement (*"Supports farmer judgment; not a disease diagnosis or flood prediction"*).
8. **Bottom Call to Action & Footer** (`padding: 48px 16px`):
   - Final `"Analyze Your Field Now"` CTA + subtle footer with `"Expert Portal Login"` and `"Known Limitations"`.

### 2.3 What Should NOT Appear on Landing
- No raw JSON, SHA-256 hashes, K-Means Silhouette/Davies-Bouldin math metrics, or developer debug logs.
- No login wall or registration prompt for farmers.

---

## 3. Screen 2: 5-Step Analysis Wizard

A single focused container (`max-width: 720px` centered on desktop, full-bleed padding `16px` on mobile) with a sticky top **Step Progress Header** (`Step X of 5` + slim progress bar + Back button).

### Step 1: Location (`Pin Your Field`)
- **Title**: *"Where is your field located?"*
- **Subtitle**: *"Tap the map inside the Hyderabad pilot area or use your phone's GPS."*
- **Inputs**:
  - Primary quick button: `"Use My Current GPS Location"` (with GPS crosshair SVG).
  - Interactive Map (`height: 320px` mobile / `380px` desktop) centered on Hyderabad pilot `[68.20°E–68.55°E, 25.20°N–25.55°N]` with visible dashed pilot boundary polygon.
  - Collapsible `"Enter Coordinates Manually"` accordion (Latitude / Longitude numeric inputs).
  - Real-time coordinate confirmation chip below map: `"Selected: 25.3960° N, 68.3578° E • Inside Hyderabad Pilot"`.
- **Buttons**: Back (`"Home"`), Primary (`"Continue to Crop History"`).
- **Error Handling**:
  - *GPS Denied/Timeout*: Amber info alert (*"GPS unavailable. Please tap directly on the map or enter coordinates."*). Never blocks progress.
  - *Outside Pilot Coordinates*: Inline warning badge (*"This location is outside the Hyderabad pilot zone. Results will show outside-pilot notice."*).
- **Empty State**: No pin placed yet $\rightarrow$ Primary button disabled with helper text *"Place a pin on the map to continue"*.

### Step 2: Crop History (`Previous or Current Crop`)
- **Title**: *"Which crop is currently in your field (or just harvested)?"*
- **Subtitle**: *"Select one crop to evaluate suitable next-season rotations."*
- **Inputs**:
  - Responsive 3-column (desktop/tablet) or 2-column (320px–390px mobile) grid of **Selectable Crop Tiles**.
  - Each tile shows: Clean botanical SVG icon + Crop Name (localized) + Season tag (`Kharif` / `Rabi` / `Annual`).
  - Only crops loaded from `GET /api/v1/crops` appear.
- **Buttons**: Back (`"Location"`), Primary (`"Continue to Farm Conditions"`).
- **Empty / Loading State**: Skeleton shimmer tiles while `/api/v1/crops` loads. If API fails, show retry card.

### Step 3: Farm Conditions (`Water, Salinity & Drainage`)
- **Title**: *"Describe your field's water and soil conditions"*
- **Subtitle**: *"Honest inputs help adjust rotation risk and confidence."*
- **Inputs**:
  1. **Canal / Irrigation Water Availability** (Required, 3-option segmented cards):
     - `Low` (*"Limited / irregular supply"*)
     - `Medium` (*"Standard seasonal turns"*)
     - `High` (*"Reliable irrigation access"*)
  2. **Soil Salinity Observed?** (Required, 2-option toggle cards: `No` / `Yes — White crust or salt stress seen`).
  3. **Seasonal Waterlogging Observed?** (Required, 2-option toggle cards: `No` / `Yes — Standing water drains slowly`).
- **Buttons**: Back (`"Crop History"`), Primary (`"Continue to Priority"`).
- **Error Handling**: Water availability defaults to unselected; user must pick one before continuing.

### Step 4: Farmer Priority (`Select Your Goal`)
- **Title**: *"What matters most for your next season?"*
- **Subtitle**: *"We will highlight a strategy tailored to this priority alongside your current and balanced options."*
- **Inputs**: 3 large descriptive radio cards (stacked on mobile, 3-col on desktop):
  1. **Balanced Approach** (*"Steady income with manageable water and soil risk"*)
  2. **Save Water** (*"Lower-irrigation crops suited for limited water turns"*)
  3. **Soil & Income Resilience** (*"Legume/oilseed diversification and soil recovery"*)
- **Buttons**: Back (`"Farm Conditions"`), Primary (`"Review Details"`).

### Step 5: Review & Submit (`Confirm Field Inputs`)
- **Title**: *"Review your field details"*
- **Subtitle**: *"Confirm your selections before generating environmental rotation options."*
- **Visible Information**:
  - Clean summary card with 4 editable rows (each row has a small `"Edit"` link jumping back to that step):
    - Location (`lat, lon` + mini static pin preview)
    - Current Crop
    - Conditions (Water level, Salinity, Waterlogging)
    - Priority
  - Clear data-mode notice: *"Analysis uses real NASA satellite & climate records for Hyderabad."* (or Demo notice if in demo mode).
- **Buttons**: Back (`"Priority"`), Primary (`"Generate Rotation Options"`).
- **Loading State**:
  - Full-container calm loading card (replaces review buttons, `aria-live="polite"`):
    - Animated botanical spinner + 3 progressive status lines:
      1. *"Matching nearest validated pilot observation point..."*
      2. *"Checking environmental cluster & regional weather..."*
      3. *"Evaluating crop rotation rules..."*
- **Error Handling**:
  - Validation error (422) or server error (500): Clean inline risk banner with `"Try Again"` button and visible `Request ID` for support. Never crashes or wipes user form selections.

---

## 4. Screen 3: Results Page

### 4.1 Exact Visual Hierarchy & Section Order
1. **Top Sticky Summary Bar / Data Mode Banner**:
   - Displays `Analysis ID` (e.g., `AGR-2026-8492` with Copy button), Data Mode pill (`Real Environmental Data` in `#DCFCE7` or `Demo Mode` in `#FEF3C7`), and `"New Analysis"` button.
2. **Section 1 (First Visible): Analysis Summary Header**:
   - Location pin summary (`25.396°N, 68.358°E • Nearest point: 0.42 km away`) + Current Crop $\rightarrow$ Priority badge.
   - If `status == "not_applicable"` or `"insufficient_data"`: Displays a clear, calm explanation card here and hides rotation cards.
3. **Section 2: Environmental Summary Strip** (3 compact metric cards in 3-col desktop / horizontal scroll or stack on mobile):
   - **Environmental Cluster Card**: Neutral label badge (e.g. `"Relatively vegetated"`), neutral subtitle (*"Grouped from Landsat 9 & terrain features — not a crop disease test"*).
   - **Satellite & Terrain Snapshot**: NDVI (`0.59`), Surface Temp (`37.4°C`), Elevation (`21m`), Relative Terrain (`Low-lying indicator` if applicable).
   - **Regional Moisture & Rain Context**: SMAP (`0.07 m³/m³ • 9 km regional`) & GPM (`38.3 mm / 7d • 0.1° regional`), explicitly tagged *"Regional context, not exact farm sensor"*.
4. **Section 3 (Primary Focus): Three Rotation Recommendation Cards**:
   - `3-column` equal-height grid on desktop (`1366px`), `1-column` vertical stack on mobile (`320px–768px`) with **Recommended/Priority or Balanced emphasis**.
   - Cards: **Current Rotation** | **Balanced Option** | **Priority Option**.
5. **Section 4: Side-by-Side Comparison Table**:
   - Clean comparison matrix across the 3 options: Next Crop, Water Need, Risk Level, Confidence, Key Tradeoff, Expert Review Needed.
6. **Section 5: Weather Context Card**:
   - Distinct visual states for **Live**, **Saved Sample**, or **Unavailable** weather (temperature, rain, humidity, wind).
7. **Section 6: Interactive Field & Overlay Map**:
   - Map showing farmer pin, nearest pilot observation point, and toggleable overlays (`NDVI`, `NDMI`, `BSI`, `Slope`) with transparent legends.
8. **Section 7: Explanation Timeline ("How This Result Was Built")**:
   - 4-step collapsible/clean vertical timeline tracing: `Farmer Inputs` $\rightarrow$ `Landsat/SRTM Match` $\rightarrow$ `K-Means Pattern` $\rightarrow$ `Agronomic Rules & Confidence Cap`.
9. **Section 8: Next Actions & Responsible AI Footer**:
   - Primary action: **"Share Summary via WhatsApp"** (`#16A34A` button).
   - Secondary actions: **"Copy Analysis Code"**, **"Print / Save Summary"**, **"Open in Expert View"** (links to Expert Portal if logged in).
   - Mandatory non-dismissible advisory notice: *"This tool supports, but does not replace, farmer judgment or local agronomic verification."*

### 4.2 What Should NOT Appear on Farmer Results
- No raw confusion matrices, PCA/Davies-Bouldin values, raw file paths, or SQLite table IDs.
- No phrasing like *"Your field is healthy"*, *"Disease free"*, or *"Guaranteed 20% yield increase"*.

---

## 5. Screen 4: Share / Save Code Flow
- Clicking **"Share via WhatsApp"** opens a clean preview modal (or directly launches `https://wa.me/?text=...` on mobile) showing the formatted plain-text summary:
  - Analysis ID, Location, Current Crop, Top Recommended Alternative, Confidence level, Weather note, and Disclaimer.
- Clicking **"Save Code"** copies the `analysis_id` with a toast confirmation: *"Code AGR-XXXX copied. Use it anytime on the home screen to reload this result."*
