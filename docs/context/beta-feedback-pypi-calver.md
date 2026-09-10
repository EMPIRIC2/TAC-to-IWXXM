# Context — beta feedback UX + PyPI CalVer / nightly

**Session:** EV-1150-beta-feedback-pypi-calver  
**Date:** 2026-09-10  
**Orchestrator:** evolve (standard)

[Corpus: product] [Corpus: tech-spec] [Corpus: tests] [Corpus: adr]

## Problem

Operators see Dissemination / Send as fully production surfaces. We want them labeled **beta**, with an obvious path to file GitHub feedback. Separately, publishable packages (F12–F14) should track calendar versions, publish on promote to `main`, and build nightlies to TestPyPI.

## Inventory (current)

| Area | State |
|------|--------|
| Dissemination UI | Restored (`operatorDisseminationUi.destinationsEnabled: true`); README still says “hidden” |
| Beta UI pattern | None — closest: soft-preview pills / shadcn `Badge` |
| Feedback Issues | One IWXXM deprecation template only; no `beta-feedback` |
| PyPI publish | Tag-driven OIDC `.github/workflows/pypi-publish.yml`; versions 0.2.0 / 0.2.0 / 0.3.0 |
| Nightly PyPI | Absent (other nightlies: load-tests, mutation, vendor-sync) |
| Promote checklist | Semver bumps + optional PyPI tags after merge |

## Locked decisions (intake + “proceed with recommendations”)

1. Beta-label **Dissemination** + **Send** (Convert&Send / Disseminate / Dissemination ops).
2. Feedback: label `beta-feedback` + issue template; in-app link to `issues/new?labels=beta-feedback`.
3. Docs: root README + GitHub repo About (“gh-overview”).
4. Process: new `.cursor` rule (+ skill note) — recommend beta tag + Issues feedback for new product features.
5. CalVer `YYYY.MM.DD` (+ `.N` same-day); nightlies `YYYY.MM.DD.devN` → **TestPyPI only**.
6. Production PyPI: date tags on **`stage`→`main` promote** (keep OIDC; no branch-push publish).

## Entry interview disposition

E0–E8 covered by evolve intake + operator “proceed with recommended next steps.” UI preview: **deferred** to build (no local preview required for badge/copy AC). Memory retrieve: no matches (fail-open).

## Must not break

- Dissemination egress / BYOC memory-only creds  
- EV-048: no internal doc refs on operator surfaces  
- OIDC trusted publishing  

## Downstream

Requirements → draft-docs (feature-list / deploy / config-spec / ADR / decisions / rules) → feasibility → tech-plan → documenting verify → **gate**.
