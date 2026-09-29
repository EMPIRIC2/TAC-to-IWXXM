# Context — regional-exchange-overlays-1222

**Session:** `EV-1222-regional-exchange-overlays`  
**Date:** 2026-09-29  
**Mode:** scoped evolve (standard)  
**Ticket:** [#1222](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1222)  
**Corpus:** [Corpus: product §F35] [Corpus: product §F36] [Corpus: domain-profiles]
[Corpus: adr/ADR-036] [Corpus: api] [Corpus: tests] [Corpus: tech-spec]

## Goal

Operators and packaging callers selecting `APAC_ROBEX` / `EUR_RODEX` / `AFI` /
`CAR_SAM` get **real packaging behavior** (or honest catalog gaps), not silent
delegation identical to `GLOBAL_AFS` with no documented regional delta.

## Locked intake (operator proceed 2026-09-29)

| Topic | Lock |
|-------|------|
| Scale | Standard |
| Primary overlay | `APAC_ROBEX` first (≥1 non-stub rule + fixture) |
| Others | Implement or explicit `gaps:` + provenance |
| UI | No Convert redesign; exchange picker already lists ids |
| Preview | Docs/repo only |
| OUT | Semantic TAC; live send; marketplace; invent matrices |

## Problem / users

Today `apply_exchange_packaging` treats all four regional stubs as
`wrap_global_afs_collect` with a comment that handbook rules deepen later
(`packages/dissemination/src/dissemination/packaging.py`). Catalog + stubs
already pin ROBEX HB / EUR Doc 018 / AFI guideline URLs (EV-090), but status
remains `stub` and tests only assert COLLECT wrap equivalence.

## Must not break

- `GLOBAL_AFS` COLLECT baseline + TC-EV063/065/086/090
- Convert-only paths (no packaging latency)
- Unknown exchange id → 400 / ValueError
- Dissemination SSRF allowlist / BYOC memory-only credentials
- EV-048 if any operator-visible string is added

## Inventory (2026-09-29)

| Id | Catalog status | Runtime |
|----|----------------|---------|
| `GLOBAL_AFS` | implemented | COLLECT wrap |
| `APAC_ROBEX` | stub | same COLLECT baseline |
| `EUR_RODEX` | stub | same |
| `AFI` | stub | same |
| `CAR_SAM` | stub | same |

Pinned sources already in `catalog.yaml` + `docs/domain/profiles/exchange/*.md`.
Mining notes: OPMET Guidelines 5th; APAC IWXXM FAQs 3rd. ROBEX HB PDF URL pinned
but no dedicated mining-notes file yet — Spec→Build will create one from citations
only (no full annex prose).

## Prior closeout this session turn

Recommended candidates that were already on `stage` but left open (PR→stage
does not auto-close): #1251, #1028–#1031, #1252 closed with honesty comments.

## CORPUS coverage

Standing rows cover F35/F36 + ADR-036 + domain-profiles. **No new CORPUS member.**
Deltas: feature-list F36, test-plan TC-EV1222-*, exchange stubs, packaging module.

## Spec → Build gate

**closed** until documenting verify PASS and operator opens gate.
