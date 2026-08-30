# National profile onboarding playbook

> **Corpus**: [Corpus: domain-profiles] · **Issue**: [#1044](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1044) · **ADR**: [ADR-036](../../adr/ADR-036-semantic-vs-exchange-profiles.md)  
> **Reference implementation**: `CA_ECCC` ([#916](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/916))  
> **Feature**: [Corpus: product §F36]

Repeatable, country-agnostic process for adding a **semantic** national profile.
Exchange overlays (#921) are a separate kind — see §Exchange boundary below.

## Design principle

```text
One pipeline (ICAO canonical IR + overlays)
  × N national profiles (data-driven, not N converters)
  × independent iwxxmVersion + extension XSD pins per profile
  × optional exchange profile for packaging (#921)
```

## Paths: thin vs full

| Path | When | Minimum artifacts | Code changes |
|------|------|-------------------|--------------|
| **Thin / compat** (#920) | Overrides + fixtures only; core IWXXM emit | Catalog row, semantic stub, TAC mining note, fixture tree + `manifest.json`, registry + convert allowlist | No national XSD pin; no `profiles/<id>.py` emitter |
| **Full national** (CA pattern) | Published national XSD / vocab / ops corpus | Thin set **plus** IWXXM mining note, vendor pins, extension emitters, validate stack, ops harvest | Extension token + vendor sync |

Templates: [`_template/`](_template/). Scaffold: `scripts/profiles/scaffold_national_profile.py --id XX_YYY`.

**Honest constraint (EV-088):** “Catalog + mining + fixtures + vendor pins only” is the **target**.
Today thin packs still need hand edits in `profile_registry.py`, `convert.py`, OpenAPI, and FE
wire enums. The scaffold prints that checklist; do not invent a second converter.

---

## 1. Profile catalog row

Machine SoT: [`catalog.yaml`](catalog.yaml). Copy [`_template/catalog-row.yaml`](_template/catalog-row.yaml).

Required fields: `id`, `kind: semantic`, `priority`, `status`, `products`, `sources`,
`mining_notes`, `stub`, `gaps`. Optional: `extension_token`, `vendor_pins`,
`iwxxm_version_pin`, `issuing_body`, `locale`, exchange-output fields (§7).

Human stub: `semantic/<ID>.md` from [`_template/semantic-profile.md`](_template/semantic-profile.md).

---

## 2. Mining notes (transitory → promote)

| Note | Template | Purpose |
|------|----------|---------|
| `<slug>-tac-mining-notes.md` | [`_template/tac-mining-notes.md`](_template/tac-mining-notes.md) | National TAC manuals |
| `<slug>-iwxxm-mining-notes.md` | [`_template/iwxxm-mining-notes.md`](_template/iwxxm-mining-notes.md) | National XSD, codes, datamart (full path; optional for thin) |
| `<slug>-doc-pdfs-mining-notes.md` | optional | Implementation PDF index |

**Promotion rule:** mining row → `rule_id` → fixture → [`RULE_SOURCE_URLS.md`](../rules/RULE_SOURCE_URLS.md) → [`COVERAGE_MATRIX.md`](../rules/COVERAGE_MATRIX.md). Never leave durable rules only in mining notes.

Skill: `.cursor/skills/mine-domain-sources/SKILL.md`.

---

## 3. Standards hierarchy (fill per profile)

```text
L0 — National regulation / operator manual
L1 — WMO-No. 306 Vol I.1 TAC templates
L2 — WMO IWXXM semantic model (profile-pinned version)
L3 — WMO XSD + Schematron (profile-pinned bundle)
L4 — National extension XSDs (if published)
L5 — National controlled vocabularies / code lists
L6 — Operational public corpus (datamart, API, examples)
```

Thin packs often fill L0–L1 (+ L2 via ICAO baseline) and leave L4–L6 as explicit `gaps:`.

---

## 4. Fixture layout

```text
packages/tac2iwxxm/tests/fixtures/profiles/<PROFILE_ID>/
  manifest.json
  <PRODUCT>/{valid,invalid,ops,expected-iwxxm}/
```

Manifest schema: see [`_template/manifest.json.example`](_template/manifest.json.example).
Reference: `CA_ECCC` (full), `AU_BOM` / `NZ_CAA_MET` (thin kickoff).

---

## 5. Staged validation pipeline

Align ADR-036 §4 and spike [#925](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/925):

```text
TAC lexical → profile semantic (tac-validate overlay)
  → cross-field → canonical IR
  → core XSD (profile iwxxmVersion)
  → extension XSD (national token)
  → Schematron → national vocabulary
  → profile output rules → exchange validation (separate kind)
```

Nationals add **plugins/config**, not forked engines.

---

## 6. Vocabulary / code-list layer

| Artifact | Location |
|----------|----------|
| National vocab vendor pin | `vendor/schemas/<national>/…` |
| Deviation matrix | `semantic/<ID>.md` §Code list policy |
| Semantic checks | `iwxxm-validate` profile hook |

CA reference: [#1033](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1033), [#1034](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1034).

---

## 7. Exchange output contract + ConversionProfile (#924)

Profile / catalog fields (national fills values; engine reads config):

| Field | Role |
|-------|------|
| `wmo_header_template` | Per-product WMO header pattern |
| `file_naming_pattern` | Exchange filename |
| `distribution_url_pattern` | Informative / ops URL shape |
| `station_reporting_rules` | Station / reporting policy |
| `translation_centre_metadata_policy` | Translator metadata on convert |

**#924 cross-check:** these map to `ConversionProfile.dissemination` / output packaging
fields on the executable-profile spike — **not** F16–F19 BYOC destination credentials.
Custom operator overlays remain #924 trust-model OOS for this playbook.

---

## 8. Child issue types A–P (reference: CA_ECCC)

Spawn the **same stack** per P1+ national; swap sources only.

| Type | Playbook § | CA reference | Reusable deliverable |
|------|------------|--------------|----------------------|
| A | 1, vendor | [#1027](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1027) | `vendor/manifest.json` + sync |
| B | 2 | [#1028](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1028) | IWXXM mining + RULE_SOURCE_URLS |
| C | 2 | [#1029](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1029) | TAC surface mining |
| D | 2 | [#1030](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1030) | TAC forecast mining |
| E | 2 | [#1031](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1031) | PDF index note |
| F | 7 | [#1032](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1032) | Exchange output fields + hooks |
| G | 6 | [#1033](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1033) | Vocab registry |
| H | 6 | [#1034](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1034) | Deviation matrix |
| I | 5 | [#1035](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1035) | Layered validate wiring |
| J | 4, 10 | [#1036](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1036) | Ops corpus + harvest |
| K | 5 | [#1038](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1038) | tac-validate overlay |
| L | emitters | [#1039](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1039), [#1041](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1041) | Product convert mappers |
| M | 7 | [#1040](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1040) | Translation metadata policy |
| N | wiring | [#1042](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1042) | API/FE registry pattern |
| O | spike | [#1037](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1037) | IWXXM-only product scope |
| P | 5 | [#1043](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1043) | Validate-first secondary products |

**Thin packs (#920):** typically C (+ optional D), N (registry), fixtures; defer A/B/G–J/L unless evidence requires.

**AU/NZ (#917/#918):** EV-087 used thin path (TAC mining + fixtures + registry; no national XSD).

---

## 9. Locale / issuing-body metadata

- Document primary mining locale per source; note translation pairs.
- Operator-visible strings: plain language only — no internal doc refs ([Corpus: product] EV-048).
- Put `issuing_body` / jurisdiction in catalog — not hardcoded string tables in emitters.
- No separate locale profiles without documented TAC/IWXXM divergence (#912 non-goals).

---

## 10. CI / reproducibility

| Check | Pattern |
|-------|---------|
| Vendor manifest integrity | National pin in manifest tests |
| Vocabulary drift | Parameterized sync (when vocab exists) |
| Ops corpus refresh | Prefer profile-id harvest (CA script is reference; generalize when second corpus lands) |
| Coverage matrix | One row per profile × product |
| Contract smoke | Templates exist; catalog parses (EV-088) |

Exchange packaging tests: copy parameterized pattern in
`packages/dissemination/tests/test_tc_ev086_exchange_profiles.py` — do not fork per region.

---

## Scaffold checklist (printed by script)

After copying `_template/` into place:

1. Fill `catalog.yaml` row + `semantic/<ID>.md`
2. Fill mining notes under `docs/domain/mining/`; index in `mining/README.md`
3. Add fixtures under `packages/tac2iwxxm/tests/fixtures/profiles/<ID>/`
4. Edit `profile_registry.py` (canonical ↔ emit maps)
5. Edit `convert.py` product allowlist / emit branch
6. OpenAPI / Form profile enum + regenerate contract if required
7. FE wire types / picker options if operator-visible
8. Tests + `docs/test-plan.md` TC rows as needed
9. Promote durable URLs into RULE_SOURCE_URLS / COVERAGE_MATRIX

---

## Exchange boundary (#921)

This playbook does **not** define regional exchange overlays. Exchange IDs live under
`exchange/*.md` and `packages/dissemination` registries. Semantic onboarding may *reference*
a default `exchange.profile` in catalog metadata; packaging deepen stays on #921 / EV-090.

**Operator UI:** light **Exchange profile** picker is [#1024](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1024)
(EV-090) — separate from semantic Type N wiring. Dissemination drawer overlay selection remains
[#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898).

---

## Related tickets (consumers)

| Ticket | How playbook helps |
|--------|--------------------|
| [#913](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/913) | §2 promotion path for mined URLs |
| [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920) | Thin path + A–P subset |
| [#921](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/921) | Exchange stubs + EV-090 mining/picker; TC-EV086/TC-EV090 |
| [#1024](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1024) | Type N wiring pattern from #1042; exchange light picker EV-090 |
| [#924](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/924) | §7 field map |
| [#1050](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1050) | Report variants stay catalog/IR (see CA LWIS/SAWR) until API deepen |

---

## References

- [profiles/README.md](README.md)
- [ADR-036](../../adr/ADR-036-semantic-vs-exchange-profiles.md)
- Epic [#912](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/912)
- Playbook issue [#1044](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1044)
