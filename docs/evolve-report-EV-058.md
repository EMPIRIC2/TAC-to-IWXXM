# Evolve report — EV-058

> Cycle: EV-058 · Session: S068-quality-metrics-diff-layout  
> Closed: 2026-08-17 · `D-S068-13=1` / `D-S068-close=1`  
> Preset: Lean · Spec→Build: open · Promote: **held**

## Goal

Selectable side-by-side vs inline (unified) XML diff on Quality metrics detail (`/quality/:stem`), with preference persistence; ship to stage.

## Outcome

| Item | Result |
|------|--------|
| PR | [#994](https://github.com/EMPIRIC2/TAC-to-IWXXM/pull/994) **MERGED** → `stage` @ `2c320c45` |
| Issue | [#983](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/983) **CLOSED** · board **Done** |
| Staging CD | [32038222032](https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/32038222032) Deploy + Staging smoke **success** |
| Smokes | H0c–H5 PASS; live UJ-056 4/4 (incl. TC-EV058-005) |

## Routing (Lean)

`00 → 16 → 01 → 02 → 10 → 13` (skip 03–09, 11–12)

## Features / corpus

- Deepen **F7.q** — [Corpus: product §F7.q]
- Deepen **UJ-056** / **TC-EV058** — [Corpus: journeys §UJ-056] [Corpus: tests §UJ-056]
- Deploy path — [Corpus: deploy] [Corpus: adr/ADR-034]

## Out of scope (honored)

API/backend · new npm diff package · C14N/`match_status` semantics · promote to main · non–Quality-metrics UI

## Next

Promote `stage`→`main` only after separate user re-approve.
