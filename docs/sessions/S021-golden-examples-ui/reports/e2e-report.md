# E2E Report — S021 / EV-016 (F7.g / UJ-032)

> Generated: 2026-07-26  
> Scope: UJ-032 / TC-F7-008 (golden examples load)  
> Branch: `evolve/EV-016-golden-examples-ui` @ `3d1c58b`  
> Mode: evolve delta (10-e2e) · parallel with 09-qa  
> Mechanism: Vitest (T0 in-process) — no Playwright spec for F7.g (per test-plan / E16-5)

## Journey matrix

| Journey / TC | Mechanism | T0 | T2 connectivity | T3 browser |
|--------------|-----------|----|-----------------|------------|
| UJ-032 / TC-F7-008 C1 catalog | Vitest `examplesCatalog.test.ts` | PASS | pending 13 | pending 13 |
| UJ-032 / TC-F7-008 C2–C4 click-to-load | Vitest `GoldenExamplesSelect` + `FileConverter` | PASS | pending 13 (H4–H5) | pending 13 |
| UJ-032 / TC-F7-008 C5 soft-fail/queue | — | N/A (OOS v1) | — | — |

## Results

| Suite | Files | Tests | Status |
|-------|-------|-------|--------|
| TC-F7-008 focused | 3 | **100** passed | PASS |
| Full `@metar/frontend` (regression) | 75 | **688** passed | PASS |

### Focused command

```bash
pnpm --filter @metar/frontend exec vitest run \
  src/fixtures/examples/examplesCatalog.test.ts \
  src/app/components/GoldenExamplesSelect.test.tsx \
  src/app/components/FileConverter.test.tsx
# Test Files  3 passed (3) · Tests  100 passed (100)
```

### Journey steps ↔ evidence (UJ-032)

| Step | Acceptance | Evidence |
|------|------------|----------|
| 1–2 | Examples control on workbench | `GoldenExamplesSelect` + FileConverter wiring Vitest |
| 3 | Load TAC → body + product + toast + demo label | TC-F7-008 C2 |
| 5 | AHL → `ahl_bulletin` | TC-F7-008 C3 |
| 6 | IWXXM → `collect_iwxxm` | TC-F7-008 C4 |
| 7 | Catalog ≥2/product or gap; VAA/TCA gap | TC-F7-008 C1 + `FIXTURE_GAPS.md` |
| — | No backend/env/DB | FE static fixtures only |

**Dedicated Playwright F7.g spec:** none (hard gate = Vitest; live H4–H5 at 13).

## Connectivity columns

| Column | Status |
|--------|--------|
| T0 in-process | **PASS** |
| T2 H4–H5 | pending — 13-deploy-smoke (FE redeploy) |
| T3 live browser UJ | pending — after H4–H5 |

**Overall T0: PASS** — production browser proof deferred to 13-deploy-smoke with explicit H4–H5 requirement (routing-plan / feature-list F7.g AC).

## F7 golden-examples gate checklist (partial)

- [x] TC-F7-008 green at T0 (Vitest catalog + click-to-load)
- [x] No backend / env / DB changes
- [ ] H4–H5 when FE deploys (13)
- [x] F7 status remains **Planned** (no flip this cycle)
