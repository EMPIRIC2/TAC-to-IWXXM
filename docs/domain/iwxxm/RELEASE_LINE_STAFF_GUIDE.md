# IWXXM release lines — operator & staff guide

> **Ticket**: [#847](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/847) · companion to engineering [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808)  
> **Session**: S040 / EV-032 · **Audience**: operators, product owners, domain SMEs, release coordinators  
> **Engineering detail**: [RELEASE_LINE_ADOPTABILITY.md](./RELEASE_LINE_ADOPTABILITY.md)  
> **Policy numbers**: [VERSION_SUPPORT_POLICY.md](./VERSION_SUPPORT_POLICY.md)

## What “IWXXM release line” means (plain language)

An **IWXXM release line** is a year-tagged edition of the XML weather standard (for example
**2025-2** or **2023-1**). Each line has its own rules and schemas. This product supports
**two** lines at a time:

| Role | Today | Meaning for you |
|------|-------|-----------------|
| **Latest (default)** | **2025-2** | What convert/validate use unless you change the picker |
| **Previous** | **2023-1** | Still allowed for legacy partners |
| **Deprecated** | 2021-2 and older | Rejected by the API with a clear error |

We do **not** invent lines. When WMO publishes a new edition, engineering adopts it on a
planned schedule (see handoff below).

## What you need to do when a new line lands

You do **not** edit code or `vendor/` pins. You should:

1. **Read** the release / CHANGELOG note that names the new default and the demoted previous line.
2. **Check the workbench version picker** — default should match “Latest” in the policy table.
3. **Tell stakeholders** which line is default vs still available for 2023-era systems.
4. **Watch for deprecation warnings** — when “previous” is about to drop, allow ~6 months for partners to move (policy).
5. **Escalate** if the picker, defaults, or error messages look wrong (owners below).

## Workbench UX (what “good” looks like)

| Cue | Expected |
|-----|----------|
| Version dropdown | Shows supported lines only (today 2025-2 and 2023-1) |
| Default on fresh load | Latest (2025-2) |
| Saved preference on an old/unsupported value | Migrates to current default (no silent wrong XML) |
| API error for deprecated line | Message lists **supported** versions — share that with partners |

If Examples or product pickers mention a product (e.g. VONA), that is separate from the
**IWXXM version** picker — product = TAC type; version = XML edition year.

## Handoff: engineering → ops / product

When engineering finishes a sync/adopt PR (checklist in
[RELEASE_LINE_ADOPTABILITY.md](./RELEASE_LINE_ADOPTABILITY.md)):

| Engineering delivers | Ops / product uses |
|----------------------|--------------------|
| Updated policy table + CHANGELOG | Stakeholder email / status page blurb |
| Deployed API + static with new default | Smoke: convert one METAR on default; optionally on previous |
| Deprecation date for the line leaving the window | Calendar reminder; partner notice |
| Link to this guide | Training / FAQ without reading ADRs |

**Handoff is incomplete** if only engineers know the new default.

## Escalation

| Symptom | Ask |
|---------|-----|
| Wrong default in UI after a release | Frontend / release owner — prefs or picker options |
| “Version not supported” for a line we still advertise | Backend / F4 config — `SUPPORTED_VERSIONS` vs docs drift |
| Partner XML fails validate after we changed default | Domain + engineering — line mismatch or golden/policy issue |
| Unsure whether US (iwxxm-us) still matches WMO line | Engineering — US pin can lag; do not invent a US-only story |

## Gaps / recommendations (#847)

| Gap | Recommendation | Child? |
|-----|----------------|--------|
| Policy doc is engineer-dense | **This one-pager** is the staff entry; keep VERSION_SUPPORT_POLICY for numbers | Closed by this doc |
| No in-app “Latest / Previous” labels on picker | UX copy child — optional badges | [#854](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/854) |
| CHANGELOG not always linked from UI | Ops runbook: paste CHANGELOG URL in release mail | Process only |
| Deprecation calendar easy to miss | Issue template / reminder when warning window starts | [#855](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/855) |
| Training | 5-minute read of this page + one convert smoke | No new product work |

## Checklist — non-technical adopt / retire

### When latest changes

- [ ] I know the new **default** line name
- [ ] I know which line is still **previous**
- [ ] I can find the CHANGELOG / release note
- [ ] I verified the workbench default once after deploy
- [ ] Stakeholders who need 2023-1 (or the demoted line) were told it remains available

### When a line is deprecated

- [ ] Warning period communicated (~6 months per policy)
- [ ] Partners given migrate-to-default guidance
- [ ] After drop: confirm picker no longer offers the old line
- [ ] Confirm old bookmarks/prefs do not leave users stuck (should migrate to default)

---

*Written 2026-08-04 — S040 / EV-032 T3.2. Engineering SoT remains #808 / RELEASE_LINE_ADOPTABILITY.*
