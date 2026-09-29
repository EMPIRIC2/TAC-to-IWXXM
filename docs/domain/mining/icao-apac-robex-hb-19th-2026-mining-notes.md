# APAC ROBEX Handbook (19th Ed., Feb 2026) — mining notes

Transitory dig — **not** standing SoT. Promote only durable citations.

**Source:** Asia Pacific ROBEX Handbook, Nineteenth Edition — February 2026  
**URL:** https://www.icao.int/sites/default/files/APAC/Documents/edocs/MET/2026-02-APAC-ROBEX-HB-19TH-ED.pdf  
**Local (agent):** `.local/reference/icao-apac-robex-hb-19th-2026/` (not committed)  
**Label:** normative-regional (bulletin scheme); IWXXM XML shell **defers** to OPMET Guidelines  
**Mined:** 2026-09-29 · [#1222](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1222)  
**Corpus:** [Corpus: product §F36] [Corpus: adr/ADR-036]

## Focus

What packaging delta (if any) `APAC_ROBEX` can claim beyond `GLOBAL_AFS` COLLECT wrap.

## Key findings (with section pointers)

| § / App | Claim | Packaging implication |
|---------|-------|------------------------|
| §5.2.1–5.2.3 | IWXXM uses AMHS/FTBP; not AFTN | Ops/transport — not COLLECT XML shape |
| §6.6.1 | METAR/SPECI IWXXM format → **refer to** OPMET IWXXM Exchange Guidelines | Same XML shell SoT as `GLOBAL_AFS` |
| §7.5 | TAF IWXXM likewise defers to Guidelines | Same |
| §6.4.2 + App A | Example WMO abbreviated heading `SACI31 ZBBB 271300` (Beijing ROC METAR bulletin) | Regional **bulletin id** examples for FTBP identifier when caller omits `bulletin_identifier` |
| App A tables | Fixed ROBEX SA bulletin ids (`SACI31`, `SAAU31`, …) | Content/routing tables — not convert IR |

## Promotion this cycle (EV-1222)

| Rule | Status | Consumer |
|------|--------|----------|
| Default FTBP-style `bulletinIdentifier` for `APAC_ROBEX` when unset: `A_SACI31ZBBB.xml` (from §6.4.2 / App A `SACI31 ZBBB` example + OPMET Guidelines `A_TTAAiiCCCC…` filename stem) | **promoted** | `dissemination.packaging` |
| Full ROBEX handbook matrix / ROC distribution lists | **held** — catalog `gaps:` | backlog |

## Gaps

- No ROBEX-specific COLLECT XML schema beyond OPMET Guidelines.
- Do not invent TTAAii selection from aerodrome lists in App A this cycle.
