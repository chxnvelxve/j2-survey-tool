# Architecture

> **Scope pivot (2026-07-15):** Intended intake is Zoho → Nextcloud project pick,
> not phone/tech upload. Read
> [`meeting-notes-intake-pivot.md`](meeting-notes-intake-pivot.md) before planning
> new work. Diagrams below may still describe the *currently built* upload-centric
> flow until the rebuild lands.

## Overview

Three-stage, swappable pipeline wrapped in a web app. The web app manages **Jobs**;
the pipeline turns a Job's inputs into a deliverable.

```
┌─────────────────────────────────────────────────────────────────┐
│                          Web App (FastAPI)                        │
│                                                                   │
│  Phone capture  ──▶  Job (inputs)  ──▶  Drafter UI (HTMX)         │
│   (web form/PWA)          │                    │                  │
│                           │                    │ manual "push"    │
│                           ▼                    ▼                  │
│                   ┌──────────────────────────────────┐           │
│                   │            PIPELINE               │           │
│                   │  parser → merge → generator       │           │
│                   └──────────────────────────────────┘           │
│                           │                                       │
│                           ▼                                       │
│                    client-ready .docx                             │
└─────────────────────────────────────────────────────────────────┘
```

## Stage contracts

Keep these boundaries clean. Each stage takes typed input and returns typed output;
no stage reaches into another's internals.

### 1. Parser — `app/services/parser/`
- **In:** path to one `.esx` file.
- **Out:** `SurveyModel` (normalized: list of APs with names, positions, radio/RF
  metadata, floor plans, referenced images).
- **Notes:** `.esx` is a ZIP of JSON + images. Parse directly — no Ekahau API.
  One call per file; a Job with N `.esx` files calls the parser N times.

### 2. Merge — `app/services/merge/`
- **In:** list of `SurveyModel` (from all the Job's `.esx` files) + the Job's field
  photos + override reasons.
- **Out:** `MergedJob` — APs each with 0/1/2 matched photos, plus a list of **flags**
  (missing photo, name mismatch, cross-file AP disagreement).
- **Join key:** exact AP name. **Hard-fail philosophy:** never guess. Unmatched →
  flag, not silent drop/merge.

### 3. Generator — `app/services/generator/`
- **In:** `MergedJob` + a `.docx` template + branding config.
- **Out:** rendered `.docx` in `storage/output/`.
- **Engine:** `docxtpl` (Jinja2-in-Word). Branding (logo, company name, colors) comes
  from config so the same engine re-skins for other clients.

## Why this shape

- **Swappability:** adding a Hamina parser = a new parser that emits the same
  `SurveyModel`. Merge and generator don't change.
- **Re-licensing:** branding lives in config, not engine code.
- **Multi-file for free:** parser is per-file, attachments are lists → multi-floor /
  multi-building sites need no special-casing.

## Storage abstraction — `app/core/storage.py`

Define a `Storage` interface (`save`, `open`, `url_for`). Ship a `LocalStorage`
implementation now (`storage/` dir). A `NextcloudStorage` implementation lands later
without touching call sites. **Do not scatter `open()`/path logic through the app.**

## Data flow of a Job

1. Tech captures AP photos on phone → uploaded to the Job (capture-and-upload only).
2. Drafter uploads one+ `.esx` files and any IDF/LLD attachments.
3. Drafter hits **push** → parser runs per file → merge runs → flags surface in UI.
4. Drafter resolves flags (bulk override reasons w/ autocomplete).
5. Drafter generates the `.docx`, reviews, edits, signs off.

## Deployment

Docker Compose: `web` (FastAPI/uvicorn), `db` (Postgres), reverse proxy. Access via
Tailscale / public URL. Keep the compose file simple — this is handed off.
