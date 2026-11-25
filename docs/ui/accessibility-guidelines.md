# AgriShift AI — Accessibility Guidelines (WCAG 2.2 AA)

## 1. Compliance Target
All public Farmer screens and Expert Portal screens must satisfy **WCAG 2.2 Level AA**, ensuring usability by smallholder farmers with varying literacy levels, screen-reader users, and low-vision agronomists.

---

## 2. Touch Targets & Motor Accessibility
- **Minimum Interactive Size**: Every button, radio tile, language switch, map zoom control, and close icon must have a minimum clickable/tappable area of **`44 × 44 px`** (`48 × 48 px` for primary Wizard CTAs).
- **Spacing**: Maintain at least **`8px` (`space-2`)** gap between adjacent interactive controls to prevent accidental taps on `320px–390px` screens.

---

## 3. Keyboard Navigation & Focus Management
- **Logical Tab Order**: Tab sequence must follow visual reading order (in both LTR and RTL).
- **Visible Focus Indicators**: Never remove browser focus outlines (`outline: none`) without replacing them. Use:
  ```css
  :focus-visible {
    outline: 2px solid #15803D;
    outline-offset: 2px;
  }
  ```
- **Wizard Focus Progression**: When advancing from Wizard Step $N$ to Step $N+1$, programmatically move focus to the new step's `<h1>` / `<h2>` heading (`tabindex="-1"`) so screen readers announce the new step title immediately.
- **Modal / Drawer Trap**: Open modals (e.g., WhatsApp preview, mobile nav drawer) must trap `Tab` focus inside and close on `Escape`, returning focus to the triggering button.

---

## 4. Screen Reader & Semantic Structure
1. **Semantic Headings**: Every page has exactly one `<h1>`; cards use `<h3>`; sections use `<h2>`. Never use styled `<div>`s as headings.
2. **Dynamic Status Announcements (`aria-live`)**:
   - **Wizard Loading Screen**: Container must carry `role="status" aria-live="polite"` announcing *"Analyzing satellite and climate records for your field..."*.
   - **Validation & API Errors**: Error banners carry `role="alert" aria-live="assertive"`.
   - **Copied Analysis ID Toast**: `role="status" aria-live="polite"`.
3. **Confidence Dots Alternative Text**:
   - Never render visual dots (`● ● ○`) alone. Include `<span class="sr-only">Confidence level: 2 out of 3 dots (Moderate)</span>`.
4. **Non-Color State Communication**:
   - **Weather States**: Live vs. Sample vs. Unavailable must display explicit text + distinct icon (`Radio`, `Clock`, `CloudOff`), never green/yellow/gray dots alone.
   - **Real vs. Demo Mode**: Explicit text banner (`"Real Environmental Data"` vs. `"Demo Mode"`).
   - **Form Selection**: Selected Crop/Priority tiles use both border/background change AND a visible checkmark SVG + `aria-checked="true"` (with `role="radiogroup"` / `role="radio"`).
5. **Decorative vs. Functional Icons**:
   - All decorative SVG icons inside text buttons carry `aria-hidden="true"`.
   - Icon-only buttons (Back arrow, Map Zoom `+`/`-`, Menu hamburger, Copy ID) carry explicit `aria-label` attributes localized in the active language (`en`, `ur`, `sd`).

---

## 5. Color Contrast Verification
- Body text (`#0F172A` on `#FFFFFF` / `#F8FAFC`): $\ge 15:1$ (Passes AAA).
- Muted metadata (`#475569` on `#FFFFFF`): $7.0:1$ (Passes AA/AAA).
- Primary CTA (`#FFFFFF` on `#15803D`): $5.1:1$ (Passes AA).
- Warning badge text (`#78350F` on `#FEF3C7`): $\ge 8.5:1$ (Passes AAA).
- Risk badge text (`#7F1D1D` on `#FEE2E2`): $\ge 9.0:1$ (Passes AAA).
- Placeholder text inside inputs must be `#64748B` or darker ($\ge 4.5:1$).
