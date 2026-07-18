# Claude / Quad handoff — post-pivot (read this first)

**Audience:** Claude / Quad Max (or Codex) helping with pricing, SOW, phase rewrite, or rebuild planning.  
**Owner:** LOG founder; Cursor Pro Plus is the main day-to-day builder; Quad is for heavy planning/QA.  
**Date:** 2026-07-15 (updated after owner pricing / hosting / builder / sales-template decisions)

---

## 0. How to read the repo (critical)

### Source of truth (post-meeting) — read in this order

1. **`docs/meeting-notes-intake-pivot.md`** — product intent after Josh clarified Zoho → Nextcloud intake ([PR #5](https://github.com/chxnvelxve/j2-survey-tool/pull/5), branch `cursor/intake-pivot-meeting-notes-3614`).  
   If missing on checkout, fetch that branch/PR first.
2. **`docs/intake-pivot-review.md`** — owner review of that pivot ([PR #6](https://github.com/chxnvelxve/j2-survey-tool/pull/6)).
3. **This file** — pricing (partner vs list), no builder-hosting, builder split, LOG sales baselines, large-doc approach, and the copy-paste Quad prompt.

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
- `.esx` parser shell, Nextcloud WebDAV shell, branding-in-config, docxtpl generator mechanics, deploy patterns

Reuse **implementation**, not **old product assumptions**. If old docs conflict with the pivot, the pivot wins.

### Do not

- Plan or price phone/PWA tech capture as v1.
- Put ThruLine or Layer-1 expansion in the first SOW.
- Assume OCR is in scope (owner is pricing **without** OCR unless Josh insists later).
- Treat 300–400 pages as every job — upper bound when AP count is high (one page per AP).
- Put **builder-provided hosting** in the SOW (see §4). Owner has home internet only and is not selling hosting yet.
- Sprawl into coding until owner says go.

---

## 1. Product in one paragraph (pivot)

Zoho intake drops files into a **Nextcloud project folder**. Drafters (Josh, Jeff, Casey — MacBooks) open a **shared web app**, **pick a Nextcloud project**, parse `.esx` + IDF PDF + AP photo dump, merge on **short AP ID** (hard-fail / flag, never silent), and generate a branded **Word** deliverable: **IDF/general tables up front**, then **one section/page per AP** (data grid + close + far photos). Draft/final marker files in the project warn concurrent users. No tech UI in this app.

Photo path **without OCR:** prefer desk rename to short AP ID; sequential pairs = close/far; otherwise **manual assign in UI**.

---

## 2. Pricing structure (what the numbers mean)

### Partner band vs stranger / list band

| Frame | Ballpark (no OCR fixed rebuild) | What it is |
|-------|----------------------------------|------------|
| **Josh / design-partner (use this for J2 quote)** | **~$6k–$8k** clean samples; **~$8k–$12k** messier | Already the **fair / mentor-friend zone**. Not a fake list price waiting for a second discount. |
| **Cold commercial / stranger list** | **~$12k–$20k** clean; **~$18k–$28k** messier/polish | Same scope **without** friend discount (~1.5–2.5× partner). Optional if owner shows “list vs partner” in a proposal. |

**Do not** invent a $20k sticker only to “discount” to $10k. If showing both, label them honestly: partner vs list.

**Old ~$2.5k scaffold is obsolete** as the commercial frame — wrong intake model.

### What the fixed rebuild fee covers (no OCR)

| In scope | Out of scope |
|----------|----------------|
| Nextcloud project browse/pick + locate `.esx` / photos / IDF | OCR / sticker reading |
| Parse `.esx`, parse IDF PDF (text), merge + flags | ThruLine, Zoho API, Hamina, AI RF |
| Manual photo assign + sequential close/far pairs | Native Mac app distribution |
| Word: front matter + per-AP pages (chunked generate); draft/final markers | Full RBAC / multi-tenant relicensing UI |
| Light shared access; deploy instructions onto **client-provided** VPS/URL | Builder hosting / home-lab hosting |
| | Managed 24/7 ops (use retainer if needed) |

### Retainer (optional separate line)

**~$400–$800 / month** modest: template tweaks, field-map fixes, Nextcloud quirks, training, small changes. Bridge toward ThruLine later — do not stuff ThruLine into the purchase price.

### OCR (optional later add-on)

**+$1.5k–$3k** typical if rename proves painful; never silent auto-merge. Not in base quote.

### Lock dollars after samples

Provisional until Josh provides: Nextcloud tree, real `.esx`, IDF PDF, gold Word/PDF page, AP ID equality confirmation.

---

## 3. Large Word output — chunk, don’t monolithic-shot

Not every job is 300–400 pages; high AP count ⇒ one page per AP can get large.

1. **Unit of work = one AP page** (+ separate front-matter render).
2. **Assemble at end** into one `.docx`, *or* Nextcloud binder (`00_front_matter.docx` + `AP_xxx.docx`…) then optional combine.
3. Progress + draft/final markers in Nextcloud; failed AP pages re-runnable.
4. Manual Drafter **Generate** — file discovery ≠ auto-fire a huge job.

---

## 4. Hosting — stay out of the SOW for now

**Owner decision:** Do **not** sell or include builder hosting. Owner only has home internet and does not want to host until they can afford proper hosting later.

**Allowed talk track only:**

- App is a **shared URL** architecture (not three local Mac apps).
- **Client rents/provides the VPS** (Josh/Jeff already open to renting a VM), **or** deploy is deferred.
- Nextcloud stays their filesystem of record.
- No builder home-lab hosting line. No managed hosting fee in this SOW.

If deploy is mentioned at all: “runs on a small VM you provide; we hand deploy docs / help once” — not “we host it.”

---

## 5. Who builds what (Cursor vs Quad)

| Role | Tool | Does |
|------|------|------|
| **Main builder** | **Cursor Pro Plus** | Day-to-day implementation in bounded phases (Ask → Plan → Build). |
| **Heavy planner / QA** | **Quad Max** | SOW, phase rewrite, architecture passes, nasty IDF/merge/generator design, QA after a slice or when something fails twice. |

Do **not** make Quad the main continuous coder for this repo — prefer Cursor for tight sequential slices; use Quad for big resets and review.

---

## 6. LOG founder sales baselines

Owner has personal **LOG founder company** baseline docs (pre-sales, sales, SOW/proposal formats, etc.).

**When owner attaches those baselines:**

- **Use the LOG format / structure.**
- **Fill substance from the pivot docs** (this file + meeting notes + review).
- **Do not “fix” or redesign** the sales system unless something is clearly broken — ask before rewriting templates.
- Hand only the templates needed for this engagement (SOW / proposal / retainer), not unrelated company docs.

---

## 7. What Quad should produce in this session (default)

Unless owner asks otherwise:

1. **SOW / proposal** in LOG baseline format (if attached); else clean one-pager.  
   - Partner price band for J2; optional list column.  
   - No OCR in base.  
   - Retainer optional.  
   - **No hosting fee**; client VM or deferred deploy only.  
   - Dollars marked provisional until samples.
2. Rewritten **phase plan** (Nextcloud pick → IDF parse → photo ladder no OCR → chunked generator → markers). Park phone capture.
3. Short **Josh ask list** (tree, `.esx`, IDF, gold page, AP ID equality, who finalizes).
4. **No large coding** until owner says go.

---

## 8. Quick links

| Doc | Role |
|-----|------|
| `docs/meeting-notes-intake-pivot.md` | Product pivot (truth) — PR #5 |
| `docs/intake-pivot-review.md` | Review / risks — PR #6 |
| `docs/claude-handoff-post-pivot.md` | This file — Quad briefing + prompt |
| LOG sales baselines (owner-attached) | Format only; pivot fills content |
| Pre-pivot `PHASES` / demo / phone docs | Stale for direction; salvage code only |

---

## 9. Copy-paste prompt for Quad

Paste into Quad Max. Attach: this file, `meeting-notes-intake-pivot.md`, `intake-pivot-review.md`, and (if using) your LOG SOW/proposal baselines.

```
You are helping me price and re-scope the J2 survey tool AFTER the intake pivot.

Read first, in order:
1) docs/claude-handoff-post-pivot.md
2) docs/meeting-notes-intake-pivot.md
3) docs/intake-pivot-review.md
If I attached LOG founder pre-sales/sales/SOW baselines, use THAT format — fill with pivot substance; do not redesign my sales templates unless something is clearly broken (ask first).

Rules:
- Pivot docs = source of truth for the product.
- Everything written before the pivot is STALE for product direction. Pre-pivot code/patterns may be salvaged (parser → merge → generator, hard-fail flags, Nextcloud shell, docxtpl, branding config) but do not plan from old phone/Job-upload assumptions.
- No OCR in the base quote.
- No builder hosting in the SOW. I only have home internet and am not selling hosting yet. Shared URL on a CLIENT-provided VPS is fine to mention; deferred deploy is fine. Do not price my hosting.
- Partner/design-friend band for J2 is already the discounted zone (~$6–8k clean / ~$8–12k messier). Optional stranger/list band (~$12–20k / ~$18–28k). Do NOT invent a fake high sticker to discount from.
- Old ~$2.5k scaffold frame is obsolete.
- Retainer optional (~$400–800/mo). OCR is a later add-on only.
- Large Word docs: recommend chunked per-AP generation + assemble, not one monolithic 300–400 page job.
- Cursor Pro Plus remains the main builder; you (Quad) do planning/SOW/phase rewrite/QA — do not start a sprawling code rebuild unless I explicitly say go.

Deliver:
1) SOW/proposal (LOG format if baselines attached) with partner pricing for J2, optional list column, no hosting fee, provisional until Josh samples.
2) Rewritten phase plan aligned to the pivot.
3) Short Josh sample/ask list.
Keep it tight and usable in a client conversation.
```
