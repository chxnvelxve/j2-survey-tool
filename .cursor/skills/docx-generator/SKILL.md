# Skill: DOCX Generator

**Use when** implementing/debugging `app/services/generator/` and templates in
`templates_docx/`. 🔒 Modeling the template well needs Josh's **sample deliverable** —
flag assumptions until it arrives.

## Engine
`docxtpl` (Jinja2 syntax inside a real `.docx`) + `python-docx` for anything docxtpl
can't express. Template lives in `templates_docx/`.

## Job
`MergedJob` + branding config + template → rendered `.docx` in `storage/output/`.

## Template conventions
- Jinja tags in the Word file: `{{ project.name }}`, loops over APs, etc.
- Insert AP photos with docxtpl's `InlineImage`. Two per AP (close, far).
- **Branding from config** — logo, company name, colors, header/footer come from
  settings, NOT hardcoded, so the same engine re-skins for other survey shops.
- Layered reader model: plain-language summary section for non-technical readers +
  RF-detail section for specialists.
- Attachments (IDF/LLD) are a list — loop, don't assume one.

## Rules
- Deterministic output — same Job renders the same doc.
- Fail loudly if a required field/photo is missing (tie to readiness gates), don't
  emit a half-filled doc silently.
- Keep the template swappable: generator shouldn't hardcode section structure that
  belongs in the `.docx`.

## Debug recipe
1. Render with a fixture `MergedJob`.
2. Open the `.docx`, check tags resolved, images placed, branding applied.
3. Diff against Josh's sample deliverable once available.
