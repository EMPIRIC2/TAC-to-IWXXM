# EV-1120 / #1122 — Profile-scoped catalog mining notes (Phase A)

**Status**: planned (spec band)  
**Session**: EV-1120-epic-profile-scoped-lint-validation-issues-catal  
**Corpus**: [Corpus: domain-profiles] · [Corpus: product] F15/F36 · [Corpus: adr/ADR-028]

## Priority this cycle

| Semantic profile | Minimum catalog content |
|------------------|-------------------------|
| `US_FAA_NWS` | ≥1 national-only TAC lint code + ≥1 IWXXM-family validation row |
| `CA_ECCC` | ≥1 national-only TAC lint code + ≥1 IWXXM-family validation row |
| Thin packs (`AU_BOM`, `NZ_CAA_MET`, …) | Stub applicability tags OK; may share ICAO examples in UX |

## Filter semantics (API)

- Omit `semantic_profile` → all rows (unchanged).
- Set → `shared/global ∪ profile-applicable`.
- National-only codes must **not** appear under `ICAO_2025` unless also marked shared.
- Provenance: public URLs / citations only; no planning ids in `source_attribution` (EV-048).

## Sources (reuse existing packs)

Prefer durable public landings already cited under:

- `docs/domain/profiles/semantic/US_FAA_NWS.md`
- `docs/domain/profiles/semantic/CA_ECCC.md`
- Prior mining notes from #912 / #913 / EV-061 / EV-062

Do **not** paste copyrighted Annex prose into operator `message_template`s.

## Out of Phase A

Full national convert/validate engines beyond catalog descriptions remain on F36 profile issues.
