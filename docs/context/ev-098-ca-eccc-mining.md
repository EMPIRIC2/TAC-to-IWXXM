# Scoped context — ev-098-ca-eccc-mining (EV-098)

**Mode:** scoped · **Date:** 2026-09-02  
**Session:** `~/.cursor/workflow/EMPIRIC2/TAC-to-IWXXM/sessions/EV-098-ca-eccc-mining`  
**Cycle:** EV-098 · **Feature:** F36 (`CA_ECCC` deepen)  
**Issues:** [#1028](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1028), [#1029](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1029), [#1030](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1030), [#1031](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1031)  
**Parent:** #916 closed (EV-078 / EV-064 P1)

[Corpus: product §F36] [Corpus: domain-profiles] [Corpus: decisions] ev-097

## Problem

`CA_ECCC` P1 shipping left mining shallow relative to open P1 children. Need deep evidence for:

1. **#1028** — Full ECCC MSC IWXXM datamart triage (schema, code-ca, ops feeds)
2. **#1031** — MSC `doc/` PDF implementation guidance catalogue
3. **#1029** — MANOBS section-level METAR/SPECI TAC → rule stubs + P0 fixtures
4. **#1030** — MANAIR TAF/AIRMET/GFA national extensions + code-ca phenomena

## Goal

Deep-research handoff (EV-097) → mining notes → promote durable URLs/stubs/fixtures via `mine-domain-sources` (gates A→B→C).

## In / out

**In:** Mining notes updates; `RULE_SOURCE_URLS` / `PROVENANCE_MAP`; rule stubs; P0 MANOBS fixtures under `profiles/CA_ECCC/`; COVERAGE_MATRIX rows; vendor pin cadence notes for `iwxxm-ca`.

**Out:** UI / e2e; SIGMET national layer & VAA (#1030 OOS); copyrighted full annex/PDF prose in git; hand-edits under `vendor/schemas/*`; SoT edits without gate C.

## Context interview (approved)

| Q | Choice |
|---|--------|
| Build intent | Notes + provenance + stubs + **P0 fixtures** |
| Research | **Emit handoff prompts**; paste findings for gate B |
| Order | **#1028 → #1031 → #1029 → #1030** |
| UI | **N/A** — must not break CA_ECCC convert/validate or IWXXM 3.0.0 pin |
| Proceed | Context approved → requirements |

## Runtime SoT (must not break)

- Profile `CA_ECCC` → IWXXM **3.0.0** + `iwxxm-ca` extensions ([ADR-036](../adr/ADR-036-semantic-vs-exchange-profiles.md))
- Existing convert/validate paths + fixtures under `profiles/CA_ECCC/`

## Prior art (do not restart)

| Artifact | Use |
|----------|-----|
| `docs/domain/mining/eccc-iwxxm-ca-mining-notes.md` | Datamart / XSD baseline (EV-064) — deepen |
| `docs/domain/mining/manobs-manair-ca-mining-notes.md` | TAC layer stub — deepen |
| `.cursor/skills/deep-research-domain-handoff` | Gate A/B/C handoff (EV-097) |
| `.cursor/skills/mine-domain-sources` | Promote only after gate C |
| EV-064 / #916 | CA_ECCC P1 already shipped |

## Skills / path

```text
requirements → draft-docs → feasibility → tech-plan → verify-tech → documenting verify
        │
        └── deep-research-domain-handoff (A→research→B→C)
                    └── mine-domain-sources (on Approve)
```

## Success

- All four issues triaged with promotion backlog rows
- Mining notes + provenance updated when operator asks to commit
- P0 MANOBS rules have fixture pairs where promoted
- No SoT without gate C; no full copyrighted prose in git

## Memory

`sessions/EV-098-ca-eccc-mining/reports/memory-context.md` — KG retrieve empty; adopt EV-097 path; keep-local prior mining notes.
