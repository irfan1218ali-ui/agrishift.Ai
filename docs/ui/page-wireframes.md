# AgriShift AI — Structural Page Wireframes

## 1. Public Landing Page

### 1.1 Desktop Wireframe (`1366px`, container `max-width: 1200px`)
```
+-----------------------------------------------------------------------------+
| [Logo] AgriShift AI          [EN | اردو | سنڌي]      [Expert Portal Login]  |
+-----------------------------------------------------------------------------+
| (Optional Demo Strip if DEMO_MODE=true)                                     |
+-----------------------------------------------------------------------------+
| HERO SECTION (2-Column Grid: 60% / 40%)                                     |
|  [Pilot Pill: Hyderabad, Sindh • Free Access]                               |
|  H1: Evidence-Backed Crop Rotation Planning     +-------------------------+ |
|  Subtitle: Compare seasonal rotations using     | [Map Thumbnail: NDVI]   | |
|  real NASA Earth observations & local rules.    |  Cluster 0: Vegetated   | |
|                                                 |  3 Rotation Options     | |
|  [ Primary CTA: Start Field Analysis -> ]       +-------------------------+ |
|  Have an Analysis Code? [AGR-____] [Open]                                   |
+-----------------------------------------------------------------------------+
| PROBLEM STATEMENT (#F8FAFC band, 3-Col Cards)                               |
|  [Card: 44°C+ Heat Stress]  [Card: Salinity & Drainage]  [Card: Water Gaps] |
+-----------------------------------------------------------------------------+
| HOW IT WORKS (4-Step Horizontal Stepper Cards)                              |
|  [1. Pin Field] -> [2. Water & Soil] -> [3. NASA Context] -> [4. Compare]   |
+-----------------------------------------------------------------------------+
| DATA SOURCES TRANSPARENCY GRID (#F8FAFC band, 3x2 Grid)                     |
|  [Landsat 9 (30m)]   [SRTM DEM (30m)]      [NASA POWER (2015–2025)]         |
|  [NASA SMAP (~9km)]  [NASA GPM (0.1°)]     [Meteomatics Weather]            |
+-----------------------------------------------------------------------------+
| BENEFITS & RESPONSIBLE AI CALLOUT                                           |
|  • Supports local farmer judgment   • Never diagnoses disease / predicts    |
|  • Transparent confidence caps        floods                                |
|  [ Final CTA: Analyze Your Field Now ]                                      |
+-----------------------------------------------------------------------------+
| FOOTER: AgriShift AI • Known Limitations • Expert Portal                    |
+-----------------------------------------------------------------------------+
```

### 1.2 Mobile Wireframe (`360px`)
```
+-------------------------------+
| [Logo] AgriShift AI  [EN|UR]  |
+-------------------------------+
| [Hyderabad Pilot • Real Data] |
| H1: Evidence-Backed Crop      |
|     Rotation Planning         |
| [Start Field Analysis ->]     |
| Reload Code: [AGR-___] [Go]   |
+-------------------------------+
| [Problem Card 1: Heat]        |
| [Problem Card 2: Salinity]    |
| [Problem Card 3: Water]       |
+-------------------------------+
| How It Works (Vertical 1..4)  |
| Data Sources (1-col Cards)    |
| Responsible AI Notice         |
| [Analyze Your Field Now]      |
| Footer: Expert Portal Link    |
+-------------------------------+
```

---

## 2. 5-Step Analysis Wizard (`max-width: 720px` centered)

### Common Sticky Wizard Shell
```
+-------------------------------------------------------+
| [<- Back]     Step 2 of 5: Crop History      [Cancel] |
| [=============>------------------------] 40%          |
+-------------------------------------------------------+
```

### Step 1: Location
```
| Title: Where is your field located?                   |
| [Crosshair Icon: Use My Current GPS Location]         |
| +---------------------------------------------------+ |
| |        INTERACTIVE MAP (Hyderabad Bounds)         | |
| |        [Dashed Pilot Boundary]                    | |
| |                    (Pin)                          | |
| +---------------------------------------------------+ |
| [Selected: 25.3960° N, 68.3578° E • Inside Pilot]     |
| [v Enter Coordinates Manually (Accordion)]            |
| [ Primary CTA: Continue to Crop History -> ]          |
+-------------------------------------------------------+
```

### Step 2: Crop History
```
| Title: Which crop is currently in your field?         |
| +---------------+ +---------------+ +---------------+ |
| | [SVG] Cotton  | | [SVG] Wheat   | | [SVG] Rice    | |
| | Kharif        | | Rabi          | | Kharif        | |
| +---------------+ +---------------+ +---------------+ |
| +---------------+ +---------------+ +---------------+ |
| | [SVG] Mustard | | [SVG] Sorghum | | [SVG] Sugarcane|
| +---------------+ +---------------+ +---------------+ |
| [ Primary CTA: Continue to Farm Conditions -> ]       |
+-------------------------------------------------------+
```
*(Note: On `320px–390px` mobile, grid transitions from 3-col to 2-col).*

### Step 3: Farm Conditions
```
| Title: Describe your water and soil conditions        |
| Q1. Canal / Irrigation Water Availability *           |
| [ Low (Limited) ] [ Medium (Standard) ] [ High ]      |
|                                                       |
| Q2. Soil Salinity Observed? *                         |
| [ No Salinity Seen ]    [ Yes — Salt Stress Seen ]    |
|                                                       |
| Q3. Seasonal Waterlogging Observed? *                 |
| [ No Waterlogging ]     [ Yes — Slow Drainage ]       |
|                                                       |
| [ Primary CTA: Continue to Priority -> ]              |
+-------------------------------------------------------+
```

### Step 4: Farmer Priority
```
| Title: What matters most for your next season?        |
| +---------------------------------------------------+ |
| | [O] Balanced Approach                             | |
| |     Steady income with manageable water/soil risk | |
| +---------------------------------------------------+ |
| | (*) Save Water  [Selected: #F0FDF4, 2px #15803D]  | |
| |     Lower-irrigation crops for limited water      | |
| +---------------------------------------------------+ |
| | [O] Soil & Income Resilience                      | |
| |     Legume/oilseed diversification                | |
| +---------------------------------------------------+ |
| [ Primary CTA: Review Details -> ]                    |
+-------------------------------------------------------+
```

### Step 5: Review & Submit
```
| Title: Review your field details                      |
| +---------------------------------------------------+ |
| | Location    : 25.3960° N, 68.3578° E     [Edit]   | |
| | Current Crop: Cotton                     [Edit]   | |
| | Conditions  : Low Water, Salinity: Yes   [Edit]   | |
| | Priority    : Save Water                 [Edit]   | |
| +---------------------------------------------------+ |
| [Info Strip: Uses Real NASA & Climate Data]           |
| [ Primary CTA: Generate Rotation Options ]            |
+-------------------------------------------------------+
```

---

## 3. Farmer Results Dashboard (`max-width: 1200px`)

```
+-----------------------------------------------------------------------------+
| STICKY BAR: Analysis ID: AGR-2026-8492 [Copy] | [Badge: REAL DATA] | [New]  |
+-----------------------------------------------------------------------------+
| 1. ANALYSIS SUMMARY HEADER                                                  |
|    Field: 25.396°N, 68.358°E (Nearest grid: 0.42 km) | Cotton -> Save Water |
+-----------------------------------------------------------------------------+
| 2. ENVIRONMENTAL SUMMARY STRIP (3-Col Desktop / 1-Col Stack Mobile)         |
|  [Cluster: Relatively vegetated] | [NDVI 0.59 • 37.4°C] | [SMAP/GPM Regional]|
+-----------------------------------------------------------------------------+
| 3. THREE RECOMMENDATION CARDS (3-Col Desktop / 1-Col Mobile)                |
|  +--------------------+  +--------------------+  +--------------------+     |
|  | CURRENT ROTATION   |  | BALANCED OPTION    |  | PRIORITY OPTION ★  |     |
|  | Cotton -> Wheat    |  | Cotton -> Mustard  |  | Cotton -> Chickpea |     |
|  | [Water: High]      |  | [Water: Medium]    |  | [Water: Low]       |     |
|  | Risk: Medium       |  | Risk: Low          |  | Risk: Low          |     |
|  | Confidence: ••◦    |  | Confidence: ••◦    |  | Confidence: ••◦    |     |
|  | • Explanations     |  | • Explanations     |  | • Explanations     |     |
|  +--------------------+  +--------------------+  +--------------------+     |
+-----------------------------------------------------------------------------+
| 4. COMPARISON TABLE (Desktop Matrix / Mobile Horizontal Scroll or Cards)    |
|  Metric | Current (Wheat) | Balanced (Mustard) | Priority (Chickpea)        |
+-----------------------------------------------------------------------------+
| 5. WEATHER & MAP SPLIT (Desktop 45% / 55% | Mobile Stacked)                 |
|  +-----------------------------+  +---------------------------------------+ |
|  | WEATHER CONTEXT             |  | INTERACTIVE MAP                       | |
|  | [Badge: Saved Sample]       |  | [Layers: NDVI | NDMI | BSI | Slope]   | |
|  | Temp: 29.8°C | Rain: 29.9mm |  | [Zoom +/-]           [Legend Strip]   | |
|  +-----------------------------+  +---------------------------------------+ |
+-----------------------------------------------------------------------------+
| 6. EXPLANATION TIMELINE ("How This Result Was Built")                       |
|  (1) Field Inputs -> (2) Satellite Match -> (3) K-Means -> (4) Rules & Cap  |
+-----------------------------------------------------------------------------+
| 7. NEXT ACTIONS & ADVISORY FOOTER                                           |
|  [ WhatsApp Share ]   [ Copy Analysis ID ]   [ Print ]   [ Expert View ]    |
|  Disclaimer: Supports farmer judgment; not disease diagnosis/flood forecast |
+-----------------------------------------------------------------------------+
```

---

## 4. Expert Portal Wireframes

### 4.1 Expert Dashboard (`/expert/dashboard`)
```
+-----------------------------------------------------------------------------+
| AgriShift AI • Expert Review   [Search ID: AGR-____]   [Farmer App] [Logout]|
+-----------------------------------------------------------------------------+
| KPI ROW (4 Quiet Stat Cards)                                                |
|  [Total Analyses]  [Pending Review (Capped)]  [149 Pilot Pts]  [Model: k=3] |
+-----------------------------------------------------------------------------+
| FILTER BAR: [All] [Needs Review] [Salinity] [Waterlogging] [Outside Pilot]  |
+-----------------------------------------------------------------------------+
| ANALYSES EVIDENCE TABLE                                                     |
|  ID       | Date       | Location     | Crop/Cond     | Cluster | Conf |Act |
|  AGR-8492 | 2026-11-25 | 25.39, 68.35 | Cotton/Sal    | Clus 0  | ••◦  |[->]|
+-----------------------------------------------------------------------------+
```

### 4.2 Expert Analysis Detail (`/expert/analyses/{id}`)
```
+-----------------------------------------------------------------------------+
| <- Dashboard / Analysis AGR-8492   [REAL DATA]   Point: hyd_042 (0.42 km)   |
+-----------------------------------------------------------------------------+
| LEFT EVIDENCE COLUMN (65%)                 | RIGHT ACTION RAIL (35%)        |
|                                            |                                |
| 1. ENVIRONMENTAL EVIDENCE                  | 5. EXPERT NOTES                |
|    [Interactive Map + 150m Radius Circle]  |    [Textarea: Local EC/pH...]  |
|    [Layer Toggles + Opacity Slider]        |    Past Notes Log              |
|    [Landsat 9 & SRTM Attribution Table]    |                                |
|    [SMAP 9km / GPM 0.1° Regional Panel]    | 6. REVIEW ACTIONS              |
|                                            |    ( ) Locally Verified        |
| 2. CLIMATE SUMMARY (Collapsible)           |    ( ) Flag Agronomic Caution  |
|    [NASA POWER 12-Mo Temp/Rain Chart]      |    ( ) Recommend Soil Test     |
|                                            |    [ Save Expert Review ]      |
| 3. K-MEANS CLUSTER DIAGNOSTICS             |    [ Print / Export PDF ]      |
|    [Feature Comparison Chart vs Centroids] |                                |
|                                            |                                |
| 4. ROTATION RULE BREAKDOWN TABLE           |                                |
|    [Scores, Penalties, Confidence Cap Log] |                                |
+-----------------------------------------------------------------------------+
```
