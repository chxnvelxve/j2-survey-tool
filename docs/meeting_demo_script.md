# J2 Owner Meeting — Live Demo Script (4–5pm)

Timed click-through for the wow sequence. Rehearse once cold; pre-stage before
they sit down. Full UAT reference: [`uat_checklist.md`](uat_checklist.md).

**Wow thesis:** *Stitching Close/Far photos to APs by hand is the thing people
skip. We made the join exact, loud on failure, and free — then wrap it in the
layered deliverable.*

---

## Agenda (60 min)

| Minutes | Block | What you do |
|---|---|---|
| 0–5 | Open | One line: raw export ≠ deliverable; this tool produces the client-ready artifact. |
| 5–12 | NotebookLM video | Play ≤7 min video (cue sheet: [`meeting_video_cue.md`](meeting_video_cue.md)). |
| 12–35 | Live demo | Beats 1–5 below (~20 min + Q buffer). |
| 35–45 | Current vs future | Use [`owner_brief.md`](owner_brief.md) table — shell vs activation vs parked. |
| 45–55 | Ask Josh | Three asks from [`meeting_josh_asks.md`](meeting_josh_asks.md). |
| 55–60 | Close | One next action + calendar hold. |

Do **not** open with stack. Owners buy outcomes. Stack is 90 seconds if asked
(see [`owner_brief.md`](owner_brief.md)).

---

## Pre-stage (before they sit down)

Run `./scripts/prep_demo.sh` (or the manual steps it prints), then:

1. Create Job named **Acme Warehouse — Jul 2026**
2. Upload `tests/fixtures/sample_survey.esx` and confirm parsed AP list
3. Desk browser: job detail page
4. Phone (or DevTools phone-width): `/jobs/{id}/capture`
5. Photos ready: `tests/fixtures/gen_photo_close.png`, `gen_photo_far.png`
6. Word ready to open downloads
7. **Fallback:** copy `demo_fallback/Acme_Warehouse_demo_fallback.docx` (created by
   rehearsal) to Desktop — also under `/opt/cursor/artifacts/` in cloud runs

Base URL (local): `http://127.0.0.1:8050` — confirm `GET /health` first.
After prep, `demo_fallback/STAGED_JOB.txt` lists the staged Job detail + capture URLs
(`.esx` parsed; photos still empty for the live hard-fail beat).

---

## Beat 1 — Tech on phone (~4 min)

Open capture page.

**Say:** *Deliberately capture-and-upload only — no merge on the phone.*

- Pick **AP-01-NE** from the datalist (exact name = join key)
- Upload Close + Far
- Optional: type a wrong name once → soft mismatch hint (upload still works; merge catches it)

---

## Beat 2 — Drafter merge hard-fail (~6 min)

On job detail:

- Leave **AP-02-SW** without photos on purpose
- Click **Push merge**
- Show missing-photo / Needs attention flags

**Say:** *Loud failure the Drafter fixes beats a quiet one that ships a broken document.*

---

## Beat 3 — Bulk override (~3 min)

- Multi-select flagged APs
- One reason: **Not surveyed this visit** (or **Ceiling access denied**)
- Status advances; readiness checklist greens

---

## Beat 4 — Generate & open Word (~5 min)

- **Generate report** → **Download report (.docx)**
- Walk narrative spine: Cover → Exec Summary → Scope → Criteria → Findings →
  **AP Inventory with photos** → Recommendations → Appendices
- Point at AP photos: *This is the differentiator — automated as-built.*

**Honesty line (one sentence):** *Prose and branding are placeholder until we drop
in your real client report template.*

---

## Beat 5 — Approve (~1 min)

- Approve → job locks
- Shows Tech / Drafter / Approver hats without RBAC theater

---

## Risk controls

- Never claim placeholder Word is final client look
- Never claim native iOS/Android — say **phone browser capture, zero install**
- Live fail → NotebookLM video + pre-downloaded `.docx`
- Tailscale flaky → local `127.0.0.1:8050` + share screen

---

## One-pager crib (phone Notes)

- Raw export ≠ deliverable → layered Summary / Findings / Appendices
- Join key = **exact AP name**; hard-fail > guess
- Phone = capture only; merge = **manual push**
- Differentiator = Close+Far as-built automated
- Human drafts Exec Summary + Recommendations; engine does the rest
- Need: real `.esx` + sample Word + threshold rule
