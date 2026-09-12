# Verification — M11 T11.3 / T11.4 (SWXA encode + convert bar)

**Cycle**: S036 / EV-029 · **Branch**: `evolve/EV-029-eight-family-ahl-rules`

## Scope

| Task | Result |
|------|--------|
| T11.3 | SWXA convert → `SpaceWeatherAdvisory` + XSD+SCH; annex3 golden `swxa_a7_3` (`spacewx-A7-3`) with `wmoReference` |
| T11.4 | `parse_swxa` / `emit_swxa_annex3` / convert dispatch; bulletin FN→LN + `split_bulletin(product=SWXA)` |

## Checks

- `ruff check` on touched tac2iwxxm sources/tests — pass
- Targeted pytest (F28-002/003/006, EV029-003 AHL, F6-030, F6-020 manifest, F6 product-matrix) — **83 passed**, 4 skipped
- Smoke: convert A7-3 → validate XSD+SCH — no blocking errors

## Next

- Commit `[T11.3]` / `[T11.4]` (atomic), push, watch CI
- **T11.5** — backend/runtime enum `product=swxa`
