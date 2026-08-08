# 11-verify-impl — S052 / EV-043

[Corpus: product §F30] [Corpus: adr/ADR-034] [Corpus: tests]

| AC / TC | Status | Evidence |
|---------|--------|----------|
| TC-F30-008 staging ns + DB | **MET** | `metar-iwxxm-staging`; DB `metar_iwxxm_staging`; secrets applied |
| TC-F30-009 staging DNS + TLS | **PARTIAL** | Ingress + cert-manager issued; DNS A records pending Porkbun (Host-header `/health` 200) |
| TC-F30-010 dual CD | **MET** (code) | `ci-cd.yml` Deploy on `stage`/`main`; Environments need admin create |
| TC-F30-011 branch protection | **PARTIAL** | `stage` branch created; rulesets script ready (admin 403) |
| TC-F30-012 staging-gate | **MET** (code) | `scripts/ci/staging_gate.sh` + CI job |

## Notes

- Solo-dev: PR is manual promote; no Environment reviewers.
- Admin follow-ups: Porkbun DNS; `apply_gh_branch_rulesets.sh`; GH Environments UI.
