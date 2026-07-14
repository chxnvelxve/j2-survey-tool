# Owner FAQ — skeptical questions, honest answers

Use before / during the 4–5pm meeting. Do **not** invent unbuilt features.
Sources: [`owner_brief.md`](owner_brief.md), UAT PASS 2026-07-08.

---

## 90-second verbal pitch

Raw Ekahau exports read like the inside of an engineer’s head. J2’s clients need a
branded Word deliverable with a narrative spine, explicit thresholds, and as-built
photos per AP. We built a Job-centered pipeline: phone captures Close+Far against
an exact AP name, the Drafter pushes merge, mismatches hard-fail instead of silent
guesses, and the generator fills a layered report. The machinery works today on
sample data. The next wow is your real `.esx` and gold-standard Word template
inside it.

---

## FAQ (12 bullets)

1. **Is this a native mobile app?**  
   No — phone **browser** capture (`/jobs/{id}/capture`), camera + Close/Far, zero
   App Store install. Intentional: keep the phone light; merge stays on the server.

2. **Why exact AP name, not fuzzy match?**  
   Highest-leverage failure point. Silent wrong joins ship broken as-builts. Loud
   flags the Drafter fixes beat quiet errors clients notice.

3. **What happens when photos don’t match the survey?**  
   Merge hard-fails: photoless APs and orphan photos both surface as Needs
   attention. Drafter bulk-applies override reasons (autocomplete from past reasons).

4. **Does merge run automatically when files land?**  
   No. Manual **Push merge** only — solves partial-handoff / incomplete jobs.

5. **Can one person run a whole job?**  
   Yes. Roles are hats (Tech / Drafter / Approver), not mandatory separate logins.
   v1 assumes Tailscale access, not full RBAC.

6. **Will the Word report look like our real client deliverable?**  
   Structure yes (8-section spine). Branding and drafted prose are placeholders
   until Josh’s gold-standard sample lands — then we swap the template.

7. **Do you need the Ekahau API?**  
   No. We unzip `.esx` (JSON + images) and parse directly.

8. **What about Hamina / other survey tools?**  
   Architecture supports a swappable parser. V1 is Ekahau-only; Hamina is parked.

9. **Where do files live?**  
   Local storage today; Nextcloud WebDAV shell is coded — flip when Josh provides
   URL + app password. No silent fallback.

10. **How is this better than assembling in Word by hand?**  
    Predictable join, flag workflow, photo-per-AP pages, repeatable branding, and
    a readiness gate so incomplete jobs don’t become “final.”

11. **What do you still need from us?**  
    Real `.esx`, matching sample Word deliverable, and threshold rule confirmation
    (per-vertical lookup vs per-job). See [`meeting_josh_asks.md`](meeting_josh_asks.md).

12. **Why not React / a bigger platform?**  
    Fixed-fee, handoff-friendly: one language (Python), Jinja+HTMX, Docker Compose.
    Engine stays re-licensable via branding config — no “J2” hardcoded in pipeline.
