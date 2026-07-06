# Domain Model & Glossary

## Entities

### Job
The central container for one survey engagement. Owns everything and moves through
phases.
- Has **many** `SurveyFile` (`.esx`) — multi-floor/building supported.
- Has **many** `Photo` (field AP photos).
- Has **many** `Attachment` (IDF diagrams, LLDs — modeled as a list).
- Has a **status** (see phase model below).
- Produces one (or more) generated `.docx` deliverables.

### SurveyFile
One uploaded `.esx`. Parsed independently into a `SurveyModel`. Multiple survey files
in a Job merge into one AP set; disagreements about the same AP name are **flagged**.

### AP (Access Point)
The join unit. Identified by **exact name**. Carries survey/RF metadata from the
`.esx` and 0–2 matched photos (close + far).

### Photo
A field-captured AP image. Two per AP expected (close, far). Matched to an AP by
exact name. Capture-and-upload only — no phone-side processing.

### Attachment
IDF closet diagrams, Low-Level Designs, etc. A list, not fixed fields.

### Flag
A merge-time problem needing Drafter attention: missing photo, name mismatch,
cross-file AP disagreement. Resolved via an **override reason**.

### OverrideReason
Free text with autocomplete from past reasons. **Bulk-applyable**: select many
flagged APs sharing a cause, apply one reason to all.

## Roles (hats, not people)
- **Tech** — field capture (photos).
- **Drafter/Editor** — uploads `.esx`, pushes the merge, resolves flags, edits,
  signs off. May be Josh, an office coordinator, or the same tech.
- **Approver** — final sign-off.

One person may wear several hats.

## Job status / phase model
A visible six-phase progression (exact names TBD — flag as unconfirmed, these came
partly from NotebookLM synthesis, confirm with Josh):
1. Created / awaiting inputs
2. Inputs uploaded
3. Merged (flags surfaced)
4. Flags resolved
5. Draft generated / in review
6. Approved / delivered

## Readiness gates (proposed — confirm)
Four gates before a deliverable is "ready": all APs matched-or-overridden; required
attachments present; template fields populated; Approver sign-off. Hard-fail on
unresolved AP name mismatches.
