# J2 Owner Brief — Current Software & Future State

One-pager for the 4–5pm owner conversation. Demo script:
[`meeting_demo_script.md`](meeting_demo_script.md). Asks:
[`meeting_josh_asks.md`](meeting_josh_asks.md).

---

## Pitch (90 seconds)

A raw Ekahau export is not a deliverable. J2’s clients need a branded Word report
with a narrative spine (Summary → Scope → Criteria → Findings → Recommendations),
explicit thresholds, and **as-built photo documentation** per AP.

This tool ingest field Close/Far photos + `.esx` files into a **Job**, joins them
on **exact AP name**, hard-fails mismatches for the Drafter to resolve, and
generates the layered client deliverable. Phone stays capture-and-upload only.

**Differentiator:** stitching photos to APs by hand is tedious enough that people
skip it. The merge engine makes it free — and loud when names don’t match.

---

## Current vs future

| Horizon | Status | What exists |
|---|---|---|
| **Now (demo)** | Built + UAT PASS on sample fixtures (2026-07-08) | Phone capture web UI, parser, manual merge push, flag list, bulk override reasons, `.docx` generate/download, approve/lock |
| **Activation (needs Josh)** | Shells ready | Real `.esx` schema confirm, gold-standard Word template + branding, Nextcloud creds |
| **Parked (post-v1)** | Explicitly not building | Hamina ingest, AI wall attenuation, self-rendered heatmaps, special photo variants beyond Close+Far, multi-tenant relicensing UI |

Honest framing: you are **not** pitching vaporware. The next wow is *their*
branding and *their* survey file inside machinery that already runs.

---

## Stack (only if asked — 90 seconds)

- **Phone:** browser capture at `/jobs/{id}/capture` — no App Store install
- **Server:** FastAPI + Postgres + Jinja2/HTMX (one language, handoff-friendly)
- **Pipeline:** `parser → merge → generator` (swap Ekahau for Hamina later without rewriting the report)
- **Output:** branded Word via `docxtpl` (branding from config, not engine code)
- **Access:** Tailscale for v1

**Why not React / native app?** Fixed-fee build — zero frontend toolchain, phone
stays light, engine re-skins via `.env`.

---

## Roles (hats, not people)

| Hat | Does |
|---|---|
| **Tech** | Capture Close+Far + AP name; upload. No merge on device. |
| **Drafter / Editor** | Push merge, resolve flags, generate, edit summary/recs, own the doc |
| **Approver** | Sign-off / lock (often Josh) |

Solo job = one person wears all three. Team job = sequential handoff.

---

## What not to oversell

- Placeholder Word prose/branding ≠ final J2 client look
- Phone capture ≠ native iOS/Android app
- Sample `.esx` fixtures ≠ production schema until Josh’s real file lands
