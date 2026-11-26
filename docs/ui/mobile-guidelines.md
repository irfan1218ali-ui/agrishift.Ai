# AgriShift AI — Mobile-First & Responsive Breakpoint Guidelines

## 1. Breakpoint System & Target Viewports

AgriShift AI uses a strict **mobile-first CSS architecture**, starting from `320px` upward:

| Tier Name | Viewport Width | Target Devices | Container Max-Width | Grid Columns |
| :--- | :--- | :--- | :--- | :--- |
| **Base (XS)** | `320px – 359px` | iPhone SE (1st gen), entry Androids | `100%` (`12px` side padding) | `1-col` (2-col max for compact crop tiles) |
| **Small (SM)** | `360px – 389px` | Standard budget/mid Android phones | `100%` (`16px` side padding) | `1-col` cards / `2-col` crop grid |
| **Medium-Mobile (MM)** | `390px – 767px` | iPhone 13/14/15, modern Android | `100%` (`16px` side padding) | `1-col` cards / `3-col` crop grid |
| **Tablet (MD)** | `768px – 1023px` | iPad Portrait, large foldables | `720px` centered | `2-col` grid / `3-col` wizard tiles |
| **Desktop (LG/XL)** | `1024px – 1366px+`| Laptops, Agronomist workstations | `1200px` centered (`24px` pad) | `3-col` recommendation grid, `65%/35%` Expert split |

---

## 2. Exact Rules Per Viewport Width

### 2.1 `320px` (Ultra-Compact Constraint Rules)
- **Zero Horizontal Overflow**: `html, body { overflow-x: hidden; }` and `max-width: 100vw`. No element may exceed `296px` inner width.
- **Crop Selection Grid**: Drops from 3 columns to **2 columns** (`grid-template-columns: repeat(2, 1fr); gap: 8px;`) so crop labels in Urdu/Sindhi never truncate awkwardly.
- **Top Navbar**: Brand wordmark shortens or pairs compact `24px` logo + compact language dropdown (`EN ▾` instead of 3 wide pill buttons).
- **Sticky Action Bar**: Wizard Next/Back buttons stack or share a `40% / 60%` split (`min-height: 44px`).

### 2.2 `360px` & `390px` (Standard Mobile Field Usage)
- **One-Handed Thumb Zone**: Primary Wizard CTA (`"Continue"`) pins cleanly to the bottom of the screen or sits immediately after content with `48px` height.
- **Map Interactions**: Map height locked at `300px–320px` (`42vh`) so the user can always scroll past the map without getting trapped in map pan gestures (require 2-finger pan or provide a clear scroll handle outside the map container).

### 2.3 `768px` (Tablet Breakpoint)
- **Landing Page**: Hero stays vertical or transitions to compact split; Data Sources Grid switches to `2x3`.
- **Results Page**: Environmental Summary Strip becomes 3-column; Recommendation Cards remain `1-col` horizontal cards (Crop transition left, explanation right) or `2+1` grid.

### 2.4 `1366px` (Desktop Workspace)
- **Farmer Results**: 3 Rotation Recommendation Cards render in a symmetric **3-column equal-height grid**.
- **Weather + Map**: Side-by-side (`45%` Weather / `55%` Map).
- **Expert Portal**: Two-column evidence layout (`65%` Main Evidence Column / `35%` Sticky Expert Notes & Review Rail).

---

## 3. Component-Specific Responsive Behaviors

### 3.1 Navigation & Menus
- **Desktop (`>= 768px`)**: Inline top bar displaying Logo, inline Language Switcher (`EN | اردو | سنڌي`), `"Expert Portal"` link.
- **Mobile (`< 768px`)**: Compact top bar (`56px` height) with Logo, compact Language Switcher pill, and a single menu icon (`44x44px`) opening a slide-over drawer for `"Open Saved Analysis"`, `"Known Limitations"`, and `"Expert Portal"`.

### 3.2 Drawers & Bottom Sheets
- **Mobile (`< 768px`)**: Secondary technical panels (e.g., Layer Legends or "Enter Coordinates Manually") use a **bottom sheet / accordion** (`border-radius: 20px 20px 0 0`) with a visible drag/close button (`44x44px`).
- **Desktop (`>= 768px`)**: Render as inline cards or side drawers (`width: 400px`).

### 3.3 Tables (Comparison Matrix & Expert Analyses Table)
- **Desktop (`>= 768px`)**: Full structured HTML `<table>` with sticky header and tabular numerals.
- **Mobile (`< 768px`)**:
  - **Farmer Comparison Table**: Transforms into **Tabbed / Swipeable Comparison Cards** OR a clean horizontally scrollable container with a frozen first column (`Metric` sticky left/start) and subtle scroll-shadow hint.
  - **Expert Analyses Queue**: Converts each table row into a **Structured Mobile List Card** (ID + Date on line 1, Crop + Salinity badge on line 2, `"Inspect →"` button on bottom).

### 3.4 Charts (Expert Portal Climate & K-Means Charts)
- **Responsive Container**: `width: 100%`, aspect ratio `16:9` on desktop, `4:3` on mobile (`min-height: 220px`).
- **Mobile Chart Simplification**: On `< 640px`, rotate X-axis month labels (`Jan..Dec` $\rightarrow$ `J, F, M...` or `45°` tilt), reduce tick count to 4–5 intervals, and replace hover-only tooltips with tap-to-inspect active point tooltips.
