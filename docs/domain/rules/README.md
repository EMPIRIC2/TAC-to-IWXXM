# Rule-source catalog (index)

Index for URL inventory and coverage. **Functional SoT** lives at domain root:

| Canonical | Path | Strategy section |
|-----------|------|------------------|
| TAC validation | [../TAC_VALIDATION.md](../TAC_VALIDATION.md) | §Validation strategy (TAC / Annex 3) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) | §Conversion strategy + §Conversion highlights |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) | §Validation strategy (produced IWXXM) |
| Domain hub (E2E pipeline) | [../README.md](../README.md) | §End-to-end strategy |

| This folder | Purpose |
|-------------|---------|
| [RULE_SOURCE_URLS.md](./RULE_SOURCE_URLS.md) | Master URL catalog |
| [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) | F6 product × profile × role · **pipeline gates** |
| [ACCESS_AND_CITATION.md](./ACCESS_AND_CITATION.md) | Paywall / citation policy |
| [PROVENANCE_MAP.md](./PROVENANCE_MAP.md) (+ [JSON twin](./PROVENANCE_MAP.json)) | **S043 / EV-035** dig ↔ rule ↔ source (path-cite; TC-EV035-*) |

**How to use:** pick product × role from [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) → open
the matching canonical strategy section → cite URLs from [RULE_SOURCE_URLS.md](./RULE_SOURCE_URLS.md).
Do not implement against mining digs alone.

### Role → strategy routing

| Catalog `role=` | Question | Canonical | Engine |
|-----------------|----------|-----------|--------|
| `validation` | Is **TAC** legal for this product/profile? | [TAC_VALIDATION.md](../TAC_VALIDATION.md) L1–L5 | `tac-validate` |
| `conversion` | TAC → IWXXM elements / nilReasons / hrefs | [IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) | `tac2iwxxm` |
| `iwxxm-validation` | Is produced XML valid for the pin? | [IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) WF→XSD→SCH | `iwxxm-validate` |
| `bulletin` | COLLECT / AHL / FTBP packaging | Conversion + [ICAO_OPMET_COMPLIANCE.md](../iwxxm/ICAO_OPMET_COMPLIANCE.md) | ops / F8 |

**Order:** TAC lint → convert → well-formed → **XSD** → **Schematron** → golden examples.  
Schematron is **blocking for release** (OPMET Guidelines). Conflict → defer to latest pin
([ACCESS_AND_CITATION.md](./ACCESS_AND_CITATION.md)).

### Apply playbooks (copy/paste for tickets)

| Goal | Steps |
|------|-------|
| **Validate TAC** | Profile (`annex3` \| `iwxxm_us`) → [TAC_VALIDATION](../TAC_VALIDATION.md) L1–L5 → product checklists (**A3-2** METAR/SPECI · **A5-1** TAF · **A6** SIGMET/AIRMET · **A2-1/A2-2** VAA/TCA · US SPECI §2.5.2 + RMK keep-list) → vocab on codes.wmo.int → accept shape vs official `.tac` |
| **Convert TAC→IWXXM** | [IWXXM_CONVERSION](../IWXXM_CONVERSION.md) decision order → product encode playbook → Guidance + pair → US RMK→iwxxm-us map when profile US → quarantine shell on fail → then validate |
| **Validate IWXXM** | [IWXXM_VALIDATION](../IWXXM_VALIDATION.md) “How to validate one document” + **per-product playbook** → product XSD + golden prefix → G4+G5 same year line |
| **US REMARKS path** | FMH-1 Ch.12 keep RMK → encode `iwxxm-us` elements (AO1→observingSystemType, SLP→seaLevelPressure, …) → combined catalogs |
| **Bulletin / ops** | Guidelines 5th + [ICAO_OPMET_COMPLIANCE](../iwxxm/ICAO_OPMET_COMPLIANCE.md) after G5 |

Gates: [COVERAGE_MATRIX.md](./COVERAGE_MATRIX.md) **G1–G7**. Hub E2E: [../README.md](../README.md).

**Transitory digs:** [../mining/](../mining/)

## Labeling

| Label | Meaning |
|-------|---------|
| **normative** | Binding WMO/ICAO/national regulation or machine artifact |
| **normative-vocabulary** | Official coded vocabularies (`codes.wmo.int`, …) |
| **normative-schema** | Official IWXXM XSD/Schematron packages |
| **normative-conversion-notes** | Official TAC→XML guidance |
| **normative-examples** | Official paired TAC/XML examples |
| **normative-exchange** | OPMET exchange / AMHS / Translation Centre guidelines |
| **informative** | Fixtures / community — not binding |
| **historical-GIFTs** | Gap baseline only (ADR-014) |

## Vendor pin

`vendor/manifest.json` → IWXXM **`v2025-2`**. Prefer `https://schemas.wmo.int/iwxxm/2025-2/`.
