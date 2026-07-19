# T4.5 — manylinux + macOS + Windows maturin wheel jobs (E10-39)

**Date**: 2026-07-19  
**Workflow**: `.github/workflows/pypi-publish.yml`

## What landed

| Item | Detail |
|------|--------|
| Job | `build-native` |
| Packages | `tac2iwxxm`, `iwxxm-validate` (not `tac-validate`) |
| OS matrix | `ubuntu-latest` (manylinux auto), `macos-latest`, `windows-latest` |
| Builder | `PyO3/maturin-action@v1` (`--release -m rust/Cargo.toml`) |
| Schemas | `iwxxm-validate` runs `sync_runtime_schemas.py` before maturin |
| Artifacts | `dist-<pkg>-pure`, `dist-<pkg>-native-<os>`; publish merges via pattern |
| Smoke / publish | Tolerate `build-native` skipped (pure-only packages / tags) |

## Checklist alignment

- [x] manylinux + macOS + Windows maturin jobs for native packages  
- [x] Pure hatch path retained for all three  
- [x] T4.4 structural tests still green (assert `build-native` + OS matrix)

## Next (M4 complete → M5)

M4 tasks T4.1–T4.5 done. Next milestone: **M5** msgspec HTTP + FE types (T5.1).
