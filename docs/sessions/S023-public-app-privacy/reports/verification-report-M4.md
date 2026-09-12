# M4 verification — S023 / EV-017 (Frontend Auth removal)

**Branch**: `evolve/EV-017-public-app-privacy`  
**Tip**: `13c9cf3`  
**Date**: 2026-07-28

## Tasks

| Task | Status | Commit |
|------|--------|--------|
| T4.1 TC-F21-auth-gone FE (red) | completed | `277b903` |
| T4.2 Remove Auth UX; omit Bearer | completed | `be1e848` |
| T4.3 Retire `api.disableAuth` | completed | `13c9cf3` |

## Checks

- `make validate-fast` — pass (pre-commit on T4.2 / T4.3)
- Vitest: `tc-f21-auth-gone`, App, FileConverter, dissemination, runtime-config — green

## Notes

- Orphaned FE `components/auth/*` + `authService` remain on disk (unused by App); delete with M5/M7 cleanup if desired.
- Backend `/auth/*` + JWT gates still present until M5.
- Draft PR: https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/786

## Next

M5 T5.1 — `/auth/*` and work-sessions → 404; convert without Authorization.
