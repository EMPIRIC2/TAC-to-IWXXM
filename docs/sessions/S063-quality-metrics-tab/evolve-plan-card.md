# Evolve Plan Card

> Cycle: EV-054 | Session: S063-quality-metrics-tab | Updated: 2026-08-10

## Goal

Operator **Quality metrics** tab: browse official WMO IWXXM corpus by product with
match / residuals / lint / validate diagnostics ([#836](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/836)).

## Features

- Deepen **F7** only; note **F7.q** in feature-list (`D-S063-fn=1`) — [Corpus: product §F7]
- Consumes F25 / F7.g catalog, F9 decode, F2 validate, F15/F20/F23+ quality bars
- New UJ (**UJ-056** proposed) — [Corpus: journeys]
- Metrics: **precomputed** fixtures via public **`GET /api/v1/quality-metrics*`**
  (`D-S063-compute=1` + `D-S063-gateA=2`)

## In / out of scope

- In: primary shell tab; public `quality-metrics*` API; precomputed fixtures; unified XML
  diff; corpus by product; gap labeling; H4–H5 / Playwright smoke
- Out: replace CI matrices; promote wmoReference→wmoPass; live WMO re-download;
  products beyond catalog; #874/#727; #840 epic; stage→main unless approved

## Preset + routing

- Preset: **Standard** (`D-S063-route=1`; amended include **05**)
- Stages: `00 → 16 → 01 → 02 → 04 → 05 → 07 → 08 → 09 → 10 → 11 → 12 → 13`
- Skip: 03, 06

## Next child stage

**07-build** M4 — detail panes + unified XML diff (T4.1–T4.3); M1–M3 done

## Risks / open decisions

1. ~~Precompute vs live~~ → **precompute default** (`D-S063-compute=1`)
2. ~~Diff UX~~ → **unified XML diff in v1** (`D-S063-diff=2`)
3. ~~Fn id~~ → F7 deepen + F7.q (`D-S063-fn=1`)
4. ~~Shell placement~~ → **separate primary tab** (`D-S063-shell-tab=1`)
5. ~~04 plan~~ → **approved as drafted** (`D-S063-04-plan=1`); no new npm diff
6. ~~05 Gate B~~ → **PASS** (`D-S063-05=1`); C1–C7 resolved
7. Ready queue thin (2) — refill from M0 Backlog
