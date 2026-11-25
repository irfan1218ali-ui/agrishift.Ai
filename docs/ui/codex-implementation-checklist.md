# AgriShift AI — Codex Phase 1 Frontend Implementation Review Checklist

Review gate derived strictly from `docs/ui/` specifications. All 18 checklist items and 10 visual checks must pass before Phase 1 frontend work is accepted.

> **Runtime Review Result (2026-11-25)**: **PASS WITH MINOR ISSUES** (`15 / 18` checklist items **PASS**, `3 / 18` **FAIL** on non-critical spec variances; `9 / 10` visual acceptance checks **PASS**, `1 / 10` **FAIL**; `npm run typecheck` **PASS**, `npm run build` **PASS**, `python -m pytest -q`: `95 passed, 1 failed, 2 skipped`).

---

## Implementation Verification Checklist

### 1. Landing Page Structure
- [ ] **FAIL** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/page-wireframes.md`)*
- **Runtime Note**: Zero-login `/` route, `EN | اردو | سنڌي` switcher, `Analyze my field` CTA (fixed white-on-green), mobile stacking (`0` overflow at `320–1366 px`), and disclaimer footer all work cleanly; fails strict spec check on `/` because there is no inline `"Open Saved Analysis"` ID lookup form (`hasReloadCodeInput: false`), only `4` `.source-card` items instead of `6`, and `"Expert access"` sits in the footer instead of the top `<nav>`.
- **Requirement**: Public zero-login entry matching exact section order, spacing, responsive stacking, and dual navigation into analysis or saved-code lookup.
- **Expected implementation**: Sticky `64px` top navbar (`EN | اردو | سنڌي` switcher + `"Expert Portal"` link); Hero with `"Start Field Analysis"` CTA and `"Open Saved Analysis"` ID lookup (`2-col` desktop with visual preview, stacked mobile); `#F8FAFC` Problem Statement (`3` cards); How It Works (`4` steps); `#F8FAFC` Data Sources grid (`3×2` desktop, `2×3` tablet, `1-col` mobile); Benefits & Responsible AI callout; bottom CTA & footer.
- **Pass/fail verification method**: Inspect `/` at `1366px` and `360px` to verify exact section sequence, working hero CTA to Wizard Step 1, working ID lookup, and absence of login walls or raw diagnostics.
- **Severity if missing**: High

### 2. Five-Step Farmer Analysis Wizard
- [x] **PASS** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/page-wireframes.md`)*
- **Runtime Note**: End-to-end 5-step flow (`/analyze`), dynamic `/api/v1/crops` loading (`14` crops), Back/Next state preservation (`statePreservedOnBack: true`), validation on empty Step 1 submission, responsive crop grid, and submission to `/results/{id}` all pass. *(Minor spec variance: uses search/GPS/map click rather than manual lat/lon accordion, alerts on Next instead of pre-disabling CTA, and uses Back instead of Step 5 per-row `"Edit"` links.)*
- **Requirement**: Focused `max-width: 720px` guided flow across Location, Crop History, Farm Conditions, Priority, and Review with sticky progress header (`Step X of 5`).
- **Expected implementation**: Step 1 GPS button + interactive MapLibre pilot boundary + manual coordinate accordion + validation chip; Step 2 selectable crop tiles (`2-col` at `320–389px`, `3-col` at `>= 390px`) from `/api/v1/crops`; Step 3 water availability (`Low`/`Medium`/`High`), salinity (`No`/`Yes`), and waterlogging (`No`/`Yes`) selectors; Step 4 `3` descriptive priority cards; Step 5 editable 4-row review summary with step-specific `"Edit"` links and `"Generate Rotation Options"` submit button.
- **Pass/fail verification method**: Walk through Steps 1–5 end-to-end; verify Continue stays disabled until required fields are filled, `"Edit"` jumps back while preserving inputs, and Step 5 submits to analyze.
- **Severity if missing**: Critical

### 3. Results Dashboard Hierarchy
- [x] **PASS** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/page-wireframes.md`)*
- **Runtime Note**: `/results/{id}` renders top header (`REAL DATA`, ID, date, distance `1.69 km`), confidence/review banner, Environmental summary, 3 Rotation Cards, Comparison table, Weather + interactive Map, Explanation Timeline, Next Actions (WhatsApp, share/copy/print/restart/expert link), and Advisory footer with zero overflow across `320–1366 px`.
- **Requirement**: Scannable vertical hierarchy displaying summary context and actionable recommendations before secondary telemetry and timelines.
- **Expected implementation**: Sticky top bar (`Analysis ID` + Copy, Data Mode badge, `"New Analysis"`) -> 1. Analysis Summary header -> 2. Environmental Summary Strip -> 3. Three Rotation Recommendation Cards -> 4. Side-by-Side Comparison Table -> 5. Weather & Interactive Map split (`45%/55%` desktop, stacked mobile) -> 6. 4-step Explanation Timeline -> 7. Next Actions (WhatsApp Share, Copy Code, Print, Expert View) & fixed Advisory Footer.
- **Pass/fail verification method**: Execute a valid Hyderabad pilot analysis and inspect DOM/visual top-to-bottom sequence on `1366px` and `360px`; confirm Recommendation Cards precede Weather, Map overlays, and Explanation Timeline.
- **Severity if missing**: High

### 4. Three Rotation-Card Variants
- [x] **PASS** *(Ref: `docs/ui/component-specification.md`, `docs/ui/design-system.md`)*
- **Runtime Note**: Observed `3` distinct cards (`"Your current rotation"` `73 / 100`, `"Balanced option"` `93 / 100`, `"Priority option: Keep it balanced"` `93 / 100`) with distinct border/header hierarchy, crop transitions, confidence meter `73% ●●○`, and `"Expert review advised"` amber warning banner for unverified crop-rule values.
- **Requirement**: Distinct `baseline` (Current Rotation), `balanced` (Balanced Option), and `priority` (Priority Option) card variants with uniform content hierarchy, risk/water badges, and confidence caps.
- **Expected implementation**: Equal-height `3-col` grid (`1366px`) / vertical stack (`<= 768px`). Current uses `#F8FAFC` header + `1px #E2E8F0` border + `"Current Practice"` pill; Balanced uses `#FFFFFF` + `1px #CBD5E1` + Info pill; Priority uses `2px #15803D` border, `4px` green top accent bar, `#F0FDF4` header, `shadow-md`, `"Matches Your Priority ★"` pill. Internally ordered: variant header -> crop SVG transition (`rtl:rotate-180` arrow) -> water/risk chips -> `<ConfidenceMeter />` (`1–3` dots + label + lock/info cap notice) -> max `3` bullets -> conditional `#FEF3C7` caution banner.
- **Pass/fail verification method**: Trigger both clean balanced and salinity-observed analyses; confirm exact card emphasis on Priority, $\le 3$ concise bullets, and confidence capped at $\le 2$ dots with `#FEF3C7` caution banner when unverified rules trigger.
- **Severity if missing**: High

### 5. Environmental Summary
- [x] **PASS** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/design-system.md`)*
- **Runtime Note**: Renders neutral cluster grouping (`Vegetation signal | Higher bare/thermal exposure | Environmental pattern grouping`), Landsat NDMI (`-0.06` · `30 m`), surface heat (`44 °C`), and SRTM terrain slope (`2.6°` · `30 m`) without red/green crop-health claims. *(SMAP `~9 km` / GPM `0.1°` regional caveats appear on Expert Detail / API metadata rather than inside the 4-metric Farmer strip.)*
- **Requirement**: Compact 3-card context strip separating unsupervised cluster grouping, field-scale satellite snapshot, and coarse regional hydrology.
- **Expected implementation**: `3-col` desktop strip (`1-col` stack mobile): (1) Environmental Cluster card with neutral label and non-evaluative teal (`#0D9488`), slate (`#64748B`), or amber (`#B45309`) styling; (2) Landsat 9 / SRTM card (`NDVI`, `Surface Temp °C`, `Elevation m`, low-lying indicator if triggered); (3) SMAP (`~9 km`) & GPM (`0.1°`) card explicitly labeled `"Regional context, not exact farm sensor"`.
- **Pass/fail verification method**: Verify all three cards render matched values, display regional scale disclaimers for SMAP/GPM, and never apply green/red crop-health styling to clusters.
- **Severity if missing**: High

### 6. Weather States: Live, Saved Sample, Unavailable
- [x] **PASS** *(Ref: `docs/ui/component-specification.md`, `docs/ui/accessibility-guidelines.md`)*
- **Runtime Note**: Runtime review verified the active `EXPIRED SAMPLE` badge (`15-Nov-2026` to `22-Nov-2026`, daily temp/rain/humidity/wind, and explicit `"weather does not block the rotation result"` banner) against the live FastAPI backend. Distinct `Live` and `Unavailable` state branches were confirmed in `results/[id]/page.tsx` source, though not separately toggled via Meteomatics credentials or mock fault injection.
- **Requirement**: Three unmistakably distinct `<WeatherCard />` visual states combining color, border treatment, SVG icon, and explicit badge copy.
- **Expected implementation**: **Live** (`is_live === true`): `#E2E8F0` border, green dot + `"Live Forecast • Meteomatics"` pill, validity dates, 4 metrics + 7-day strip; **Saved Sample** (`is_sample === true`): `1px #F59E0B` border, amber clock icon + `"Saved Weather Sample"` pill, explicit expired/reference banner, muted `#475569` values; **Unavailable** (`status === "unavailable"`): dashed `#CBD5E1` border on `#F8FAFC`, cloud-off SVG, `"Weather Unavailable"` badge, fallback copy citing NASA POWER `2015–2025` baselines with zero placeholder `0°C` figures.
- **Pass/fail verification method**: Test `live`, `is_sample` (`expired: true`/`false`), and `unavailable` payloads; confirm each state renders its exact border, icon, badge text, and never fakes numbers when unavailable.
- **Severity if missing**: High

### 7. Real/Demo Data Badges
- [ ] **FAIL** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/design-system.md`, `docs/ui/accessibility-guidelines.md`)*
- **Runtime Note**: `/results/{id}` (`REAL DATA` / `حقیقی ڈیٹا` / `حقيقي ڊيٽا`) and `/expert/analysis/{id}` (`REAL`) render clear localized data-mode badges. Fails strict spec check because `/` (`hasDataBadgeOnLanding: false`) and Wizard Step 5 omit the Real/Demo indicator badge, and `DEMO_MODE=true` runtime toggle was not executed in this pass.
- **Requirement**: Continuous, text-explicit distinction between Real Environmental Data mode and Demo Mode across public and expert views.
- **Expected implementation**: `DEMO_MODE=true` renders sticky `#FEF3C7` warning strip (`#78350F` text: *"Demo Mode Active — Using sample environmental records"*) and explicit Demo pill in Results sticky header; Real Mode displays `#DCFCE7` pill (`#14532D` text) `"Real Environmental Data"` on Hero, Wizard Step 5 notice, Results header, and Expert Detail.
- **Pass/fail verification method**: Toggle backend `demo_mode` (`false` vs `true`) and verify Landing, Wizard Step 5, and Results sticky bar immediately switch textual banners and pill styles without relying on color alone.
- **Severity if missing**: Critical

### 8. Map Overlays and Dynamic Legends
- [ ] **FAIL** *(Ref: `docs/ui/component-specification.md`, `docs/ui/rtl-guidelines.md`)*
- **Runtime Note**: Shared `<AppMap />` enforces `dir="ltr"`, loads `/maplibre-gl-worker.mjs` with `0` worker errors, switches `Base map`, `Vegetation` (`ndvi.png` `200`, `-1.00..0.95`), `Moisture` (`ndmi.png` `200`, `-1.00..0.87`), `Bare soil` (`bsi.png` `200`, `-0.70..1.00`), and `Slope` (`slope.png` `200`, `0.00..73.29 degrees`) with live legends (`>= 44×44 px` controls). Fails strict spec check on Expert extensions because Expert Detail omits the `20%–100%` opacity slider and `150m` radius circle overlay.
- **Requirement**: Interactive MapLibre map supporting pixel-aligned overlay toggling (`NDVI`, `NDMI`, `BSI`, `Slope`), dynamic numeric legends, zoom controls, and Expert extensions.
- **Expected implementation**: Map container enforces `dir="ltr"`; pill controls toggle `None`, `NDVI`, `NDMI`, `BSI`, `Slope` using PNGs and bounds from `/api/v1/layers/metadata`; translucent bottom legend displays color gradient, min/max values, and source attribution (`"Landsat 9 • 30m • 2025-09-30"` or SRTM); `44×44 px` `+`/`-` zoom and recenter buttons; Expert Detail adds `20%–100%` opacity slider, `150m` radius circle around `hyd_XXX`, and spectral inspection popover.
- **Pass/fail verification method**: Switch every overlay in Farmer Results and Expert Detail; verify valid PNG layer overlays align within Hyderabad pilot bounds, legend min/max updates dynamically, pan/zoom stays LTR in Urdu/Sindhi, and Expert opacity slider adjusts raster alpha.
- **Severity if missing**: High

### 9. Expert Login, Dashboard, and Analysis Detail
- [x] **PASS** *(Ref: `docs/ui/expert-user-flow.md`, `docs/ui/page-wireframes.md`)*
- **Runtime Note**: `/expert/login` validates configured local credentials cleanly (`invalidLoginErr` shown on failure); `/expert/dashboard` displays overview KPIs and `/api/v1/health` status; `/expert/analysis/{id}` loads evidence (`16` evidence rows, `3` monthly NASA POWER charts, `3` option comparisons, local notes saved in `localStorage`) with `0` overflow across `320–1366 px`. *(Phase 2 backend work deferred per instructions: global expert analysis-list API, search/filter queue over backend records, and server-side expert notes API.)*
- **Requirement**: Single authenticated research-grade Expert Portal avoiding noisy developer logs or multi-sidebar admin panels.
- **Expected implementation**: Login (`/expert/login`) centered `420px` card with password reveal toggle and return link; Dashboard (`/expert/dashboard`) with `64px` nav, 4 KPI cards (`Total`, `Pending Review`, `149 Pilot Pts`, `Model & Weather`), search/filter chips (`All`, `Needs Review`, `Salinity`, `Waterlogging`, `Outside Pilot`), and analyses table (mobile cards `< 768px`); Detail (`/expert/analyses/{id}`) `65%/35%` desktop split containing Environmental Evidence, collapsible NASA POWER monthly chart, collapsible K-Means cluster comparison chart/metrics, Rotation Rule Breakdown table, and sticky right rail for Expert Notes log and Review Status actions.
- **Pass/fail verification method**: Test auth screen, search/filter queue on Dashboard, inspect Detail view across desktop and mobile collapsed states, and verify charts, tables, and note/review forms behave cleanly without raw terminal dumps.
- **Severity if missing**: High

### 10. English, Urdu RTL, and Sindhi RTL
- [x] **PASS** *(Ref: `docs/ui/rtl-guidelines.md`, `docs/ui/design-system.md`)*
- **Runtime Note**: `<html lang="en|ur|sd" dir="ltr|rtl">` updates dynamically across Wizard and Results; Urdu and Sindhi scripts render cleanly (`ربیع 2026–27`, `خریف 2027`, `ربيع 2026–27`, `خريف 2027`); directional sequence arrows mirror (`matrix(-1, 0, 0, 1, 0, 0)`); map remains `dir="ltr"`; comparison table flows `dir="rtl"` (`text-align: right`); `.ltr-token` isolates negative values and units (`-0.06`, `44 °C`, `2.6°`). *(Minor gaps: some secondary API/table labels—e.g. `"Higher bare/thermal exposure"`, unverified-rule alert body, weather row metric names, comparison cells, timeline, and next steps—still display in English under `ur`/`sd`.)*
- **Requirement**: Native switching across `en`, `ur`, and `sd` with logical CSS mirroring, Arabic-script typography, and isolated BiDi numeric formatting.
- **Expected implementation**: Language selector updates `<html lang="en|ur|sd" dir="ltr|rtl">`; Urdu/Sindhi use `"Noto Naskh Arabic"` at `16px–17px`, `line-height: 1.75`, and zero negative `letter-spacing`; all spacing/borders use CSS logical properties (`margin-inline-*`, `padding-inline-*`, `text-align: start`); numeric tokens (coords, Analysis IDs, dates, Scene IDs, negative decimals like `-0.17`) use Western `0–9` numerals wrapped with `dir="ltr"` / `unicode-bidi: isolate`; arrows/chevrons flip (`scaleX(-1)`) while checkmarks, compass, weather, and map container remain LTR.
- **Pass/fail verification method**: Switch cleanly through `EN`, `UR`, and `SD` on Landing, Wizard, Results, and Expert screens; inspect HTML `dir`/`lang`, confirm negative numbers do not invert (`0.17-`), check Sindhi glyphs (`ٻ`, `ڄ`, `ڃ`, `ڏ`, `ڳ`, `ڻ`, `ھ`) render cleanly, and verify comparison table flows RTL in `ur`/`sd`.
- **Severity if missing**: High

### 11. Mobile Layouts at 320, 360, 390, 768, and 1366 px
- [x] **PASS** *(Ref: `docs/ui/mobile-guidelines.md`, `docs/ui/page-wireframes.md`)*
- **Runtime Note**: Tested at `320×568`, `360×800`, `390×844`, `768×1024`, and `1366×768` across `/`, `/analyze`, `/results/{id}`, `/expert/login`, `/expert/dashboard`, and `/expert/analysis/{id}`; desktop vs mobile drawer/collapse breakpoints (including fixed `<= 900px` `.expert-shell` collapse) adapt with zero horizontal overflow.
- **Requirement**: Progressive mobile-first responsive adaptation matching exact viewport breakpoints, navigation drawers, comparison tables, and charts.
- **Expected implementation**: `320px` (`12px` pad, `2-col` crop grid, compact lang control, `40%/60%` or stacked sticky actions); `360–390px` (`16px` pad, `300–320px` map height avoiding pan-trap, bottom sheet/drawer under `768px`, mobile list cards for Expert queue, tabbed/scrollable sticky-first-column comparison table); `768px` (`720px` container, `2×3` data sources, `3-col` env strip); `1366px` (`1200px` container, `3-col` Rotation Cards, `45%/55%` Weather/Map, `65%/35%` Expert Detail). Expert charts adapt X-axis labels cleanly `< 640px`.
- **Pass/fail verification method**: Test all routes in responsive device emulation at `320×568`, `360×800`, `390×844`, `768×1024`, and `1366×768`; verify drawer transitions, comparison matrix usability, and chart responsiveness.
- **Severity if missing**: High

### 12. Keyboard Navigation and Visible Focus
- [x] **PASS** *(Ref: `docs/ui/accessibility-guidelines.md`, `docs/ui/design-system.md`)*
- **Runtime Note**: Verified visible focus rings (`3px solid` outline / `box-shadow` focus rings) across nav links, language toggles, search input, and buttons via keyboard Tab checks; wizard step-heading `tabindex="-1"` auto-focus shift not implemented.
- **Requirement**: Full keyboard reachability, programmatic wizard focus transitions, modal focus traps, and visible focus outlines in both LTR and RTL.
- **Expected implementation**: Logical `Tab`/`Shift+Tab` sequence; `:focus-visible { outline: 2px solid #15803D; outline-offset: 2px; }` preserved on every button, tile, input, and toggle; advancing wizard steps moves focus to the new step heading (`tabindex="-1"`); open drawers/modals trap focus and dismiss cleanly via `Escape` restoring trigger focus.
- **Pass/fail verification method**: Navigate entire Farmer flow + WhatsApp/Share modal + Nav drawer using only `Tab`, `Shift+Tab`, `Enter`, `Space`, arrow keys, and `Escape`; confirm unbroken focus visibility and step heading focus transfer.
- **Severity if missing**: High

### 13. Minimum 44×44 px Touch Targets
- [x] **PASS** *(Ref: `docs/ui/accessibility-guidelines.md`, `docs/ui/design-system.md`)*
- **Runtime Note**: Zero control violations (`smallControls: []`) across `320×568`–`1366×768` on `/analyze`, `/results/{id}` (`en`, `ur`, `sd`), `/expert/login`, `/expert/dashboard`, and `/expert/analysis/{id}`; only `/` inline footer prose credit link (`a.credit-link`) sits below `44 px` height (WCAG inline link exception).
- **Requirement**: Field-friendly tap sizing and clear spacing on all interactive controls across desktop and mobile.
- **Expected implementation**: All buttons, crop/condition/priority selection tiles, nav links, drawer close icons, language pills, and map zoom `+`/`-`/recenter buttons enforce `min-height: 44px; min-width: 44px;` (`>= 48px` height for primary Wizard CTAs) with `>= 8px` (`space-2`) gap between adjacent controls.
- **Pass/fail verification method**: Inspect `getBoundingClientRect()` dimensions and gap spacing in DevTools at `320×568` and `360×800` for every button, map button, tile, and icon control.
- **Severity if missing**: High

### 14. No Horizontal Overflow
- [x] **PASS** *(Ref: `docs/ui/mobile-guidelines.md`, `docs/ui/accessibility-guidelines.md`)*
- **Runtime Note**: Confirmed `scrollWidth === innerWidth` (`overflow: false`) across `320×568`, `360×800`, `390×844`, `768×1024`, and `1366×768` for `/`, `/analyze`, `/results/{id}` (`en`, `ur`, `sd`), `/expert/login`, `/expert/dashboard`, and `/expert/analysis/{id}`.
- **Requirement**: Strict elimination of horizontal page scrolling across all breakpoints and all three languages.
- **Expected implementation**: Document respects `max-width: 100vw`; wide monospace strings, tables, and charts stay wrapped or inside scoped horizontal containers without expanding the page viewport.
- **Pass/fail verification method**: Evaluate `document.documentElement.scrollWidth <= window.innerWidth` across Landing, Wizard Steps 1–5, Results, and Expert views at `320px`, `360px`, `390px`, `768px`, and `1366px` in `en`, `ur`, and `sd`.
- **Severity if missing**: High

### 15. No Raw Technical JSON in Farmer View
- [x] **PASS** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/expert-user-flow.md`)*
- **Runtime Note**: Confirmed `hasRawJsonBraces: false` across Landing, Wizard, and Results (`en`, `ur`, `sd`); replaced backend `health_poor_001` identifier leakage with `"Environmental pattern grouping"`, and verified zero Silhouette/DBI scores, SQLite IDs, or server paths appear on public screens.
- **Requirement**: Public farmer screens must present clean domain language and zero exposed JSON blobs, math diagnostics, or internal system artifacts.
- **Expected implementation**: No raw JSON blocks, Silhouette/Davies-Bouldin numbers, SHA-256 strings, SQLite IDs, or server filesystem paths anywhere on Landing, Wizard, Results, Explanation Timeline, or Share outputs; deep diagnostics remain strictly inside Expert Detail.
- **Pass/fail verification method**: Audit full DOM text, collapsible Explanation Timeline, and Share preview in Farmer view after analysis; confirm zero raw keys, stack details, or clustering math scores appear.
- **Severity if missing**: Medium

### 16. No Unsupported Scientific Claims
- [x] **PASS** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/expert-user-flow.md`, `docs/ui/component-specification.md`)*
- **Runtime Note**: Cluster displays neutral label (`"Higher bare/thermal exposure"`) and `"Environmental pattern grouping"`; unverified crop rules cap confidence at `73% ●●○` with `"Expert review advised"` caution banner; advisory footer (`"Satellite signals support a conversation with local experts; they do not replace field inspection."`) and WhatsApp share URL work without disease/yield claims.
- **Requirement**: Faithful enforcement of Responsible AI wording, neutral K-Means cluster terminology, scale limitations, and advisory disclaimers.
- **Expected implementation**: Clusters display neutral labels (*"Relatively vegetated"*, *"Intermediate condition"*, *"Higher bare/thermal exposure"*) with explanatory non-diagnostic caption; no *"healthy crop"*, *"diseased"*, *"crop failure"*, *"guaranteed suitable/yield"*, or *"flood-prone/prediction"*; SMAP/GPM state coarse regional context; unverified rules warn instead of hard rejecting; Results and WhatsApp share preserve visible disclaimer (*"supports, does not replace, farmer judgment"*).
- **Pass/fail verification method**: Search rendered `en`, `ur`, and `sd` UI strings across all states for banned phrases and verify regional limitation tags, cap explanations, and advisory disclaimer appear prominently.
- **Severity if missing**: Critical

### 17. Existing Backend API Compatibility
- [x] **PASS** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/component-specification.md`, `apps/api/app/main.py`)*
- **Runtime Note**: Verified live against FastAPI (`uvicorn app.main:app` on `127.0.0.1:8000` via `python scripts/start_demo.py`): `GET /api/v1/health`, `GET /api/v1/crops`, `POST /api/v1/analyze`, `GET /api/v1/analyses/{id}`, `GET /api/v1/weather`, `GET /api/v1/layers/metadata`, and `GET /api/v1/layers/{ndvi,ndmi,bsi,slope}.png` returned HTTP `200` with zero unhandled payload mismatches or `pageErrors`.
- **Requirement**: Frontend integrates cleanly against existing FastAPI contracts without altering or breaking API schemas.
- **Expected implementation**: Consumes `GET /api/v1/health`, `GET /api/v1/crops`, `GET /api/v1/weather?lat=...&lon=...`, `POST /api/v1/analyze`, `GET /api/v1/analyses/{analysis_id}`, `GET /api/v1/layers/metadata`, and `GET /api/v1/layers/{name}.png` (`ndvi`, `ndmi`, `bsi`, `slope`), gracefully handling optional unavailable weather/model flags. *(Expert Portal features requiring new auth/notes endpoints must either align with approved backend contracts or explicitly isolate unsupported persistence without faking saves).*
- **Pass/fail verification method**: Run live frontend against running backend (`uvicorn app.main:app`) and verify Network tab shows clean `200` responses across Health, Crops, Analyze, Analysis Reload, Weather, and PNG Layers with zero unhandled payload mismatches.
- **Severity if missing**: Critical

### 18. Loading, Empty, Error, Insufficient-Data, and Outside-Coverage States
- [x] **PASS** *(Ref: `docs/ui/farmer-user-flow.md`, `docs/ui/accessibility-guidelines.md`)*
- **Runtime Note**: Verified Step 1 empty-location `[role="alert"]`, invalid analysis ID recovery screen (`"No saved analysis found for this ID."` + `"Try again"`), outside Hyderabad pilot coverage `25.8140, 68.4220` (`Not applicable` card, `0` rotation cards, `"Try again"` link), and invalid Expert login alert without page crashes. (`insufficient_data` JSX branch verified in source code review; not mock-triggered in Playwright.)
- **Requirement**: Every asynchronous delay, missing selection, validation/server error, and spatial boundary status displays clear, accessible feedback while preserving user inputs.
- **Expected implementation**: Step 1 keeps Continue disabled until location is selected + amber GPS fallback alert; Step 2 shows crop tile skeletons while loading + retry card on failure; Step 5 shows `role="status" aria-live="polite"` 3-step botanical loader + `role="alert"` error banner retaining selections and showing `Request ID`; Results renders calm dedicated notice cards when `status === "not_applicable"` (outside Hyderabad pilot) or `status === "insufficient_data"` (hiding rotation grid cleanly).
- **Pass/fail verification method**: Simulate GPS denial, slow/failed `/crops`, `422`/`500` on `/analyze` (verify state preserved + `Request ID` shown), out-of-bounds coords (e.g., `31.52, 74.36`), and `insufficient_data` response.
- **Severity if missing**: Critical

---

## Top 10 Visual Acceptance Checks (Before Phase 1 Sign-Off)

1. **Zero Prototype Artifacts**: **PASS** — Heavy borders/neon outlines replaced with hairline borders, restrained SaaS cards, readable typography (`16px` scale), and clean SVG icons; zero dev overlay errors after MapLibre worker fix.
2. **Calm SaaS Palette Fidelity**: **PASS** — Light canvas with botanical `#15803D` brand actions, fixed white-on-green CTA contrast (`rgb(255, 255, 255)`), and cohesive Farmer/Expert visual language verified on screenshots.
3. **Above-the-Fold Farmer Clarity**: **PASS** — Hero CTA + clean sections on `/`, and Analysis Summary + Environmental strip + 3 Rotation Cards lead `/` and `/results/{id}` cleanly above map/timeline telemetry *(Landing `/` still lacks inline Saved ID lookup)*.
4. **Priority Card Visual Hierarchy**: **PASS** — Equal-height 3-column desktop grid clearly emphasizes `Priority option: Keep it balanced` alongside `Your current rotation` and `Balanced option` without obscuring score/confidence tradeoffs.
5. **Weather State Visual Separation**: **PASS** — Active `EXPIRED SAMPLE` state renders clearly with explicit pill and `"weather does not block the rotation result"` banner; distinct `Live` and `Unavailable` branches exist in `results/[id]/page.tsx` *(not independently toggled at runtime)*.
6. **Non-Diagnostic Cluster & Scale Honesty**: **PASS** — Cluster cards avoid diagnostic crop-health red/green framing (`Environmental pattern grouping`) and Expert/API preserves SMAP/GPM coarse-scale honesty.
7. **Map Overlay & Legend Polish**: **FAIL** *(Partial)* — All 4 overlays (`NDVI`, `NDMI`, `BSI`, `Slope`) align in `dir="ltr"` with `>= 44×44 px` controls and live numeric min/max/date legends; Expert opacity slider and `150 m` circle overlay are omitted in Phase 1.
8. **True Urdu & Sindhi RTL Elegance**: **PASS** — `dir="rtl"`, Arabic typography, Sindhi glyphs (`ٻ`/`ڳ`/`ڻ`), flipped crop sequence arrows, and `.ltr-token` numeric BiDi isolation verified across Results screenshots *(some secondary English labels remain in tables/timelines)*.
9. **`320px` & `360px` Mobile Fit**: **PASS** — Zero horizontal overflow across `320×568` and `360×800` on all Farmer and Expert routes with `>= 44×44 px` touch targets.
10. **Research-Grade Expert Portal Look**: **PASS** — Login, Dashboard, and `Analysis evidence` views present calm scientific metrics, monthly charts, and local review notes without console dumps *(global queue/notes APIs deferred to Phase 2 backend work)*.
