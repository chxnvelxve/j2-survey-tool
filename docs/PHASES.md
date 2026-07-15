# Build Phases

Bounded, sequential. **Do not jump ahead.** Each phase is a self-contained work unit
you can drive in Cursor with Ask → Plan → Build → Auto and review before moving on.

> **2026-07-15:** These phases describe the *built* phone/upload-centric path.
> Intended product pivot (Nextcloud project pick, IDF PDF, photo ladder) is in
> [`meeting-notes-intake-pivot.md`](meeting-notes-intake-pivot.md). Rewrite this
> phase plan before more feature work on the old intake model.

Legend: 🔒 = blocked on Josh (real `.esx` / sample deliverable / Nextcloud).

---

## Phase 0 — Scaffold & rails
Goal: the app boots, nothing domain-specific yet.
- FastAPI app factory, config (`app/core/config.py`), settings from env.
- Postgres + SQLAlchemy session (`app/core/db.py`), Alembic init.
- `Storage` interface + `LocalStorage` (`app/core/storage.py`).
- Docker Compose (`web` + `db`), `.env.example`, health-check route.
- Base Jinja2 layout + HTMX wired in.
**Done when:** `docker compose up` serves a health page; migrations run.

## Phase 1 — Jobs & uploads
Goal: create a Job and attach inputs. No pipeline yet.
- `Job`, `SurveyFile`, `Photo`, `Attachment` models + migration.
- Job CRUD + list/detail HTMX views.
- Upload endpoints (esx, photos, attachments) → `LocalStorage`.
- Job status enum (see DOMAIN.md), displayed in UI.
**Done when:** create a Job, upload files, see them listed. Status = "Inputs uploaded".

## Phase 2 — Parser
Goal: read `.esx` → `SurveyModel`. See skill `esx-parser`.
- Unzip `.esx`, read JSON, build normalized `SurveyModel` (APs, names, RF, images).
- Per-file; N files → N parses.
- Unit tests against a fixture `.esx`. 🔒 validate against real J2 `.esx` when available.
**Done when:** upload `.esx`, get a parsed AP list back for a Job.

## Phase 3 — Merge & flags
Goal: join photos to APs, surface flags. See skill `photo-matching`.
- Exact-name join; produce `MergedJob` with per-AP photo slots + flag list.
- Detect: missing photo, name mismatch, cross-file AP disagreement.
- **Manual push** trigger (not automatic).
**Done when:** pushing a Job produces a flag list; matched APs show their photos.

## Phase 4 — Flag resolution UI
Goal: Drafter resolves flags.
- Flag list view; multi-select; **bulk override reason** with autocomplete from past
  reasons.
- Status advances to "Flags resolved" when clean-or-overridden.
**Done when:** 30 flagged APs can be resolved with one bulk action.

## Phase 5 — Generator
Goal: `MergedJob` → `.docx`. See skill `docx-generator`. 🔒 needs sample deliverable.
- `docxtpl` template in `templates_docx/`; branding from config.
- Render endpoint → `storage/output/`; download link.
- Embed AP photos, survey data, attachments.
**Done when:** generate a downloadable Word report from a merged Job.

## Phase 6 — Review, sign-off, polish
- Approver sign-off; readiness gates; regenerate; audit of overrides.
- Deploy hardening; Nextcloud storage impl. 🔒

---

### Deferred / parked (not v1)
AI wall-attenuation inference; Hamina ingest; multi-tenant relicensing UI. Design so
these slot in later (swappable parser, branding-in-config) but **don't build now**.
