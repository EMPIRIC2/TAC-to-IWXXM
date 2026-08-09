# #882 compose design note — optional live refresh outside PR CI

> **Cycle**: EV-050 / S059 · **Task**: T4.1 · **AC6 / TC-EV050-006**  
> **Decision**: `D-S059-882=3a` — design-only; **no** job implementation this cycle  
> **Corpus**: [Corpus: decisions §EV-050], [Corpus: tech-spec], [Corpus: product §F12]

## Purpose

Sketch how an **optional scheduled live refresh** of Code Registry signals can compose with
[#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) (WMO standards change-notification
spike) **without** putting live `codes.wmo.int` HTML into PR CI, and without implementing the
full notification pipeline in EV-050.

## Boundaries (locked)

| Surface | Role | In EV-050? |
|---------|------|------------|
| Offline harvest → `wmo_membership.json` | PR CI / `tac-validate` L3 Validated | **Shipped** (M1–M2) |
| `make membership-regen` / `membership-check` | Pin-aligned regenerate + drift | **Shipped** |
| [#859](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/859) URI drift | SCH RDF ↔ vendor CSV (optional `--live` RDF, never HTML) | Keep; compose |
| [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882) notify | Who/what/when when schemas/SCH/codelists/releases move | **Design only** |
| Live HTML scrape in PR CI | Forbidden | Out of scope forever for this bar |

## Composition sketch

```
┌─────────────────────────────────────────────────────────────┐
│ PR CI (always offline)                                       │
│  vendor/schemas/iwxxm-codelists + pin RDF                    │
│       → make membership-regen / membership-check             │
│       → tac-validate membership tests (TC-EV050-001/002)     │
│  make codelist-uri-drift (#859) — vendor-only by default     │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ vendor sync PR bumps pin
                              │ (normal M6 / sync_iwxxm cadence)
┌─────────────────────────────────────────────────────────────┐
│ Outside PR CI (future #882 job — not built here)             │
│  Scheduled poll of signal sources:                           │
│    • wmo-im/iwxxm releases + tip (#852 tip-diff overlap)     │
│    • iwxxm-codelists tip vs vendor/manifest pin              │
│    • optional Linked Data / RDF fetch (Accept headers)       │
│    • never require HTML scraping for gate green              │
│  Emit: GH issue / discussion / workflow summary artifact     │
│  Human: open vendor sync PR → membership-regen → merge       │
└─────────────────────────────────────────────────────────────┘
```

## Ownership split vs existing tickets

| Concern | Owner | EV-050 note |
|---------|-------|-------------|
| TAC token ∈ harvested register (happy/sad) | #959 / #889 Validated | Done offline |
| URI membership drift SCH ↔ CSV | #859 | Unchanged; compose on same pin |
| Tip-diff XSD/SCH/example stems | #852 | Unchanged |
| “Something moved — ping engineers” | #882 | **This note**; job still open |
| Exhaustive fixture depth | #959/#889 defer+cite | Not notify |

## Recommended #882 follow-on (when spike resumes)

1. **Cadence**: weekly or on `schedule` Action; fail-soft (notify only, never block `main`/`stage` PR CI).
2. **Diff grain**: pin SHA / tag delta for `iwxxm-codelists` + release notes for `iwxxm`; optional RDF member-count delta — **not** HTML DOM scrape.
3. **Handoff artifact**: short markdown summary + checklist “bump pin → `make membership-regen` → commit `wmo_membership.json`”.
4. **Noise control**: tip vs tagged release; suppress if already covered by open vendor sync PR.
5. **No duplicate Validated CI**: do not re-implement membership asserts in the notify job.

## Explicit non-goals (this cycle)

- No GitHub Action / cron / worker for live refresh
- No full notification pipeline (channels, templates, on-call)
- No live HTML in any CI required check
- No new ADR (`D-S059-04-adr=1`)

## Pointers

- Harvest path (standing): [Corpus: tech-spec] §WMO membership harvest; [TAC_VALIDATION.md](../../../domain/TAC_VALIDATION.md) §Offline membership harvest
- Validated closeout: [evolve-decisions.md](../../../decisions/evolve-decisions.md) §EV-050 AC5
- Parent spike: [#882](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/882)
