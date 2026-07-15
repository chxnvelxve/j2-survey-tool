# Claude handoff — post-pivot (read this first)

**Audience:** Claude / Codex (or any new agent) helping with pricing, SOW, phase rewrite, or rebuild planning.  
**Owner:** taking this into Claude after the Josh/Jeff intake pivot.  
**Date:** 2026-07-15

---

## 0. How to read the repo (critical)

### Source of truth (post-meeting)

Use these, in this order:

1. **`docs/meeting-notes-intake-pivot.md`** — product intent after Josh clarified Zoho → Nextcloud intake ([PR #5](https://github.com/chxnvelxve/j2-survey-tool/pull/5), branch `cursor/intake-pivot-meeting-notes-3614`).  
   If this file is missing on your checkout, fetch that branch/PR first.
2. **`docs/intake-pivot-review.md`** — owner review of that pivot ([PR #6](https://github.com/chxnvelxve/j2-survey-tool/pull/6)).
3. **This file** — pricing opinion (no OCR), large-doc approach, hosting, and agent rules.

### Stale by default (pre-pivot)

Assume **everything written before the pivot notes is stale for product direction**, including:

- `docs/PHASES.md` phase bodies (phone capture, Job upload UX, old activation order)
- `docs/ARCHITECTURE.md` / `DOMAIN.md` / `CLAUDE.md` product narrative on `main` (upload-centric Job flow)
- Pre-meeting demo pack: `meeting_demo_script.md`, `owner_brief.md`, `meeting_josh_asks.md`, etc.
- Any “Tech captures on phone → upload into Job” framing

**Exception — salvage, don’t invent from scratch:**  
Pre-pivot *code and patterns* that still serve the pivot are fair to reuse:

- `parser → merge → generator` stage boundaries
- Exact AP join + hard-fail / flag philosophy
- Bulk override reasons
- `.esx` parser shell, Nextcloud WebDAV shell, branding-in-config, docxtpl generator mechanics, deploy/Tailscale pattern

Reuse **implementation**, not **old product assumptions**. If old docs conflict with the pivot, the pivot wins.

### Do not

- Plan or price phone/PWA tech capture as v1.
- Put ThruLine or Layer-1 expansion in the first SOW.
- Assume OCR is in scope (owner is pricing **without** OCR unless Josh insists later).
- Treat 300–400 pages as every job — it is the **upper bound when AP count is high** (one page per AP).

---

## 1. Product in one paragraph (pivot)

Zoho intake drops files into a **Nextcloud project folder**. Drafters (Josh, Jeff, Casey — MacBooks) open a **shared web app**, **pick a Nextcloud project**, parse `.esx` + IDF PDF + AP photo dump, merge on **short AP ID** (hard-fail / flag, never silent), and generate a branded **Word** deliverable: **IDF/general tables up front**, then **one section/page per AP** (data grid + close + far photos). Draft/final marker files in the project warn concurrent users. No tech UI in this app.

Photo path **without OCR:** prefer desk rename to short AP ID; sequential pairs = close/far; otherwise **manual assign in UI**.

---

## 2. Professional pricing opinion (no OCR)

This is **owner guidance for a conversation with Claude / Josh**, not a signed quote. Refine after samples (`.esx`, IDF PDF, gold page, Nextcloud tree).

### What “no OCR” still includes

| In scope | Out of scope (for this price band) |
|----------|-------------------------------------|
| Nextcloud project browse/pick + locate `.esx` / photos / IDF | OCR / sticker reading / auto-suggest from image text |
| Parse `.esx`, parse IDF PDF (text), merge + flags | ThruLine node, Zoho API, Hamina, AI RF |
| Manual photo assign + sequential close/far pairing | Native Mac app distribution (shared URL is the plan) |
| Word: front matter + per-AP pages; draft/final markers | Full RBAC / multi-tenant relicensing UI |
| Light shared access (owners + Casey admin), deploy on one VM/URL | Managed 24/7 ops beyond a modest retainer |

### Ballpark fixed rebuild (design-partner honesty)

Given salvageable pipeline shells but a **real UX + IDF + template rebuild**:

| Band | When it fits |
|------|----------------|
| **~$6,000–$8,000** | Samples are clean (text IDF, clear folder tree, short AP IDs match), template close to one gold page, desk rename mostly works, shared URL on existing-style VPS |
| **~$8,000–$12,000** | Messier IDF tables, more merge-flag UI, large-doc assembly work, more Nextcloud edge cases, stronger template fidelity |
| **Above ~$12k** | Only if samples prove ugly (scan IDF, weak ID equality, heavy custom Word layout) — re-scope before quoting that high |

**Old ~$2.5k scaffold is not the right frame anymore.** That bought the wrong intake model. Be transparent: rebuild fee replaces/supersedes that mental model; apply an explicit partner discount if you want goodwill — **do not** invent a $20k sticker to “discount” to $10k.

### Retainer + hosting (separate lines)

| Line | Suggested talk track |
|------|----------------------|
| **Retainer** | **~$400–$800 / month** modest: template tweaks, field-map fixes, Nextcloud quirks, training, small changes. Bridge toward ThruLine later without stuffing it into the purchase price. |
| **VM / shared URL** | One small VPS is the right architecture (they live in Nextcloud; no need for three local Mac installs). Infra cost is often **~$20–$60 / mo** raw; if you **manage** it for them, add a clear **hosting/ops** line (e.g. **+$50–$150 / mo** bundled with retainer, or itemized). They already accepted “rent a VM + URL” if needed. |

### Optional later (not in the no-OCR fixed fee)

- Photo OCR assist + batch confirm — separate add-on once rename proves painful (often **+$1.5k–$3k** depending on accuracy expectations; never silent auto-merge).

**Lock dollars only after Josh’s samples.** Use the bands above in Claude to draft SOW language; adjust one band up/down when IDF/`.esx`/folder reality is known.

---

## 3. Large Word output — don’t rely on one 300–400 page shot

Not every job is huge; high AP count ⇒ one page per AP ⇒ can get large. **Correctness and ops** are easier if generation is **chunked**, then assembled (or delivered as a binder).

### Recommended approach

1. **Unit of work = one AP page** (plus a separate **front-matter** render).  
   Validate/generate/retry per AP without redoing the whole book.
2. **Assemble at the end** into one `.docx` *or* ship a **Nextcloud folder binder**:  
   `00_front_matter.docx` + `AP_xxx.docx`… + optional final “Combine to single file” step.
3. **Write progress + draft/final markers** into the Nextcloud project so concurrent users see status; failed AP pages are re-runnable.
4. Keep **manual “Generate”** (Drafter push) — discovery of files ≠ auto-fire a 400-page job.

### Why this is better than one monolithic job

- Failures don’t waste a full run  
- Easier to QA a single AP page against the gold sample  
- Memory/timeout risk drops on a small VM  
- Parallelism later is optional; start sequential

Still deliver **one client Word file** when they need it — assembly is an implementation detail, not a product compromise.

---

## 4. Hosting opinion

- **Shared URL on one VM** = best fit (cost, three Mac users, Nextcloud-centric shop).  
- Local-per-Mac apps = more install/sync pain for little gain.  
- Nextcloud remains the **filesystem of record**; the app is the processor with a bookmarkable URL (Tailscale or similar is fine for v1).  
- Hosting can be **owner-managed VM** or **you-managed** as an extra monthly line — discuss explicitly so rebuild fee ≠ perpetual free ops.

---

## 5. What Claude should produce next (suggested)

1. One-page **SOW** using the no-OCR band + retainer + optional hosting line (mark dollars as provisional until samples).  
2. Rewritten **phase plan** centered on Nextcloud project pick → IDF parse → photo ladder (no OCR) → chunked generator → markers. Park phone capture.  
3. Short **Josh ask list** (tree, `.esx`, IDF, gold page, AP ID equality, who finalizes).  
4. Do **not** start large coding until owner says go.

---

## 6. Quick links

| Doc | Role |
|-----|------|
| `docs/meeting-notes-intake-pivot.md` | Product pivot (truth) |
| `docs/intake-pivot-review.md` | Review of pivot / risks |
| `docs/claude-handoff-post-pivot.md` | This file — Claude briefing + price/hosting/doc strategy |
| Pre-pivot `PHASES` / demo / phone docs | Stale for direction; salvage code only where pivot still needs it |
