# AgriShift AI — Multilingual & RTL Layout Guidelines (Urdu, Sindhi, English)

## 1. Document Direction & Language Switching
Every language switch updates the root `<html>` element synchronously:
- **English**: `<html lang="en" dir="ltr">`
- **Urdu**: `<html lang="ur" dir="rtl">`
- **Sindhi**: `<html lang="sd" dir="rtl">`

**Strict CSS Rule**: Never use physical directional CSS properties (`margin-left`, `padding-right`, `text-align: left`, `border-left`, `left: 0`). Always use **CSS Logical Properties**:
- `margin-inline-start` / `margin-inline-end`
- `padding-inline-start` / `padding-inline-end`
- `inset-inline-start` / `inset-inline-end`
- `border-inline-start` / `border-inline-end`
- `text-align: start` / `text-align: end`

---

## 2. Typography & Vertical Rhythm

| Language | Primary Font Stack | Base Font Size | Line Height | Special Rules |
| :--- | :--- | :--- | :--- | :--- |
| **English (`en`)** | `"Inter", system-ui, sans-serif` | `16px` | `1.5` | Standard letter-spacing (`0`) |
| **Urdu (`ur`)** | `"Noto Naskh Arabic", "Noto Nastaliq Urdu", sans-serif` | `16px–17px` | `1.75` | Never apply negative `letter-spacing` (breaks Arabic ligatures). Increase vertical line-height to prevent ascender/descender collisions (`Diacritics` / `Zabar-Zer`). |
| **Sindhi (`sd`)** | `"Noto Naskh Arabic", "MB Lateefi", system-ui, sans-serif` | `16px–17px` | `1.75` | Ensure font supports Sindhi-specific glyphs (`ٻ`, `ڄ`, `ڃ`, `ڏ`, `ڳ`, `ڻ`, `ھ`). `Noto Naskh Arabic` provides full Unicode Arabic Supplement coverage. |

---

## 3. Alignment & Spacing Rules
- **Paragraphs & Headings**: Always `text-align: start` (Right-aligned in `ur`/`sd`, Left-aligned in `en`).
- **Centered Hero/Wizard Titles**: May use `text-align: center` across all 3 languages, provided sub-lists inside cards revert to `text-align: start`.
- **Lists & Bullet Indentation**: Use `padding-inline-start: 20px;` so bullets/checkmarks sit cleanly on the right in Urdu/Sindhi and left in English.
- **Accent Borders**: Emphasis bars on alerts or cards (`border-inline-start: 4px solid ...`) automatically flip to the right edge in RTL.

---

## 4. Numbers, Units & Mixed-Language (BiDi) Handling
Improper bidirectional (`BiDi`) rendering causes numbers, coordinates, and negative signs (`-0.17`) to flip backwards in Urdu/Sindhi sentences.
1. **Numeral System**: Use **Western Arabic numerals (`0–9`)** consistently across English, Urdu, and Sindhi for agricultural clarity (temperatures `37.4°C`, coordinates `25.396°`, Analysis IDs `AGR-8492`).
2. **Isolate Technical Tokens (`dir="ltr"`)**: Wrap the following elements in `<span dir="ltr" class="bidi-isolate">` (`unicode-bidi: isolate; direction: ltr; display: inline-block;`):
   - GPS Coordinates (`25.3960° N, 68.3578° E`)
   - Analysis IDs (`AGR-2026-8492`)
   - Scientific indices & negative decimals (`-0.17`, `0.59`, `38.26 mm`)
   - Dates (`2025-09-30`)
   - Scene IDs (`LC09_L2SP_...`)
3. **Mixed Language Brand/Crop Terms**: Terms like `"NASA SMAP"` or `"Landsat 9"` embedded inside an Urdu sentence should be wrapped with `<bdi>` tags so punctuation (periods, parentheses) stays in the correct logical order.

---

## 5. Tables in RTL
- **Farmer Comparison Table**: Follows document direction (`dir="rtl"` in Urdu/Sindhi). The frozen attribute column (`Metric / پیرامیٹر`) sits on the **right** (`inset-inline-start: 0`), with the 3 rotation columns flowing right-to-left.
- **Numeric Cells inside RTL Tables**: Apply `dir="ltr"; text-align: end;` (or `center`) to numeric cells so `-0.17` never renders as `0.17-`.
- **Expert Scientific Evidence Tables**: If an agronomist opens the Expert Portal in Urdu/Sindhi, structural headings translate, while raw USGS scene identifiers and coordinate columns enforce `dir="ltr"`.

---

## 6. Icons & Directional Mirroring
- **Icons that MUST Mirror in RTL (`[dir="rtl"] .icon-directional { transform: scaleX(-1); }`)**:
  - Next / Back wizard arrows (`→`, `←`)
  - Crop transition arrow inside `<RotationCard />` (`Cotton → Wheat`)
  - Breadcrumb chevrons (`>`)
  - Progress bars (fill direction flows right-to-left naturally with `dir="rtl"`).
- **Icons that MUST NOT Mirror in RTL**:
  - Checkmarks (`✓`)
  - Clock / History icons
  - Map compass North arrow (`N`), Zoom `+` / `-`, GPS Crosshair
  - WhatsApp brand logo, Plant/Leaf SVG icons, Rain/Sun weather icons
  - Charts & Map Canvas (`MapLibre GL` container MUST enforce `dir="ltr"` internally so map tile coordinates, pan gestures, and scale bars never invert).
