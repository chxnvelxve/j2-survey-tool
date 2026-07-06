# Skill: Photo ↔ AP Matching (Merge)

**Use when** implementing/debugging `app/services/merge/`.

## Job
Join field photos to survey APs and produce a `MergedJob` with a **flag list**.

```
MergedJob:
  aps: [{ap_name, survey_data, photos:{close?, far?}, status}]
  flags: [{ap_name, type, detail, override_reason?}]
```

## The one join rule
**Exact AP name.** Photo AP name must equal survey AP name character-for-character.

## Flag types (never silently resolve)
- `MISSING_PHOTO` — AP has <2 photos.
- `NAME_MISMATCH` — a photo's AP name matches no survey AP.
- `CROSS_FILE_DISAGREEMENT` — two `.esx` files describe the same AP name
  inconsistently.
- `ORPHAN_PHOTO` — photo with no corresponding AP at all.

## Hard-fail philosophy
Never fuzzy-match, auto-correct casing, or drop unmatched items quietly. Every
mismatch becomes a **flag** the Drafter resolves. Correctness > convenience.

## Override reasons (bulk)
- Drafter multi-selects flagged APs sharing a cause → applies **one** reason to all.
- Reason is free text with **autocomplete** from previously used reasons (e.g.
  "Ceiling access denied", "AP swapped post-survey"). No rigid enum.
- An overridden flag is resolved-with-reason, not deleted — keep it for the audit.

## Trigger
Merge runs on the Drafter's **manual push**, never automatically.
