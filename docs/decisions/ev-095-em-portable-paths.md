# EV-095 — Portable engineering-memory plugin / MCP paths (#1095)

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-08-31 | Treat #1095 as **stale install output**, not a new plugin design | Upstream `install-workspace.sh` already copies runtime `register-workspace-plugins.sh` (BUG-2026-08-31 / spec-dev-knowledge-graph#106) |
| 2026-08-31 | Reuse **`EM_ENGINEERING_MEMORY_ROOT`** | Already used by `.cursor/bin/memory-hook` and install script; do not add a second env name |
| 2026-08-31 | Refresh via **`install-workspace.sh`** | Preserves merge of Supabase/Render MCP; regenerates portable hook + ENGINEERING-MEMORY.md |
| 2026-08-31 | Keep **tracked** `.cursor/mcp.json` | Prefer `${userHome}/…` EM command; no gitignore overlay for this cycle |
| 2026-08-31 | Missing plugin → **empty `pluginPaths` + stderr** | Fail-open for `workspaceOpen`; match upstream template |
| 2026-08-31 | Add TAC **CI guard** against `/Users/` and `/home/<user>/` in tracked `.cursor/**` | Prevent recurrence; keep-local vs plugin-only tests |
| 2026-08-31 | Docs: this decision + install-rewritten `.cursor/ENGINEERING-MEMORY.md` | No new product CORPUS row / Fn |

## Acceptance

See issue [#1095](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1095) and session `EV-095-em-plugin-portable-paths` requirements report.

## Related

- EV-023 / EV-024 plugin migration (`docs/decisions/ev-023-plugin-migration.md`)
- `.cursor/ENGINEERING-MEMORY.md` (rewritten by install)

[Corpus: decisions] [Corpus: WAIVED — product/api/journeys/tests for DX-only #1095; reason: tooling path portability; decided: EV-095]
