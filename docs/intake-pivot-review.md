# Intake pivot review (for owner)

**Date:** 2026-07-15  
**Source of truth used:** [`meeting-notes-intake-pivot.md`](meeting-notes-intake-pivot.md) on branch `cursor/intake-pivot-meeting-notes-3614` ([PR #5](https://github.com/chxnvelxve/j2-survey-tool/pull/5)), plus the discovery transcript that produced it.  
**Deliberately ignored as stale for product direction:** `docs/PHASES.md` body, phone-capture / Job-upload architecture, and the pre-meeting demo pack (`meeting_*`, `owner_brief.md` on `cursor/j2-meeting-demo-prep-fac6`). Those describe the *built* app, not the intended one after Josh/Jeff.

---

## Verdict

The pivot notes are **good enough to price and re-scope against**. They correctly kill the phone/tech UI assumption, center Zoho → Nextcloud project pick, expand merge to include IDF, and redefine the Word deliverable as front-matter tables + one page per AP.

What is *not* ready yet: a rewritten phase plan, a dollar quote, or coding. Samples from Josh still drive the biggest unknowns (folder tree, IDF extractability, AP ID equality, real `.esx` field coverage, gold template).

---

## What changed (one screen)

| Keep | Scrap / rework |
|------|----------------|
| `parser → merge → generator` contracts | Phone / PWA tech capture UI |
| Exact join + hard-fail / flag (no silent merge) | Create-Job-then-upload as primary UX |
| Word via `docxtpl`, branding in config | Assumptions that photos arrive AP-named |
| FastAPI + Jinja/HTMX + Postgres (shared web preferred) | Treating Nextcloud as “later activation only” |
| Manual Drafter control (don’t auto-merge) | Tech role in v1 |
| Close + far photo pair concept | Current ~8-section narrative template as the gold shape |

**New product center:** Drafter picks a Nextcloud project → app finds `.esx` + photo dump + IDF PDF → parse/merge/flag → generate large Word doc → draft/final markers so Josh/Jeff/Casey don’t clobber each other.

---

## What the built codebase still buys you

Not a full rewrite from zero. Salvageable:

- **`.esx` parser shell** + schema guard / fixtures (still needs real J2 file).
- **Merge + flag + bulk override reason** pattern (extend to IDF + photo identity flags).
- **Nextcloud WebDAV storage shell** (becomes primary UX, not a flip switch).
- **Generator / branding config / deploy** (template contract must be rewritten for front matter + per-AP pages).

Expect to **park or gut** Job upload + capture screens as the main path. Domain model likely shifts from “Job you create and fill” toward “Nextcloud project you open and process.”

---

## Gaps / risks in the pivot notes (challenge these in review)

1. **Photo identity is the biggest delivery risk.** Sequential pairs solve close vs far only. Which-AP still depends on rename, OCR assist, or manual assign — and labels are inconsistent (hostname/MAC/serial may be absent or wrong). Price OCR as optional add-on, not core path assumption.
2. **“Short AP ID” equality across three sources is unproven.** If Ekahau name ≠ IDF short ID ≠ renamed photo stem, merge flags explode. Confirm with one real project before locking SOW dollars.
3. **IDF PDF parser is a new stage-class problem.** Notes assume readable text. If pages are scan/image-heavy, scope jumps. Treat sample PDF as a go/no-go for “parse tables” vs “attach + manual closet field.”
4. **300–400 page Word docs** are a performance/template risk (docxtpl + many InlineImages). Plan for chunked generation / memory testing; don’t under-quote this.
5. **Manual merge push** is still listed as a standing decision and was never re-decided after project-pick intake. Recommend: keep an explicit Drafter “Run merge / Generate” action even if inputs are auto-discovered.
6. **Auth is light-handwaved.** Three concurrent Mac users + draft/final markers is enough for v1 if Tailscale + simple roles; don’t invent full RBAC in the rebuild quote.
7. **ThruLine / Layer-1** correctly parked — keep them out of the SOW so the quote stays honest.
8. **Pre-meeting “asks” list is stale.** Threshold/profile confirmation and “phone capture demo” framing are no longer the close. New asks = samples in § Blockers below.

---

## Commercial frame (review, not a quote)

Notes correctly reject fake high-sticker discounting. Use three lines:

| Line | Include | Hold until samples |
|------|---------|--------------------|
| **Fixed rebuild** | Nextcloud project pick, `.esx` parse, IDF parse (if text), merge+flags, Word front matter + per-AP pages, draft/final markers, light shared auth, deploy | Exact IDF complexity, template fidelity |
| **Photo assist (optional)** | Sequential pair logic + OCR suggest + batch confirm | Whether desk rename is good enough |
| **Modest retainer** | Template tweaks, field-map fixes, Nextcloud quirks, training, small changes; ThruLine conversation later | Not a substitute for the rebuild fee |

**Why this is above the old ~$2.5k scaffold:** Nextcloud-primary UX, IDF parsing + front tables, photo identity ladder, large doc generation, light multi-user coordination. The old fee bought the pipeline shell under the *wrong* intake model.

Do not put dollars in the notes until one real project tree + IDF + `.esx` + gold page reduce OCR/IDF/template risk. Then quote real effort and apply an explicit partner discount if you want — not a manufactured list price.

---

## Confirm with Josh (short list)

Use this instead of the old demo-prep asks:

1. Example **Nextcloud project tree** (folder names + generic photo dump).
2. Real **`.esx`** + matching **IDF/closet PDF** + **gold Word/PDF page**.
3. Is **short AP ID character-identical** in Ekahau, IDF, and (when renamed) photos?
4. Who may **finalize** — all three, or Josh/Jeff only?
5. Shared **web URL** (preferred) vs local Mac app — after they see price.
6. Is the IDF PDF **text-extractable** end-to-end?

---

## Recommended next steps (order)

1. **Merge/keep PR #5** (pivot notes + decision supersessions) as the living product brief.
2. **Do not code** the rebuild until you lock SOW shape with Josh on samples.
3. Rewrite **phase plan** around: project index → IDF parser → photo ladder → generator template → draft/final markers. Park phone capture.
4. Draft a **one-page SOW** with good / better / photo-assist + retainer options (dollars after samples).
5. When coding: one bounded slice at a time; first slice is docs/phase rewrite + Nextcloud project browse, not OCR.

---

## Documents to trust vs ignore right now

| Trust for direction | Built-state only (do not plan from) |
|---------------------|-------------------------------------|
| `docs/meeting-notes-intake-pivot.md` (PR #5) | `docs/PHASES.md` phase bodies |
| Updated rows in `docs/DECISIONS.md` on that PR (14–20 + superseded 2/12) | Phone capture / Job upload UX docs |
| This review | `meeting_demo_script.md`, `owner_brief.md`, old “three asks” |

`ARCHITECTURE.md` / `DOMAIN.md` / `CLAUDE.md` on main still describe the built upload path; PR #5 only adds warning banners. Treat them as historical until rewritten.
