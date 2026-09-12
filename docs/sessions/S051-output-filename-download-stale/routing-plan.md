# Routing plan — S051-output-filename-download-stale

**Type:** hotfix · **Orchestrator:** 14-hotfix  
**Path:** `14→(15 optional after deploy)`  
**Status:** in_progress

| Stage | Required | Mode | Status | Notes |
|-------|----------|------|--------|-------|
| 14-hotfix | yes | full | **in_progress** | #904 / BUG-2026-08-07-output-filename-download-stale; local-first |
| 15-service-health | no | when_deployed | pending | optional after deploy (explicit approval required) |

## Intent

After a successful manual-input conversion, changing **Output filename (optional)** must update the name used for Download and ZIP member names — not only the live preview under the field.

## References

- Bug report: `docs/bug-reports/BUG-2026-08-07-output-filename-download-stale.md`
- GitHub: https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/904
