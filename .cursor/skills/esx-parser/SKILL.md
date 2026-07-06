# Skill: .esx Parser

**Use when** implementing or debugging anything that reads Ekahau `.esx` files
(`app/services/parser/`).

## What an .esx is
A `.esx` is a **ZIP archive** containing JSON files + image assets. You do **not**
need the Ekahau API — unzip and read the JSON directly.

Typical contents (names/structure vary by Ekahau version — inspect the real file):
- `accessPoints.json` — AP records (id, name, model, vendor).
- `simulatedRadios.json` / `measuredRadios.json` — RF/radio data per AP.
- `floorPlans.json` — floor plan metadata + referenced image files.
- `project.json` — project-level metadata.
- image assets (floor plan bitmaps, etc.).

⚠️ Structure is **unverified against a real J2 file** — treat field names as
provisional. First step on a real `.esx`: unzip and print the JSON key structure.

## Job
Emit a normalized `SurveyModel` regardless of Ekahau version quirks:
```
SurveyModel:
  project: {name, ...}
  floors: [{id, name, image_ref}]
  aps: [{name, model, vendor, floor_id, x, y, radios:[{band, channel, tx_power, ...}]}]
```
- **AP name is sacred** — it's the join key for merge. Preserve it exactly, no
  trimming/casing changes that could break matching.
- One `.esx` → one `SurveyModel`. A Job with N files parses N times; merge combines.

## Rules
- Never mutate the uploaded file. Extract to a temp dir, read, clean up.
- Be defensive: missing/renamed keys → raise a clear parse error, don't guess.
- Don't depend on Ekahau being installed or online.

## Debug recipe
1. `unzip -l file.esx` to inventory.
2. Pretty-print each JSON's top-level keys.
3. Map real keys → `SurveyModel` fields; update the parser + a fixture test.
