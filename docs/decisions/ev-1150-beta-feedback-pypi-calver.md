# EV-1150 decisions

**Session:** EV-1150-beta-feedback-pypi-calver  
**Date:** 2026-09-10

| ID | Decision | Rationale |
|----|----------|-----------|
| D1 | Shared `beta-feedback` Issues label + template | One feedback funnel for all beta surfaces |
| D2 | gh-overview = GitHub repo About + root README | No separate in-app overview page |
| D3 | CalVer `YYYY.MM.DD` (+ `.N` / `.devN`) | Operator request for date versioning |
| D4 | Nightly → TestPyPI only | Avoid unstable prod installs |
| D5 | Prod publish on promote via date tags + OIDC | Align with ADR-034; no bare-branch publish |
| D6 | Agent rule recommends beta+Issues for new features | Durable process after EV-1150 |
| D7 | ADR-043 Proposed → Accept at build gate | Standing decision record |

[Corpus: adr/ADR-043] [Corpus: product] [Corpus: tech-spec]

| D8 | GitHub About description update deferred | `gh repo edit` / PATCH returned 404 for this token; label `beta-feedback` already exists; README updated |
