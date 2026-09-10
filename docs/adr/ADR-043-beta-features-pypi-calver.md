# ADR-043: Beta feature surfacing + PyPI CalVer / nightly TestPyPI

> **Status**: Accepted (EV-1150)  
> **Date**: 2026-09-10  
> **Deciders**: User (evolve intake — proceed with recommendations)  
> **Related**: F12–F14; F16–F19; [ADR-034](ADR-034-doks-staging-promote-from-stage.md); [docs/deploy.md](../deploy.md); [docs/context/beta-feedback-pypi-calver.md](../context/beta-feedback-pypi-calver.md)  
> **Sessions**: EV-1150-beta-feedback-pypi-calver

## Context

Dissemination and Send were restored to the operator UI (EV-091) but are still maturing.
Operators need a clear **beta** signal and a one-click path to file feedback on GitHub.

Publishable packages (`tac-validate`, `iwxxm-validate`, `tac2iwxxm`) use semver (`0.2.0` /
`0.3.0`) with infrequent, manual tag publishes. We want date-based versions, promote-aligned
prod publishes, and nightly builds without polluting prod PyPI.

## Decision

### A — Beta surfacing + feedback

1. Operator UI marks **Dissemination** and **Send** (including Convert&Send and Dissemination
   ops) as **beta** with plain-language copy and a link to GitHub Issues:
   `https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/new?labels=beta-feedback`.
2. Root README and GitHub repo About mention beta status and the same feedback path.
3. Issue template `.github/ISSUE_TEMPLATE/beta_feedback.md` + label `beta-feedback`.
4. Agent process: when adding **new product features**, recommend (AskQuestion first option)
   shipping as beta with Issues feedback wiring — see `.cursor/rules/core/beta-feature-rollout.mdc`.
5. Operator-visible strings must not embed internal doc refs (EV-048).

### B — PyPI CalVer + nightly + promote

1. **CalVer** for F12–F14 packages: `YYYY.MM.DD` (PEP 440); same-day rebuilds
   `YYYY.MM.DD.N`; nightlies `YYYY.MM.DD.devN`.
2. Tag patterns remain `{package}-v{version}` (e.g. `tac-validate-v2026.09.10`).
3. **Prod PyPI** stays tag-driven OIDC via `pypi-publish.yml` — no publish on bare branch push.
4. On **`stage`→`main` promote**: bump CalVer on `stage` when packages changed; after merge,
   push package tags from `main` tip (amends ADR-034 release language from “semver” to
   “CalVer for publishable packages”).
5. **Nightly**: scheduled workflow publishes `.devN` builds to **TestPyPI only** (OIDC or
   TestPyPI trusted publisher / token as configured in GitHub Environments).
6. Existing `0.x` releases remain installable; CalVer is forward-looking.

## Consequences

- Trusted Publisher tag filters on PyPI/TestPyPI may need updating for date-shaped tags.
- Promote PR template and `pypi-package-publish.mdc` cite CalVer + nightly.
- UI tests assert beta badge + feedback `href`.
- Agents default new operator surfaces toward beta+feedback unless waived.

## Alternatives considered

| Option | Rejected because |
|--------|------------------|
| Hide Dissemination again | Already restored; beta labeling is clearer |
| Nightly → prod PyPI | Risk of unstable installs; TestPyPI is enough |
| Auto-publish on every `main` push | Bypasses intentional tag/OIDC gate |
| Keep semver | Operator asked for date versioning |

## References

- [Corpus: product] F12–F14, F16–F19  
- [Corpus: tech-spec] / [Corpus: deploy]  
- EV-1150 requirements report  
