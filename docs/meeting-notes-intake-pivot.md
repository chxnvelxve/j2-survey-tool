# Meeting notes — Nextcloud intake pivot (2026-07-15)

> **Read this first if you are a new agent reviewing scope, pricing, or next work.**  
> This document supersedes the phone/tech-capture assumptions in `ARCHITECTURE.md`,
> `DOMAIN.md`, `PHASES.md` (esp. field-capture phases), and older rows in
> `DECISIONS.md`. Those files still describe the *built* codebase; this file
> describes the *intended product* after Josh clarified intake.

Pipeline shape stays: **parser → merge → generator**. Intake and photo identity change.

---

## 1. One-paragraph product statement

Josh’s techs capture photos via a **Zoho intake** form. Zoho places files into a
**Nextcloud project folder** (organized subfolders). This app does **not** do
on-site tech capture. Drafters (Josh, Jeff, Casey — all on MacBooks) open the app,
**pick a project from Nextcloud**, parse `.esx` + IDF PDF + AP photos, merge on
**short AP name**, and generate a long branded **Word** deliverable: general/IDF
tables up front, then **one AP section/page** (data grid + close + far photos).

---

## 2. What is changing vs the current repo

| Old assumption (built / documented) | New assumption (Josh / owner) |
|-------------------------------------|-------------------------------|
| Phone/PWA tech uploads into a Job | **No tech UI.** Zoho → Nextcloud is intake |
| Create Job, then upload `.esx` / photos / attachments | **Pick existing Nextcloud project** (dropdown / browse) |
| Photos named for exact AP match (or flag) | Photos often **generic** (`file_0001`…); folder organized by Zoho |
| IDF/LLD as generic attachments | **Parse IDF PDF** (readable text); closet + tables; short AP ID + hostname |
| Merge = survey APs ↔ photos | Merge = survey APs ↔ **photos** ↔ **IDF rows** (short AP ID) |
| Deliverable ~ template sections | **Front matter (all IDF/general tables)** + **one page per AP** (~300–400 pages) |
| Storage: local stub, Nextcloud later | Nextcloud is **the** working filesystem for inputs *and* draft/final outputs |
| Roles include Tech | Roles: drafters/finalizers only (Josh & Jeff owners, Casey admin hire) |

**Owner is OK scrapping most of the initial upload/Job-centric design** and
restructuring around Nextcloud project pick + parse/merge/generate.

**Still keep:** three-stage pipeline, exact AP join / hard-fail philosophy, Word
via docxtpl, branding in config, FastAPI + Jinja/HTMX + Postgres stack (unless a
later pricing decision chooses pure local Mac apps — see §7).

---

## 3. Users and access

| Person | Location | Machine | Role notes |
|--------|----------|---------|------------|
| Josh | Paducah, TX | MacBook | Co-owner; drafter/finalizer |
| Jeff | Dallas | MacBook | Co-owner; drafter/finalizer |
| Casey | (unconfirmed) | MacBook | New admin hire; drafter/finalizer unless owners restrict final sign-off |

- They may work **at the same time**.
- Prefer **easiest / cheapest**: likely one **shared web app** + Mac shortcut/bookmark.
  Pure local Mac apps are acceptable if cheaper, but three installs + Nextcloud
  sync is usually *more* ops cost than one small VPS/Tailscale URL.
- If shared auth: Josh & Jeff = owners; Casey = admin.
- Assume all three can finalize unless Josh/Jeff say otherwise later.

**Concurrency / status files:** When generate (or a major step) runs, write a
marker/file into the Nextcloud project (draft vs final). If another user opens
that project and the marker exists, **flag**: who/what already created draft or
final. Do not silently overwrite without warning.

---

## 4. Nextcloud / Zoho intake (as understood)

- Zoho intake creates (or instructs Nextcloud to create) a **project folder** and
  **subfolders** per asset type.
- App must **discover** a project and locate:
  - Ekahau `.esx` (survey)
  - AP photo dump
  - IDF / closet PDF (and related IDF imagery in some cases; Zoho can name *some*
    files, e.g. front-of-rack, but not all)
- Exact subfolder names: **unknown until Josh provides a real project tree.**
- **No document upload UI required** in v1 if everything is referenced from
  Nextcloud. (Local stub may remain for offline/dev.)

---

## 5. AP photos — naming ladder

**Reality:** Flat folder of generic names (`file_0001`, etc.). Not tech-inserted
in this app.

**Pairing rule (owner preference):** Photos arrive in **batches / sequential
pairs** — `0001` = close, `0002` = far for the *same* AP; then `0003`/`0004` for
the next AP, and so on. That solves **close vs far**, not **which AP**.

**Identity ladder (prefer in this order):**

1. **Best:** Desk user (or future Zoho improvement) **manually renames** files to
   short AP ID (+ close/far suffix if possible).
2. **Second:** In-app assisted matching (open picture, **OCR** label/hostname/MAC
   when present, suggest match against parsed AP list from `.esx`).
3. **Last:** Manual assign in UI.

**Critical constraint:** Physical labels are **not consistent** across projects —
hostname, MAC, serial, or *no* readable ID. OCR is assistive; **never silent
auto-merge**. Hard-fail / flag philosophy remains. Suggested matches should be
constrained to the Job’s known AP name list when possible.

**Do not confuse:** “Batch accept OCR suggestions” ≠ tech uploading photos. It
only means drafters confirm identity in batches instead of renaming 100 files in
Finder one-by-one.

---

## 6. IDF PDF and deliverable shape

**IDF PDF**

- Readable text (not scan-only — confirm with sample).
- Has **short AP ID** and **longer AP hostname**.
- Short AP ID should match Ekahau AP name and (ideally) photo names.
- Closet (and related switch/patch data as available) feeds merge.
- **Full IDF/general content** also feeds a **front section** of the Word doc
  (tables: AP naming, IDF patch, etc.) — not only the per-AP closet cell.

**Per-AP page fields (from sample page shown in meeting)**

| Field | Source |
|-------|--------|
| AP NUMBER | `.esx` |
| MAKE / MODEL | `.esx` |
| ANTENNA HEIGHT | `.esx` / survey JSON (validate with real file) |
| LOCATION | `.esx` / survey JSON (validate with real file) |
| ANTENNA TYPE | `.esx` |
| MOUNTING TYPE | `.esx` / survey JSON (validate with real file) |
| CLOSET | IDF PDF |
| Close photo | AP photo pair |
| Far photo | AP photo pair |

Sample visual reference discussed: WLAN Validation–style page (header branding +
client logo, blue data grid, two photos). Branding/template details deferred until
gold deliverable arrives; client logos may live in the project folder and be
referenced at generate time.

**Output:** Word `.docx` still. Large docs (300–400 pages) are expected because of
one-AP-per-section layout.

---

## 7. Future (explicitly not v1)

- ThruLine: this app should eventually be connectable as an external app node;
  **do not build ThruLine integration in v1.**
- Broader Layer-1 documentation (switches, routers, etc.): design data model so
  “project → parsed assets → merged entities → generated sections” can grow;
  **keep v1 WLAN AP documentation only.**
- Zoho API integration: out of scope if Nextcloud already has the files.

---

## 8. Blockers (waiting on Josh)

1. Real J2 `.esx`
2. Real IDF / closet PDF
3. Gold-standard deliverable (Word or PDF to mirror)
4. Example Nextcloud project tree (folder names + sample generic photo dump)
5. Confirm short AP ID string equality across the three sources
6. Auth preference confirmation (shared web vs local) after pricing discussion

---

## 9. Pricing / commercial notes (owner intent — not a signed quote)

**Context:** Original mental model was a small fixed-fee scaffold (~$2.5k class).
Josh asked to **restructure pricing**, build out the real app, give a **realistic**
price, and asked about a **retainer**. Owner does **not** want a fake $20k list
with a “discount” to $10k. Wants a solid product, fair discount as design partner,
and a path into **ThruLine** later.

**Suggested commercial frame for discussion (refine after samples arrive):**

| Line | What it covers | Notes |
|------|----------------|-------|
| **Fixed rebuild** | Nextcloud project pick, parse `.esx`, parse IDF PDF, merge + flags, Word generator (front matter + per-AP pages), draft/final markers, basic shared auth/roles, deploy | Core product Josh needs |
| **Photo assist (optional)** | Sequential pair logic + OCR suggest + batch confirm UI | Only if desk rename isn’t reliable enough |
| **Retainer (monthly, modest)** | Template tweaks, field-mapping fixes, Nextcloud quirks, training, small change requests | Natural bridge toward ThruLine; avoids inflating purchase price |

**Pricing principles for the next conversation**

- Quote **real effort**, then apply a **partner discount** — do not invent a high
  sticker to discount from.
- Shared web app on existing VPS/Tailscale pattern is usually the **lowest total
  cost** for three Mac users vs three maintained local apps.
- Do not price ThruLine integration into this SOW.
- Lock numbers only after §8 samples reduce unknown OCR/IDF/template risk.

**Rough scope drivers (why this is more than the old $2.5k scaffold)**

- Nextcloud as primary UX (browse/pick project, read subfolders, write status/output)
- IDF PDF parsing + front-matter tables
- Photo identity ladder (rename / OCR / manual) + sequential close/far pairs
- Very large Word generation (performance + template fidelity)
- Light multi-user draft/final coordination

*(Numeric quote intentionally omitted here — owner + next agent should set dollars
after reviewing samples and rebuild plan.)*

---

## 10. Recommended next steps for a review agent

1. Walk owner through §§2–6 and confirm nothing material is wrong.
2. Propose a **rewritten phase plan** that parks/scrapes phone capture and
   centers Nextcloud project intake (do not implement until owner says go).
3. Draft a **one-page SOW + price + retainer** options for Josh (good / better /
   photo-assist add-on).
4. List exact questions for Josh when samples arrive (folder tree, AP ID
   equality, finalize rights).
5. When coding starts: bounded slices — docs/phase rewrite first, then storage
   project-index, then IDF parser, then photo ladder, then generator template.

---

## 11. Open questions (short list)

1. Exact Nextcloud subfolder names and project naming scheme?
2. Is short AP ID **character-identical** in `.esx`, IDF PDF, and renamed photos?
3. Shared web (preferred for cost) vs local Mac app — final call after pricing?
4. Finalizer = all three, or Josh/Jeff only?
5. Which Ekahau JSON fields actually populate height / location / mounting?
6. Is the IDF PDF text-extractable end-to-end or partly image-based?

---

## 12. Source

Captured from owner ↔ agent discovery chat (Cloud Agent), 2026-07-14/15, after
Josh clarified Zoho → Nextcloud intake and sample AP-page deliverable layout.
Owner asked that a new cloud agent be able to load this for review of changes,
pricing, and next checks.
