# AgriShift AI — Component Specifications

## 1. Rotation Recommendation Card (`<RotationCard />`)

### 1.1 Card Variants & Emphasis Rules
All three cards sit in an equal-height 3-column grid on desktop (`1366px`) and stack vertically on mobile (`320px–768px`).
1. **Current Rotation (`variant="baseline"`)**:
   - Header background: `#F8FAFC` (Slate 50), Border: `1px solid #E2E8F0`.
   - Tag: `"Current Practice"` (Neutral Slate pill).
   - No special elevation emphasis.
2. **Balanced Option (`variant="balanced"`)**:
   - Header background: `#FFFFFF`, Border: `1px solid #CBD5E1`.
   - Tag: `"Balanced Alternative"` (Info Blue `#E0F2FE` / `#0369A1`).
3. **Priority Option (`variant="priority"`)**:
   - **Visual Emphasis**: `2px solid #15803D` border, `4px solid #15803D` top accent bar, subtle `#F0FDF4` header strip, `shadow-md`.
   - Tag: `"Matches Your Priority ★"` (Primary Green `#15803D` fill, `#FFFFFF` text).
   - *Note*: On mobile, if the user selected a priority (e.g., Save Water), the **Priority Option** may show a `"Top Match for Your Goal"` ribbon, while keeping clear comparison order.

### 1.2 Exact Content Hierarchy (Top to Bottom)
1. **Card Header**: Variant badge + Strategy Title (e.g. `"Balanced Option"`).
2. **Season Transition Visual**:
   - `[Current Crop SVG + Name]` $\rightarrow$ `[Recommended Next Crop SVG + Name]`
   - Directional arrow mirrors automatically in RTL (`rtl:rotate-180`).
3. **Key Metric Chips Row** (Wrap cleanly):
   - **Water Requirement**: Icon + `"Low Water"` (`#DCFCE7`) | `"Medium Water"` (`#FEF3C7`) | `"High Water"` (`#FEE2E2`).
   - **Agronomic Risk**: `"Low Risk"` | `"Moderate Risk"` | `"Elevated Risk"`.
4. **Confidence Meter**:
   - Visual 3-dot indicator (`● ● ○` = 2 of 3 dots) + text `"Confidence: Medium (2/3)"`.
   - If capped due to unverified rules (salinity/waterlogging): Amber lock/info icon + `"Capped: Needs local verification"`.
5. **Explanation Bullets (Max 3 concise points)**:
   - Plain farmer language explaining agronomic fit, water impact, and nitrogen/soil effect.
6. **Caution / Verification Banner** (Conditional):
   - Appears in `#FEF3C7` tint with `#D97706` border if unverified crop rules apply: *"Tolerance under observed salinity is not locally verified. Consult an extension officer."*

---

## 2. Weather Section (`<WeatherCard />`)

The Weather Section MUST visually distinguish between **Live**, **Saved Sample**, and **Unavailable** states so users are never misled about forecast currency.

### 2.1 State A: Live Weather (`is_live === true`)
- **Border & Header**: `1px solid #E2E8F0`, Top right badge: Green pulsing dot + `"Live Forecast • Meteomatics"` (`#DCFCE7` / `#14532D`).
- **Content**:
  - Timestamp: `"Valid: Nov 25 – Dec 02"`
  - 4 clean metric tiles (`2x2` mobile, `4x1` desktop): Temperature (`°C`), 7-Day Rain (`mm`), Humidity (`%`), Wind (`m/s`).
  - Mini 7-day daily strip showing icon + high/low temp.

### 2.2 State B: Saved Sample (`is_sample === true`)
- **Border & Header**: `1px solid #F59E0B` (Amber hairline), Top right badge: Clock icon + `"Saved Weather Sample"` (`#FEF3C7` / `#78350F`).
- **Mandatory Banner inside Card**:
  - If `expired === true`: *"Reference sample from Sep 1–8, 2025 (Expired). Not a live forecast."*
  - If `expired === false`: *"Saved weather sample valid for stated dates."*
- **Content**: Displays the 4 metric tiles in slightly muted slate tones (`#475569`) so it feels clearly distinct from live telemetry.

### 2.3 State C: Unavailable Weather (`status === "unavailable"`)
- **Border & Header**: `1px dashed #CBD5E1`, background `#F8FAFC`, badge: `"Weather Unavailable"` (`#F1F5F9` / `#475569`).
- **Content**:
  - Cloud-off SVG icon.
  - Message: *"Live weather data is currently unavailable. Crop rotation options remain valid using long-term NASA POWER climate baselines (2015–2025)."*
  - Zero fabricated numbers or placeholder zeros (`0°C`) shown.

---

## 3. Map Experience (`<FieldMap />`)

### 3.1 Map Placement & Container Sizing
- **Wizard Step 1**: Full-width interactive picker (`height: 320px` mobile, `380px` desktop).
- **Farmer Results Page**: Paired beside Weather Card on desktop (`55%` width, `height: 380px`); full-width stacked below Weather on mobile (`height: 300px`).
- **Expert Analysis Detail**: Top of Left Evidence Column (`height: 360px` desktop, `280px` mobile).

### 3.2 Layer Controls & Legends
- **Overlay Toggles**: Segmented pill bar floating or docked cleanly above the map:
  - `None (Base Map)` | `NDVI (Vegetation)` | `NDMI (Moisture)` | `BSI (Bare Soil)` | `Slope (Terrain)`
- **Dynamic Legend Strip**:
  - Docked at the bottom of the map (`background: rgba(255, 255, 255, 0.94)`, `backdrop-filter: blur(4px)`).
  - Displays: Gradient color bar matching the selected PNG layer + Min/Max labels (e.g., `NDVI: -0.20 (Bare) ── 0.88 (Dense)`), plus source tag (`"Landsat 9 • 30m • 2025-09-30"`).
- **Zoom & GPS Controls**:
  - Standard `+` / `-` zoom buttons (`44x44px` touch targets) + `"Recenter on Hyderabad Pilot"` button.
- **Expert Mode Differences**:
  - Adds **Layer Opacity Slider** (`20% – 100%`).
  - Renders the `150m` circular zonal sampling radius ring around the matched pilot point (`hyd_XXX`).
  - Clicking a point opens a crisp coordinate & spectral readout popover.

---

## 4. Confidence Meter (`<ConfidenceMeter />`)
- **Visual**: 3 circular indicator dots (`10px` diameter, `4px` gap) + adjacent text label.
  - **1 Dot**: `#DC2626` (Low — Data gaps or multiple unverified constraints)
  - **2 Dots**: `#D97706` (Moderate — Capped by unverified salinity/waterlogging rule)
  - **3 Dots**: `#16A34A` (High — Verified rules & complete local features)
- **Accessibility**: Always paired with `<span class="sr-only">Confidence: 2 out of 3 dots</span>` and visible text (`"Moderate Confidence"`).
