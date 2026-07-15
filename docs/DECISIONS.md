# Decision Log

Confirmed decisions from design conversations. Append new ones; don't rewrite history.

> **2026-07-15 intake pivot:** See [`meeting-notes-intake-pivot.md`](meeting-notes-intake-pivot.md).
> Decisions 2 and 12 below are **superseded** for the intended product (codebase may
> still reflect the old path until rebuild).

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | Stack: FastAPI + Jinja2 + HTMX, Postgres, docxtpl, Docker Compose | Single language, no JS build step, cheap to maintain post-handoff |
| 2 | ~~Phone = capture-and-upload only~~ **SUPERSEDED** — no tech/phone UI; Zoho → Nextcloud is intake | Josh clarified field capture lives in Zoho |
| 3 | Merge fires on manual push by Drafter | Drafter controls when photos + survey combine |
| 4 | Join key = exact AP name; hard-fail on mismatch | No silent/fuzzy merging; correctness over convenience |
| 5 | Two photos per AP (close + far) | Documentation standard |
| 6 | Override reasons are bulk-applyable w/ autocomplete | Handles 30-AP same-cause case in one action |
| 7 | Multiple `.esx` per Job, parsed per-file | Multi-floor/building sites (warehouses, hospitals) |
| 8 | Attachments modeled as lists | Multiple IDF/LLD fall out for free |
| 9 | Output format = Word `.docx` via repeatable template | J2 hands Word docs to its clients |
| 10 | Branding in config, not engine | Engine re-licensable to other survey shops |
| 11 | Postgres over SQLite | Multi-tenant future without migration pain |
| 12 | ~~Local storage stub now, Nextcloud later~~ **SUPERSEDED for product UX** — Nextcloud is primary working filesystem; local stub OK for dev | Zoho drops assets into Nextcloud project trees |
| 13 | Roles are hats, not people | One person may wear several hats (no Tech hat in v1 pivot) |
| 14 | Primary UX = pick Nextcloud project (no create-Job-then-upload) | Easier ops; Zoho already created the folder tree |
| 15 | Merge joins survey + photos + IDF on short AP ID | Closet/IDF fields and front-matter tables need the PDF |
| 16 | Photo identity ladder: rename → OCR assist → manual; sequential pairs = close/far | Generic Zoho filenames; labels inconsistent across projects |
| 17 | Deliverable = IDF/general front matter + one AP section/page | Matches J2 WLAN validation style; often 300–400 pages |
| 18 | Draft/final marker files in Nextcloud project | Multi-user warning without heavy locking |
| 19 | ThruLine / Layer-1 expansion out of v1 | Keep first run WLAN-doc only; leave room to grow |
| 20 | Price as real fixed rebuild + optional photo-assist + modest retainer; no inflated sticker | Josh asked for realistic pricing + retainer path; owner is design partner toward ThruLine |

## Open / unconfirmed (flag inline where relevant)
- Exact Job status/phase names (partly NotebookLM synthesis — confirm w/ Josh).
- Definition of the four readiness gates.
- Billing-phase split & billable-troubleshooting definition (business, not code).
- Exact Nextcloud subfolder names / project naming scheme.
- Shared web vs local Mac app (cost favors shared web).
- Finalizer rights: all three vs Josh/Jeff only.
- Which Ekahau JSON fields populate antenna height / location / mounting.

## Blockers on Josh / J2
- Real `.esx` file · IDF/closet PDF · Sample deliverable (Word) · Example Nextcloud project tree · Nextcloud access.
