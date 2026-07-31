# Scoped context — iwxxm-domain-mine (S031 / EV-024)

**Mode:** scoped · **Date:** 2026-07-30  
**Session:** S031-iwxxm-domain-mine · **Cycle:** EV-024  
**Issues:** #804, #807, #773 (exclude #806)

## Problem

Vendor pin already mirrors WMO IWXXM **v2025-2**, but:

1. **#804** — Official examples / `rule/` / XSD tree are under-used in catalog/CI; folder relevancy vs product map is incomplete.
2. **#807** — Org-level ranking (`wmo-im-org-mining-notes.md`, 2026-07-14) needs refresh against current pin and sibling repos (codelists, modelling, translation, collect/SAF lineage).
3. **#773** — IWXXM-US METAR/SPECI model PDF + MDL modelling not fully mapped to encode/validate/fixture matrices (F6.b).

## Runtime SoT

`vendor/manifest.json` → `vendor/schemas/iwxxm/2025-2/` (+ `iwxxm-us` pin). Upstream `master` tip is drift/relevancy only.

## Prior art (do not restart)

| Artifact | Use |
|----------|-----|
| `docs/domain/mining/wmo-im-tier-a-mining-notes.md` | Deep clones at pin SHAs |
| `docs/domain/mining/wmo-im-org-mining-notes.md` | Org survey — refresh |
| `docs/domain/mining/iwxxm-2025-2-reference-set-mining-notes.md` | Reference-set tracker |
| `apps/frontend/src/fixtures/examples/FIXTURE_GAPS.md` | Catalog wiring gaps |
| EV-023 / #800 | Encode deltas already shipped; consume Guidance re-scrape here |

## Skills

- `.cursor/skills/mine-domain-sources`
- `.cursor/skills/extract-pdf-to-repo` (#773 PDF → `.local/`)

## Success

Every #804/#807/#773 acceptance checklist item closed or tracked via child issue; mining notes indexed; durable promotions committed; in-scope WMO stems wired or explicitly deferred.
