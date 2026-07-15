# CLAUDE.md — J2 Wireless Site Survey Automation Tool

> This file is the top-level context for any AI agent (Cursor, Claude) working in
> this repo. Read it before writing code. Nested `CLAUDE.md` files add
> directory-specific rules and override this file where they conflict.
>
> **2026-07-15:** Product intake pivoted to Zoho → Nextcloud (no tech/phone UI).
> Start with [`docs/meeting-notes-intake-pivot.md`](docs/meeting-notes-intake-pivot.md)
> before planning rebuilds, pricing, or phase changes.

## What this project is

A VPS-hosted web app that automates the pipeline from **field AP photo capture →
Ekahau survey ingestion → polished, client-ready Word (.docx) deliverable**.

The customer is **J2 Communications (J2)**, a 25-year wireless services firm. J2's
techs capture AP photos in the field; a Drafter/Editor merges those photos with
Ekahau survey data and produces a branded Word report that J2 hands to *its* own
customers.

The core engine is owned by the builder and designed to be **re-licensed** to
other survey shops by changing branding variables — so keep branding, client
names, and J2-specifics out of the engine and in config.

## The pipeline (the heart of the app)

Three swappable stages. Keep them decoupled — each stage has a clean input/output
contract so a stage can be replaced (e.g. add Hamina support) without touching the
others.

```
  [.esx files]  ──parser──▶  [normalized survey model]
  [field photos] ─────────▶                │
                                           ▼
                                        merge  ──▶  [matched Job model + flags]
                                           │
                                           ▼
                                      generator  ──▶  [client-ready .docx]
```

1. **Parser** (`app/services/parser/`) — reads each `.esx` (a ZIP of JSON + images),
   emits a normalized survey model. One parser call per file. Never depends on the
   Ekahau API.
2. **Merge** (`app/services/merge/`) — joins AP photos to survey APs on **exact AP
   name**. Hard-fails / flags on mismatch; never silently merges.
3. **Generator** (`app/services/generator/`) — fills a Word template
   (`templates_docx/`) via `docxtpl` to produce the deliverable.

## Core domain model

- **Job** — the server-side container for one survey engagement. Holds all inputs
  (one *or more* `.esx` files, field photos, IDF/LLD attachments) and moves through
  visible phases. A Job can have **multiple `.esx` files** (multi-floor/building);
  each is parsed independently and their AP lists merge into one set.
- **AP (Access Point)** — matched between survey data and photos by **exact name**.
  Two photos per AP (close + far).
- **Roles are hats, not people** — Tech (field capture), Drafter/Editor (merge,
  error resolution, editing, sign-off), Approver. One person may wear several.

## Non-negotiable design rules

1. **Hard-fail on AP name mismatch.** If a photo's AP name doesn't match a survey
   AP (or two `.esx` files disagree about the same AP), **flag it — never guess or
   silently merge**. The Drafter resolves flags explicitly.
2. **Override reasons are bulk-applyable.** The Drafter multi-selects flagged APs
   sharing a root cause and applies one reason to all. Past reasons appear as
   autocomplete suggestions ("Ceiling access denied," "AP swapped post-survey"),
   not a rigid enum.
3. **Phone is capture-and-upload only.** No on-device merging or processing.
4. **Merge fires on manual push** by the Drafter, not automatically.
5. **Attachments are lists, not single fields** (multiple IDF closets / LLDs fall
   out for free).
6. **Engine stays brandable.** No hardcoded "J2" in engine logic — use config.

## Stack

- **Backend:** Python 3.11+, FastAPI
- **Views:** Jinja2 templates + HTMX (no React, no npm build step)
- **DB:** PostgreSQL (via SQLAlchemy + Alembic migrations)
- **Docx generation:** `docxtpl` / `python-docx`
- **Deploy:** Docker Compose on a VPS
- **Storage:** local storage stub now; Nextcloud integration later (blocked on Josh)

Single language (Python), single repo, no separate frontend toolchain. This is a
~$2,500 build — resist adding infrastructure that costs maintenance after handoff.

## Known blockers (waiting on Josh / J2)

- A **real `.esx` file** from J2 (currently using sample `.esx` from another project).
- A **sample deliverable** (the Word report J2 currently hands clients) to model the
  template on.
- **Nextcloud access** for real storage (local stub unblocks dev today).

Flag inline in code/docs anywhere a decision depends on these, rather than assuming.

## How to work in this repo (Cursor 3 workflow)

The builder drives Cursor with **Ask → Plan → Build → Auto**. Support that:

- In **Ask/Plan**, produce a written plan and confirm scope before editing files.
- Keep changes **bounded and sequential** — one topic/phase at a time, not sprawling
  multi-area edits. (The builder has ADHD and explicitly wants tight, self-contained
  work units.)
- Prefer small, reviewable diffs. Show the plan; wait for go-ahead before large edits.

## Phases

See `docs/PHASES.md`. Do not jump ahead — Phase 1 is scaffold + Job CRUD + upload,
**not** the full pipeline.

## Where things live

- `app/api/` — FastAPI routers (thin; delegate to services)
- `app/services/` — the three pipeline stages (parser / merge / generator)
- `app/models/` — SQLAlchemy models + Pydantic schemas
- `app/core/` — config, db session, storage abstraction
- `app/templates/` — Jinja2 (server-rendered HTMX views)
- `templates_docx/` — the Word `.docx` template(s) for output
- `.cursor/rules/` — Cursor rule files (always/auto-attached guidance)
- `.cursor/skills/` — reusable skill docs for the hard sub-problems
- `docs/` — architecture, phases, domain, decisions
