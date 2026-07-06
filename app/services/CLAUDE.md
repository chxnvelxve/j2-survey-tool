# CLAUDE.md — Pipeline Services

This directory holds the three swappable pipeline stages. **Read the matching skill
in `.cursor/skills/` before working on a stage.**

## Contracts (do not break)
- `parser/`   : `.esx` path → `SurveyModel`         (skill: esx-parser)
- `merge/`    : `[SurveyModel]` + photos → `MergedJob` w/ flags  (skill: photo-matching)
- `generator/`: `MergedJob` + template + branding → `.docx`      (skill: docx-generator)

## Hard rules
- **No FastAPI imports here.** Services are framework-agnostic and unit-testable.
- **No cross-stage reaching.** A stage only sees its typed input; it never imports
  another stage's internals. Communicate via the models above.
- **Exact AP name** is the join key. **Hard-fail / flag** on any mismatch — never
  fuzzy-match or silently drop.
- **Branding via config**, never hardcoded, in the generator.
- Parser is **per-file**; a Job with N `.esx` calls it N times.
