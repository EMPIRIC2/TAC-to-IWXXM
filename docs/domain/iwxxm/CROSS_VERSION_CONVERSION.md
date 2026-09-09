# IWXXM cross-version conversion matrix (#908)

> **Corpus:** domain (iwxxm) · cited from [Corpus: product] F4 / [Corpus: api]  
> **Cycle:** EV-908-iwxxm-cross-version · **Date:** 2026-09-09  
> **Runtime:** `VersionMigrator` + `POST /api/v1/convert` with `product=iwxxm`

Global supported lines follow [VERSION_SUPPORT_POLICY.md](VERSION_SUPPORT_POLICY.md):
**2025-2** (latest) and **2023-1** (previous). Profile-scoped **3.0.0** (`CA_ECCC`) is
**not** in this global matrix.

## Legend

| Status | Meaning |
|--------|---------|
| `supported` | Transform defined; may emit migration warnings |
| `lossy` | Supported with documented element removes / no reverse invent |
| `unsupported` | Fail closed (HTTP 400 / structured error) — no silent NS rewrite |
| `noop` | Same version — pass-through |

## Global pair matrix (all encode products unless noted)

| From \ To | 2023-1 | 2025-2 |
|-----------|--------|--------|
| **2023-1** | noop | **lossy** (remove `runwayState` / `AerodromeRunwayState`; rewrite NS/schemaLocation) |
| **2025-2** | **unsupported** | noop |

Product-specific notes:

| Product | 2023-1 → 2025-2 | Notes |
|---------|-----------------|-------|
| METAR / SPECI | lossy | Runway-state removes are METAR-family relevant |
| TAF / SIGMET / AIRMET / VAA / TCA / SWXA / VONA | supported* | *Namespace rewrite + empty breaking list today; deepen goldens as needed |
| COLLECT envelopes | unsupported unless unwrapped first | Prefer report-level XML |

## Operator path

1. `POST /api/v1/convert` with `product=iwxxm`, file/XML body, `iwxxm_version=<target>`.
2. Response metadata may include `source_iwxxm_version`, `target_iwxxm_version`, `migrated_iwxxm`.
3. Migration warnings use code `IWXXM_VERSION_MIGRATION`.
4. Unsupported pairs use issue code `UNSUPPORTED_IWXXM_MIGRATION` (HTTP 400).
5. Success requires target-line validation when migration occurred.

## Related

- Implementation: `apps/backend/src/utilities/version_migration.py`
- Breaking-change SoT: `apps/backend/src/config/iwxxm_versions.py` → `breaking_changes_from_prior`
- Validate-only without convert: `#838` / `/api/v1/validate`
