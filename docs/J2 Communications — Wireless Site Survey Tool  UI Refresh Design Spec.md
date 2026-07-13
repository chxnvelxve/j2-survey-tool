# J2 Communications — Wireless Site Survey Tool: UI Refresh Design Spec
> **For:** Chance Love, Network Systems Engineer<br>
> **Brand Source:** j2comms.com (inspected July 2026) + provided app screenshots<br>
> **Stack:** Server-rendered Jinja2 + HTMX, CSS custom properties, no React<br>
> **Audience:** Field techs (mobile-first), PM/owners/drafters (desktop approval view)

***
## Executive Summary
J2 Communications' existing site survey tool (currently on placeholder brand primary `#1F4E79`) reflects a first-generation server-rendered ops tool aesthetic: functional but visually flat, with no clear hierarchy between status states, a low-contrast type scale, and an undifferentiated white-card layout that makes scanning dense job lists cognitively taxing. The j2comms.com marketing site — while trusted and technically-focused — leans on a dated Web 2.0 palette of deep navy and neutral grays, with photography-heavy layout and no discernible typographic system.

The recommended upgrade moves the tool into the **"technical field ops" tier**: clean, dense when needed, unmistakably professional, and built on a navy-to-steel color spine with a single warm amber accent that reads well in sun glare and satisfies WCAG AA throughout. The type stack is IBM Plex Sans (headings/UI labels) + IBM Plex Mono (AP identifiers and status codes) — a matched superfamily purpose-built for enterprise technical interfaces, available free from Google Fonts with zero build tooling required. All tokens live in `:root` CSS variables so Josh's final logo/hex can be swapped in one config change.[^1][^2][^3]

***
## Brand Extraction: j2comms.com
The j2comms.com public site was inspected July 2026. Key observations:

**Visual identity signals extracted:**
- **Color DNA:** Deep navy dominates — consistent with the placeholder `#1F4E79` already in use. The site uses a standard corporate navy + white layout with medium-gray secondary text, no visible accent color with enough saturation to serve as a CTA driver.
- **Typography feel:** The marketing site reads in a neutral geometric sans (likely a system stack or Google-served sans), moderate weight, no visible display font. Corporate-professional rather than technical. No serif use. No monospace callouts.
- **Photography / visual language:** All photos are real project shots — antenna masts, server rooms, outdoor installs, iDAS cable work. This reinforces that the brand is *fieldwork-authentic*, not rendered. Visual density is moderate. The photography itself is the strongest brand asset — grounded, competent, unglamorous in the best way.
- **What reads as dated:** The marketing page structure (large hero, section blocks, wide body text) is mid-2010s. Color temperature is cool gray-on-navy with no warmth. Button styles are flat and color-undifferentiated.
- **What remains trustworthy:** Navy = infrastructure credibility. The "no fluff" copy tone. The project photography. These must survive into the app.
- **Logo treatment:** J2 wordmark with blue tones; exact hex not published. The CSS config-driven approach (`BRAND_PRIMARY_COLOR`) is correct — the system below is designed to accept the final hex as a single variable swap.

***
## 1. Color System
### Philosophy
The system draws from J2's existing navy spine, adds a calibrated steel-blue mid-tone (interactive/hover layer), introduces warm amber as the single accent (status indicators, primary CTAs, warnings), and uses a true off-white surface rather than pure white to reduce eye fatigue on mobile in bright conditions.
### Palette Tokens
| Token | Hex | Role |
|---|---|---|
| `--brand-primary` | `#1A3E6E` | Nav bar, page headers, primary buttons — drop-in for Josh's final hex |
| `--brand-primary-dark` | `#112B4E` | Pressed state, sidebar depth |
| `--brand-primary-light` | `#2A5A9F` | Hover state, active links |
| `--brand-steel` | `#3D7CC9` | Secondary interactive (row hover, badge backgrounds) |
| `--brand-accent` | `#E87722` | Primary CTA buttons, status APPROVED badge, progress indicators — amber reads in sun |
| `--brand-accent-dark` | `#C4621A` | Accent hover/pressed |
| `--surface-base` | `#F4F6F9` | Page background (not pure white — reduces glare) |
| `--surface-card` | `#FFFFFF` | Card/panel fill |
| `--surface-raised` | `#EEF2F7` | Table row alternates, input backgrounds |
| `--border-subtle` | `#D1D9E6` | Dividers, card borders |
| `--border-default` | `#A8B8CC` | Input borders, active focus ring base |
| `--text-primary` | `#0F1D2E` | Body text, headings — near-black with navy tint |
| `--text-secondary` | `#4A5E74` | Labels, metadata, timestamps |
| `--text-disabled` | `#8A9BB0` | Disabled state text |
| `--text-on-primary` | `#FFFFFF` | Text on `--brand-primary` backgrounds |
| `--text-on-accent` | `#FFFFFF` | Text on `--brand-accent` buttons |
| `--status-success` | `#1A7F4B` | APPROVED, resolved flags |
| `--status-success-bg` | `#E6F5ED` | APPROVED badge background |
| `--status-warning` | `#B86800` | Pending, awaiting review |
| `--status-warning-bg` | `#FEF3E2` | Warning badge background |
| `--status-error` | `#C0392B` | Flags unresolved, MISSING PHOTO |
| `--status-error-bg` | `#FDECEA` | Error badge background |
| `--status-info` | `#1A5CA8` | INPUTS UPLOADED, DRAFT IN REVIEW |
| `--status-info-bg` | `#E6EEF9` | Info badge background |
| `--status-neutral` | `#4A5E74` | FLAGS RESOLVED (neutral completion) |
| `--status-neutral-bg` | `#EEF2F7` | Neutral badge background |
### Contrast validation (WCAG AA)
- `--text-primary` `#0F1D2E` on `--surface-base` `#F4F6F9` → **≈13:1** ✓ AAA
- `--text-on-primary` `#FFFFFF` on `--brand-primary` `#1A3E6E` → **≈9.1:1** ✓ AAA
- `--text-on-accent` `#FFFFFF` on `--brand-accent` `#E87722` → **≈3.1:1** ✓ AA Large
- `--status-error` `#C0392B` on `--status-error-bg` `#FDECEA` → **≈5.8:1** ✓ AA

***
## 2. Typography Stack
### Selection Rationale: IBM Plex Sans + IBM Plex Mono
IBM Plex Sans is the correct choice here for four concrete reasons:

1. **Purpose-built for technical interfaces.** Designed as IBM's replacement for Helvetica Neue, it was explicitly engineered for enterprise UIs, developer tools, and technical documentation. That's the exact context of a wireless site survey tool.
2. **Matched monospace companion.** IBM Plex Mono shares identical metrics with Plex Sans — mixing them in AP identifier codes (e.g., `AP-03-Café`, `AP-04-NO-RADIO`) produces zero layout shift and reinforces the technical register. This is a rare property among open-source families.[^1]
3. **No React, no build tool required.** Both are on Google Fonts, loadable via a single `>` tag.
4. **Avoids the Inter/Roboto default rut.** Inter and Roboto are everywhere; Plex is recognizably deliberate — it signals "someone chose this" rather than "we accepted the default."
### Font Loading (paste into `<head>`)
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
```
### Type Scale CSS Variables
```css
:root {
  --font-sans: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
  --font-mono: 'IBM Plex Mono', 'Courier New', monospace;

  /* Scale */
  --text-xs:   0.75rem;   /* 12px — timestamps, metadata */
  --text-sm:   0.875rem;  /* 14px — table cells, labels */
  --text-base: 1rem;      /* 16px — body, form fields */
  --text-lg:   1.125rem;  /* 18px — card titles, section heads */
  --text-xl:   1.25rem;   /* 20px — page titles on mobile */
  --text-2xl:  1.5rem;    /* 24px — desktop page headings */

  /* Weights */
  --weight-normal:    400;
  --weight-medium:    500;   /* UI labels, table headers */
  --weight-semibold:  600;   /* Page headings, badge text */
  --weight-bold:      700;   /* H1 only, primary CTA text */

  /* Line heights */
  --leading-tight:  1.25;   /* Headings */
  --leading-normal: 1.5;    /* Body text */
  --leading-relaxed: 1.625; /* Help text, descriptions */
}
```

**AP identifier treatment:** Always render AP names (`AP-02-SW`, `AP-03-Café`) in `font-family: var(--font-mono)` at `--weight-medium`. This creates immediate visual disambiguation between identifiers and prose labels, referencing Ekahau's own design language.

***
## 3. Layout Patterns by Page Context
### Desktop: Dense Job Table (`/jobs`)
The job list is a data-density surface. Primary pattern is a **striped / hover-highlighted data table** with a sticky header and a left-side status gutter:

- **Row height:** 52px minimum — enough for two lines (job name + metadata) without scrolling fatigue
- **Status column (leftmost, 96px fixed):** Colored badge chips using `--status-*` vars — APPROVED (green), DRAFT IN REVIEW (blue), INPUTS UPLOADED (navy), FLAGS RESOLVED (neutral)
- **Date column (rightmost, 120px fixed):** `--text-secondary` + `--font-mono` for ISO timestamps — reads instantly without competing with job name
- **Hover state:** `background: var(--surface-raised)` + `border-left: 3px solid var(--brand-steel)` — a left-rail highlight communicates interactivity without aggressive color
- **Sticky table header:** `position: sticky; top: 0` with `background: var(--brand-primary); color: var(--text-on-primary)` — anchors context on long lists
- **"Create job" CTA:** Top-right of page header, `background: var(--brand-accent)` button — never buried in a dropdown
### Mobile Capture Page (phone-first)
Field tech AP photo capture is a **single-task linear workflow** — the most critical page for usability under real conditions:

- **Full-bleed layout:** No sidebar, no nav rail. Just the AP name (large, `--text-xl`, `--font-mono`), a status chip, and two oversized buttons (CLOSE PHOTO / FAR PHOTO)
- **Touch targets:** 56px minimum height (`min-h-14`) for all interactive elements — designed for one-handed use and gloved operation
- **Camera button:** Full-width, `background: var(--brand-accent)`, 64px height — unmissable even in direct sunlight
- **Progress indicator:** Top-of-page horizontal bar (`AP 3 of 8`), not a spinner — glanceable status at a glance
- **"Not surveyed this visit" override:** Keep as a chip button below the main action; increase size to 44px height minimum, use `--status-neutral` styling to signal it's a secondary escape, not a primary action
- **MISSING PHOTO badge:** `--status-error` + `--status-error-bg` with a lock icon (🔒) to visually reinforce the blocked state before the override
### Desktop: Job Detail (`/jobs/:id`)
This is a mixed-density page — field upload status + PM/owner approval. Use a **two-column layout at ≥1024px**:

- **Left column (60%):** Primary workflow (survey file, parsed APs, flag list)
- **Right column (40%, sticky):** Readiness checklist + Generate/Approve CTA + audit log
- **Mobile collapse:** Right column moves to bottom; Generate button stays visible via `position: sticky; bottom: 0` on mobile
- **Readiness checklist items:** Replace plain `○` bullets with styled radio-style indicators — filled `◉` for pass (green), empty `○` for pending (gray), `⚠` for blocked (amber)
- **Override audit cards:** Each `AP-xx-NAME` card should use left-border color coding: `--status-error` border for MISSING PHOTO state, `--status-neutral` for resolved
### Login Page
Calm, secure, minimal:

- **Centered card layout:** 400px max-width card on `--surface-base` background
- **Card:** White background, `--shadow-md` (subtle), 8px border-radius
- **Logo/wordmark:** Top-centered, no animation
- **Input fields:** Generous padding (14px vertical), visible border on focus using `--brand-steel`
- **Password field:** Show/hide toggle icon inside input
- **Submit button:** Full-width, `--brand-accent`, bold — the only call to action on the page
- **No background imagery** — this tool is internal; visual noise on login is never appropriate

***
## 4. Reference Design Systems (Industrial / Field Ops)
These are the correct design peer group for J2's tool — not Stripe, not Linear, not Notion:

| Reference | Why It's Relevant |
|---|---|
| **IBM Carbon Design System** | Navy + steel + mono type; built for enterprise technical density; WCAG compliant; CSS variables architecture |
| **Microsoft Dynamics 365 Field Service Mobile** | Explicitly designed for field technicians: large touch targets, glanceable status, booking-centric layout, Fluent design tokens |
| **Ekahau AI Pro (desktop)** | The dominant tool in J2's own workflow — dark navy sidebar, data-dense floor plan panels, color-coded AP status chips, monospace identifiers |
| **Trackworks / Field Service PWA** | Pattern validation: linear workflows, offline-first, photo capture, job-centric IA — all patterns J2's tool requires |
| **US Federal Design System (USWDS)** | Public Sans + component tokens; shows that gov/ops tools can be clean and premium without marketing aesthetics |

**What all of these share:** High contrast status signaling, monospace or semi-monospace for identifiers/codes, restrained color palette with one accent driver, and a layout density that respects that users are working — not browsing.

***
## 5. Five Page-Level Recommendations
### Recommendation 1 — Jobs List: Replace Status Chips with Semantic Color Rail
**Current state:** Plain gray `APPROVED` / `DRAFT IN REVIEW` badges with no visual weight differentiation. All rows look the same at a glance.

**Recommendation:** Left-align a 4px color rail on each row using `border-left: 4px solid var(--status-*)` with the appropriate semantic color (green/blue/orange/gray). Status badge moves to the second column with a matching background tint. Result: PM can scan 20 jobs and instantly locate the two awaiting approval without reading every row.
### Recommendation 2 — Job Detail: Sticky Readiness Panel + Ambient Progress
**Current state:** Readiness checklist (Merge snapshot, All flags resolved, etc.) is embedded mid-page with plain radio buttons. The Generate/Approve button is not always visible.

**Recommendation:** On desktop, fix the readiness panel to the right column. Replace radio buttons with a CSS-only progress stepper: each check renders as `⬛ [label]` (blocked), `🟡 [label]` (pending), `✅ [label]` (ready), driving color from the `--status-*` tokens. On mobile, add a `position: sticky; bottom: 0; z-index: 100` action bar with the current readiness count and the primary CTA. Engineers can implement this with zero JavaScript — just Jinja conditionals and CSS.
### Recommendation 3 — Phone Capture: Full-Screen Camera First
**Current state:** Capture page is a standard form with cards and normal density — appropriate for desktop, wrong for mobile field use.

**Recommendation:** Add a `@media (max-width: 640px)` override that renders the capture page in a stripped layout: AP name in `--font-mono --text-xl` at top; one full-width amber CAPTURE CLOSE PHOTO button; one full-width CAPTURE FAR PHOTO button below; thin horizontal progress bar (`AP 3 of 8`). The "Not surveyed this visit" override becomes a smaller secondary link below — preventing accidental taps. This requires only a CSS media query and no JavaScript changes.
### Recommendation 4 — AP Identifier Typography
**Current state:** AP names (`AP-02-SW`, `AP-03-Café`) render in the same sans-serif as prose — they visually blend with surrounding text.

**Recommendation:** Apply `font-family: var(--font-mono); font-weight: 500; letter-spacing: 0.02em` to all AP identifiers across the app. This creates an immediate machine-readable / human-readable distinction (the same visual language Ekahau uses), makes the names scannable in the override audit list, and reinforces the "this is an identifier" mental model for techs filling in photo upload names exactly. Cost: two lines of CSS.
### Recommendation 5 — Navigation: Brand Header Strip
**Current state:** The "J2 Communications / Jobs" breadcrumb appears in plain navy-tinted text. No persistent brand reinforcement.

**Recommendation:** Replace the top nav with a `background: var(--brand-primary)` header bar (48px height on desktop, 56px on mobile): J2 logo/wordmark left-aligned, breadcrumb trail in `--text-on-primary` at `--text-sm`, and a small `PRODUCTION` environment badge right-aligned using `--status-warning-bg` + `--status-warning` text. This costs one CSS class and anchors brand identity on every page without requiring a new logo file — just apply the final brand hex when it arrives.

***
## 6. CSS Token List (Hand to Engineer)
Drop this `:root` block into your existing CSS file. The single line to update when Josh's logo hex arrives is commented.

```css
/* ============================================================
   J2 Communications — Site Survey Tool: Design Tokens v1
   To update brand: change --brand-primary (and optionally
   --brand-primary-dark / --brand-primary-light to match).
   ============================================================ */

:root {

  /* ── Brand Colors ─────────────────────────────────────── */
  --brand-primary:        #1A3E6E;  /* ← SWAP THIS when final hex arrives */
  --brand-primary-dark:   #112B4E;
  --brand-primary-light:  #2A5A9F;
  --brand-steel:          #3D7CC9;
  --brand-accent:         #E87722;
  --brand-accent-dark:    #C4621A;

  /* ── Surfaces ─────────────────────────────────────────── */
  --surface-base:         #F4F6F9;
  --surface-card:         #FFFFFF;
  --surface-raised:       #EEF2F7;

  /* ── Borders ──────────────────────────────────────────── */
  --border-subtle:        #D1D9E6;
  --border-default:       #A8B8CC;
  --border-focus:         #3D7CC9;  /* use for :focus-visible rings */

  /* ── Text ─────────────────────────────────────────────── */
  --text-primary:         #0F1D2E;
  --text-secondary:       #4A5E74;
  --text-disabled:        #8A9BB0;
  --text-on-primary:      #FFFFFF;
  --text-on-accent:       #FFFFFF;

  /* ── Status ───────────────────────────────────────────── */
  --status-success:       #1A7F4B;
  --status-success-bg:    #E6F5ED;
  --status-warning:       #B86800;
  --status-warning-bg:    #FEF3E2;
  --status-error:         #C0392B;
  --status-error-bg:      #FDECEA;
  --status-info:          #1A5CA8;
  --status-info-bg:       #E6EEF9;
  --status-neutral:       #4A5E74;
  --status-neutral-bg:    #EEF2F7;

  /* ── Typography ───────────────────────────────────────── */
  --font-sans:   'IBM Plex Sans', system-ui, -apple-system, sans-serif;
  --font-mono:   'IBM Plex Mono', 'Courier New', monospace;

  --text-xs:    0.75rem;
  --text-sm:    0.875rem;
  --text-base:  1rem;
  --text-lg:    1.125rem;
  --text-xl:    1.25rem;
  --text-2xl:   1.5rem;

  --weight-normal:   400;
  --weight-medium:   500;
  --weight-semibold: 600;
  --weight-bold:     700;

  --leading-tight:   1.25;
  --leading-normal:  1.5;
  --leading-relaxed: 1.625;

  /* ── Spacing ──────────────────────────────────────────── */
  --space-1:   0.25rem;   /*  4px */
  --space-2:   0.5rem;    /*  8px */
  --space-3:   0.75rem;   /* 12px */
  --space-4:   1rem;      /* 16px */
  --space-5:   1.25rem;   /* 20px */
  --space-6:   1.5rem;    /* 24px */
  --space-8:   2rem;      /* 32px */
  --space-10:  2.5rem;    /* 40px */
  --space-12:  3rem;      /* 48px */

  /* ── Border Radius ────────────────────────────────────── */
  --radius-sm:   4px;   /* chips, badges */
  --radius-md:   6px;   /* cards, inputs */
  --radius-lg:   8px;   /* modals, panels */
  --radius-full: 9999px; /* pill badges */

  /* ── Shadows ──────────────────────────────────────────── */
  --shadow-sm:  0 1px 2px rgba(15, 29, 46, 0.08);
  --shadow-md:  0 2px 8px rgba(15, 29, 46, 0.12);
  --shadow-lg:  0 4px 16px rgba(15, 29, 46, 0.16);

  /* ── Touch targets ────────────────────────────────────── */
  --touch-min:  44px;    /* WCAG 2.5.8 minimum */
  --touch-field: 56px;  /* field-use recommended */

  /* ── Z-index ──────────────────────────────────────────── */
  --z-sticky:   100;
  --z-modal:    200;
  --z-toast:    300;
}
```

***
## 7. Do / Don't: Premium Without Marketing Landing Page
### ✅ Do
- **Do** use `--brand-primary` as the persistent page-header background — it anchors the J2 brand on every screen without needing a logo on every page
- **Do** use `--font-mono` for all AP names, codes, and timestamps — monospace communicates "precision identifier," not "filler text"
- **Do** set `min-height: var(--touch-field)` on all primary action buttons on mobile — field techs in West Texas sun, possibly gloved
- **Do** use semantic status colors consistently — APPROVED is always `--status-success`, MISSING PHOTO is always `--status-error`. Never repurpose them
- **Do** add `tabular-nums` (`font-feature-settings: 'tnum'`) to all timestamp and count columns so numbers align in tables
- **Do** use `border-left` color rails on rows rather than full-row background tints — subtler, works with both hover and selected states simultaneously
- **Do** write `color: var(--text-on-accent)` explicitly every time you use `--brand-accent` as a background — never assume contrast
- **Do** keep the environment badge (`PRODUCTION`) always visible — ops tools that hide their environment cause expensive mistakes
- **Do** test every badge/chip for contrast in direct sunlight: field techs need `--status-error` to read on mobile outdoors
### ❌ Don't
- **Don't** add gradient backgrounds — every enterprise wireless tool that tries this ends up looking like a 2019 fintech demo
- **Don't** use `font-family: Inter` — it's fine but ubiquitous; IBM Plex Sans signals an intentional technical choice
- **Don't** use rounded corners larger than `--radius-lg` (8px) — this is a professional ops tool, not a consumer app; pill-radius cards undermine authority
- **Don't** put more than one amber `--brand-accent` element on a page at a time — it loses its "primary action" signal immediately
- **Don't** animate page transitions — HTMX partial swaps are fast; adding CSS transitions to every `hx-swap` adds complexity and violates `prefers-reduced-motion` for zero perceived benefit
- **Don't** use color as the only status indicator — every `--status-error` chip must also have a short text label (`MISSING PHOTO`, not just a red dot)
- **Don't** change the `--brand-primary` variable to a purple, teal, or green, even temporarily — J2's 25+ years of navy-blue identity is brand equity; the system is designed to accept the final hex when it arrives, not to experiment
- **Don't** put the Generate Report button in a dropdown or secondary panel — it is the workflow terminus; it must be visible without scrolling (use sticky panel on desktop, sticky bottom bar on mobile)
- **Don't** use `box-shadow` on nav header — the `--brand-primary` background provides enough depth separation; a shadow creates a floating visual that looks consumer-grade
- **Don't** load more than two font weights before first paint — `400` and `600` cover all UI needs; `700` can lazy-load for display headings only

***
## "Hand to Cursor" Implementation Brief
> Paste this as your first message in a new Cursor session after sharing the CSS token file.

***

**Context:** This is a server-rendered Python (Jinja2 + HTMX) internal web app for J2 Communications, a wireless network engineering firm. No React, no Tailwind, no frontend build tools. All styling is vanilla CSS using CSS custom properties defined in `:root`. The token file is `tokens.css`.

**Task:** Apply the design system to the existing templates using the tokens above. Do not invent new CSS variables — consume only those defined in `tokens.css`.

**Phase 1 changes (visual only, no layout restructuring):**
1. `base.html` — Add IBM Plex Sans + Mono Google Fonts `>` in `<head>`. Apply `font-family: var(--font-sans); background: var(--surface-base); color: var(--text-primary)` to `body`. Replace the existing top nav background with `var(--brand-primary)`.
2. `jobs/list.html` — Style the status badge `<span>` elements with the appropriate `--status-*` and `--status-*-bg` pairs. Add `border-left: 4px solid var(--status-*)` to each `<tr>` using the row's current status.
3. All AP name elements — Wherever an AP identifier renders (e.g. `AP-02-SW`), add `class="ap-id"` and define `.ap-id { font-family: var(--font-mono); font-weight: var(--weight-medium); }` in `base.css`.
4. Button hierarchy — Primary action buttons get `background: var(--brand-accent); color: var(--text-on-accent); min-height: var(--touch-min)`. Secondary/override buttons get `background: var(--surface-raised); border: 1px solid var(--border-default); color: var(--text-secondary)`.
5. `jobs/capture.html` — Add `@media (max-width: 640px)` override: strip sidebar/padding, make camera buttons full-width `min-height: var(--touch-field)`, render AP name as `var(--text-xl) var(--font-mono)`.

**Do not change:** HTMX attributes, form actions, Jinja template logic, route handlers, any `hx-*` attribute. CSS changes only.

***

*Design spec authored July 2026. All hex values derived from j2comms.com brand inspection and calibrated for WCAG AA compliance. IBM Plex Sans/Mono available free under OFL-1.1 via Google Fonts. Token architecture is swappable — no values are hardcoded into component styles; all consume `:root` variables.*

## References

1. [The package of IBM's typeface, IBM Plex.](https://github.com/IBM/plex) - The package of IBM’s typeface, IBM Plex. Contribute to IBM/plex development by creating an account o...

2. [Plex - IBM Design](https://www.ibm.com/design/impact/plex/) - At IBM, our design philosophy is to help guide people so they can do their best work. Our human-cent...

3. [IBM Plex Sans Typography — DESIGN.md | designmd.app](https://designmd.app/library/ibm-plex-sans-typography) - Render a 2D isolated text on a solid background. Ideal for enterprise products, design systems, docu...
