# AgriShift AI — Design System Specification

## 1. Visual Philosophy & Aesthetic Direction
AgriShift AI transitions from a prototype layout to a **modern Agricultural SaaS platform** suitable for a university final-year engineering product.
- **Visual Tone**: Calm, authoritative, trustworthy, data-transparent, and field-accessible.
- **Core Principles**:
  1. **No Raw Prototype Borders**: Replace heavy `3px` solid borders and neon yellow outlines with `1px` subtle hairline borders (`#E2E8F0`), soft elevation shadows, and clear surface contrast.
  2. **Crisp Vector Iconography**: Replace raw OS emojis (`🌾`, `💧`) in primary controls with consistent `1.75px` stroke SVG icons (e.g., Lucide Icons).
  3. **Scientific Honesty First**: Real vs. Demo modes, forecast expiry, and confidence caps are visually unmistakable without looking alarmist.

---

## 2. Color Tokens

### 2.1 Semantic Color Roles

| Role | Token Name | Hex | Usage | Contrast Target |
| :--- | :--- | :--- | :--- | :--- |
| **Primary (Brand)** | `--color-primary-700` | `#15803D` | Primary CTAs, active wizard steps, brand header accent | $\ge 4.5:1$ with `#FFFFFF` |
| **Primary Hover** | `--color-primary-800` | `#166534` | Button hover/pressed states, deep botanical headers | $\ge 7.0:1$ with `#FFFFFF` |
| **Primary Tint** | `--color-primary-50` | `#F0FDF4` | Selected option card background, subtle positive surface | Dark text `#14532D` |
| **Success** | `--color-success-600` | `#16A34A` | High confidence indicators, live weather badge, balanced fit | $\ge 4.5:1$ on `#FFFFFF` |
| **Success Surface** | `--color-success-50` | `#DCFCE7` | Success pill/chip background | Text `#14532D` |
| **Warning** | `--color-warning-600` | `#D97706` | Unverified agronomic rule caution, sample/expired weather, medium risk | $\ge 4.5:1$ with `#FFF` or `#78350F` on tint |
| **Warning Surface** | `--color-warning-50` | `#FEF3C7` | Caution callouts, demo mode alert bar | Border `#F59E0B`, text `#78350F` |
| **Risk / Danger** | `--color-risk-600` | `#DC2626` | High agronomic constraint conflict, validation errors, unavailable critical data | $\ge 4.5:1$ on `#FFFFFF` |
| **Risk Surface** | `--color-risk-50` | `#FEE2E2` | Error banners, high waterlogging/salinity conflict badges | Border `#EF4444`, text `#7F1D1D` |
| **Info** | `--color-info-600` | `#0284C7` | Regional hydrological context (SMAP/GPM), NASA metadata tooltips | $\ge 4.5:1$ on `#FFFFFF` |
| **Info Surface** | `--color-info-50` | `#E0F2FE` | Regional context cards, environmental cluster info badges | Border `#38BDF8`, text `#0C4A6E` |
| **Neutral Text Primary**| `--color-neutral-900` | `#0F172A` | Primary headings, body copy, data values | $\ge 15:1$ on `#FFFFFF` |
| **Neutral Text Muted** | `--color-neutral-600` | `#475569` | Subtitles, metadata labels, helper text, timestamps | $\ge 7.0:1$ on `#FFFFFF` |
| **Neutral Border** | `--color-neutral-200` | `#E2E8F0` | Card borders, table dividers, input outlines | Subtle structural separation |
| **Neutral Surface** | `--color-neutral-50` | `#F8FAFC` | Page canvas background, secondary table header fill | Clean SaaS canvas |
| **Elevated Surface** | `--color-surface-white` | `#FFFFFF` | Cards, modals, drawers, wizard containers | Elevated above `#F8FAFC` |

### 2.2 Cluster Neutral Color Coding
Clusters represent **environmental patterns**, never crop health. Avoid red/green good/bad metaphors for K-Means clusters:
- **Cluster 0 (Relatively vegetated)**: `#0D9488` (Teal 600) on `#F0FDFA`
- **Cluster 1 (Intermediate condition)**: `#64748B` (Slate 500) on `#F8FAFC`
- **Cluster 2 (Higher bare/thermal exposure)**: `#B45309` (Amber 700) on `#FFFBEB`

---

## 3. Typography

### 3.1 Font Families
- **English / Numeric Data (`ltr`)**: `"Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif`
- **Urdu / Sindhi (`rtl`)**: `"Noto Naskh Arabic", "Noto Nastaliq Urdu", system-ui, sans-serif`
- **Monospace (Analysis IDs, Coordinates, Scene IDs)**: `"JetBrains Mono", "Fira Code", ui-monospace, monospace`

### 3.2 Type Scale (Mobile-First Base: `16px`)
*Note: The current `20px` base caused cramped mobile cards. Standardizing on `16px` (`1rem`) with generous line-height preserves readability while allowing SaaS-grade information density.*

| Token | Size (Mobile / Desktop) | Weight | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- |
| `text-display` | `28px` / `40px` | `700` | `1.2` | Landing hero headline |
| `text-h1` | `22px` / `28px` | `700` | `1.25` | Page & Wizard step titles |
| `text-h2` | `18px` / `22px` | `600` | `1.3` | Section headers (Results, Expert Evidence) |
| `text-h3` | `16px` / `18px` | `600` | `1.35` | Card titles (Rotation Option, Weather) |
| `text-body` | `15px` / `16px` | `400` | `1.5` (LTR) / `1.7` (RTL) | Standard descriptions, explanations |
| `text-sm` | `13px` / `14px` | `500` | `1.4` | Secondary metadata, table cells, chips |
| `text-xs` | `12px` / `12px` | `500` | `1.35` | Source resolution tags, timestamps, footnotes |

---

## 4. Spacing, Radii & Elevation

### 4.1 4px / 8px Spacing Scale
- `space-1`: `4px` (inline icon gap, tight chip padding)
- `space-2`: `8px` (gap between related badges, label-to-input)
- `space-3`: `12px` (internal card compact padding, mobile stack gap)
- `space-4`: `16px` (standard card padding on mobile, grid gutter)
- `space-6`: `24px` (desktop card padding, section vertical gap)
- `space-8`: `32px` (major page section separation)
- `space-12`: `48px` (landing page vertical rhythm)

### 4.2 Border Radii
- `radius-sm`: `6px` (badges, small inputs, table tags)
- `radius-md`: `10px` (buttons, standard form inputs, map controls)
- `radius-lg`: `14px` (standard cards, alerts, wizard step containers)
- `radius-xl`: `20px` (hero containers, bottom-sheet drawers on mobile)
- `radius-full`: `9999px` (pills, status dots, avatar/step circles)

### 4.3 Elevation (Shadows)
- `shadow-xs`: `0 1px 2px 0 rgba(15, 23, 42, 0.05)` (subtle buttons, inputs)
- `shadow-sm`: `0 1px 3px 0 rgba(15, 23, 42, 0.08), 0 1px 2px -1px rgba(15, 23, 42, 0.04)` (default SaaS cards)
- `shadow-md`: `0 4px 6px -1px rgba(15, 23, 42, 0.08), 0 2px 4px -2px rgba(15, 23, 42, 0.04)` (hover cards, floating map legend)
- `shadow-lg`: `0 10px 15px -3px rgba(15, 23, 42, 0.1), 0 4px 6px -4px rgba(15, 23, 42, 0.05)` (modals, drawers, dropdowns)

---

## 5. Core UI Primitives

### 5.1 Buttons
- **Minimum Touch Target**: `min-height: 44px` (`48px` for primary farmer wizard CTAs).
- **Variants**:
  - **Primary**: Background `#15803D`, text `#FFFFFF`, hover `#166534`, border `none`, `radius-md`.
  - **Secondary**: Background `#FFFFFF`, text `#0F172A`, border `1px solid #CBD5E1`, hover `#F8FAFC`.
  - **Ghost / Subtle**: Background `transparent`, text `#475569`, hover `#F1F5F9`.
  - **WhatsApp Action**: Background `#16A34A`, text `#FFFFFF`, leading WhatsApp SVG icon.
  - **Disabled State**: `opacity: 0.5`, `cursor: not-allowed`, no hover elevation.
- **Focus Ring**: `outline: 2px solid #15803D; outline-offset: 2px;` on `:focus-visible`.

### 5.2 Inputs & Selection Controls
- **Text / Number / Select**: Height `44px`, padding `0 12px`, `1px solid #CBD5E1`, background `#FFFFFF`, `radius-md`. Error state: `1.5px solid #DC2626` with `#FEF2F2` background tint and inline helper message below.
- **Selectable Option Tiles (Crop, Water, Priority)**:
  - Surface `#FFFFFF`, border `1px solid #E2E8F0`, `radius-lg`, padding `12px 16px`.
  - **Selected State**: Border `2px solid #15803D`, background `#F0FDF4`, subtle top-end checkmark badge `#15803D`. (No thick yellow outlines).

### 5.3 Cards
- Standard SaaS Card: Background `#FFFFFF`, border `1px solid #E2E8F0`, `radius-lg`, `shadow-sm`, padding `16px` (mobile) / `24px` (desktop).
- Emphasized Card (Recommended Option): Top accent bar (`4px solid #15803D`) or subtle `#F0FDF4` header strip, never a loud neon border.

### 5.4 Badges & Chips
- Compact pills (`height: 24px`, `padding: 0 10px`, `font-size: 12px`, `font-weight: 600`, `radius-full`).
- **Always pair icon + text label** (never rely on color alone).

### 5.5 Tables
- Header background `#F8FAFC`, text `#475569`, uppercase or semibold `12px`–`13px`.
- Row dividers `1px solid #E2E8F0`, row padding `12px 16px`, alternating subtle hover `#F8FAFC`.
- Numeric columns use `font-variant-numeric: tabular-nums`.

### 5.6 Charts (Expert Portal)
- Clean gridlines (`#E2E8F0` dashed), zero 3D effects, crisp tooltips (`#0F172A` background, `#FFFFFF` text).
- Color palette for multi-series: Primary Green `#15803D`, Info Blue `#0284C7`, Teal `#0D9488`, Amber `#D97706`.

### 5.7 Icons
- Standard library: **Lucide Icons** (`20px` default, `16px` inline badges, `24px` card headers).
- Directional icons (arrows, chevrons) must mirror automatically in RTL (`urdu`, `sindhi`) using CSS logical transforms (`rtl:rotate-180`).
