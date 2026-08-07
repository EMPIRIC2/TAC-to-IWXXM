# Operator UI runbook (sources-first)

> **Audience:** day-to-day operators of the TAC→IWXXM workbench  
> **Cycle:** S049 / EV-041  
> **Companion briefing pack:** [../guides/operator-sources-pptx/](../guides/operator-sources-pptx/)  
> **Citation policy:** [../domain/rules/ACCESS_AND_CITATION.md](../domain/rules/ACCESS_AND_CITATION.md) — cite landings; **never** paste Annex 3 / Manual on Codes full text

This runbook explains **how to use** the operator UI and, for each surface, **which
standards, schemas, and packages** underwrite that behavior.
[Corpus: product §F7] [Corpus: system-spec] [docs/domain/README.md]

---

## 1. Purpose and access model

| Topic | What operators see | Source / cite |
|-------|--------------------|---------------|
| Convert / lint / validate / decode | Public API — **no JWT required** | [Corpus: product] F21 Amended; [Corpus: api] |
| Long-term work sessions | Optional login (Supabase Auth) → server sessions | [Corpus: product] F31; ADR-033 |
| Guest history | Local IndexedDB (privacy-gated) | [Corpus: product] F7.h / F22 / F31 |
| Deploy credentials | Operator-owned env (BYO) — not pasted in-app | F7.a / #697; [Corpus: tech-spec] env-contract |

**Journeys:** UJ-001/005 (convert), UJ-013/015–018 (workbench), UJ-020/021 (decode/preview),
UJ-027–030 (dissemination when used) — [Corpus: journeys].

---

## 2. What the tool implements (pipeline)

End-to-end strategy for profile **`annex3`** (and overlay **`iwxxm_us`** where national
REMARKS apply). Stages are separate — do not treat XSD success as “Annex 3 compliant TAC”.

| Stage | Proves | Strategy SoT | Engine |
|-------|--------|--------------|--------|
| 1. TAC lint | TAC matches templates + vocab | [TAC_VALIDATION.md](../domain/TAC_VALIDATION.md) | `packages/tac-validate` |
| 2. Convert | Tokens → IWXXM structure / nilReasons | [IWXXM_CONVERSION.md](../domain/IWXXM_CONVERSION.md) | `packages/tac2iwxxm` |
| 3–5. Well-formed + XSD + Schematron | Structure + business rules + RDF codelists | [IWXXM_VALIDATION.md](../domain/IWXXM_VALIDATION.md) | `packages/iwxxm-validate` |
| 6. Golden pairs | Official TAC↔XML examples | `schemas.wmo.int/iwxxm/2025-2/examples/` (+ vendored) | CI / Examples catalog |
| 7. Bulletin / ops | AHL / COLLECT / translation attrs | [ICAO_OPMET_COMPLIANCE.md](../domain/iwxxm/ICAO_OPMET_COMPLIANCE.md) | bulletin + F16–F19 |

Hub: [docs/domain/README.md](../domain/README.md).

**Conflict rule:** when sources disagree, defer to the **latest machine pin** in
[`vendor/manifest.json`](../../vendor/manifest.json) / `https://schemas.wmo.int/iwxxm/<pin>/`
over older printed tables or workshop decks.

---

## 3. Runtime pins (what the UI validates against)

| Bundle | Pin | Upstream |
|--------|-----|----------|
| IWXXM schemas | **v2025-2** | [wmo-im/iwxxm](https://github.com/wmo-im/iwxxm) |
| Codelists | **49-2** | [wmo-im/iwxxm-codelists](https://github.com/wmo-im/iwxxm-codelists) |
| Modelling | **v2025-2** | [wmo-im/iwxxm-modelling](https://github.com/wmo-im/iwxxm-modelling) |
| Translation suite | tip (informative) | [wmo-im/iwxxm-translation](https://github.com/wmo-im/iwxxm-translation) — not encode SoT |
| IWXXM-US | **3.0** | NWS tarball (manifest URL) |

Local trees: `vendor/schemas/*` (read-only). Version picker **Latest / Previous** aligns with
supported lines in [VERSION_SUPPORT_POLICY.md](../domain/iwxxm/VERSION_SUPPORT_POLICY.md)
(typically **2025-2** + **2023-1**).

Public schema root: <https://schemas.wmo.int/iwxxm/2025-2/>  
Vocabulary: <https://codes.wmo.int/>

---

## 4. Products and profiles

| Product | Operator entry | Primary normative TAC / practice | Encode / validate |
|---------|----------------|----------------------------------|-------------------|
| METAR / SPECI | Workbench + My METARs filter | ICAO Annex 3 (paywall); FMH-1 for US REMARKS | pin XSD/SCH; iwxxm-us when profile set |
| TAF | Workbench | Annex 3 App 5; WMO-306 FM forms | `taf.xsd` + SCH |
| SIGMET / AIRMET | Workbench | Annex 3 + EUR Doc 014 (public) | `sigmet.xsd` / `airmet.xsd` |
| VAA / TCA | Workbench | Annex 3 App 2 templates | product XSDs + SCH |
| SWXA / VONA | When catalogued | FM 205 / pin examples | product XSDs |

Coverage matrix: [COVERAGE_MATRIX.md](../domain/rules/COVERAGE_MATRIX.md).  
Master URL catalog: [RULE_SOURCE_URLS.md](../domain/rules/RULE_SOURCE_URLS.md).

**Profiles**

| Profile | TAC rules | Encode | Validate |
|---------|-----------|--------|----------|
| `annex3` | Annex 3 + WMO-306 + codes.wmo.int | pin examples + TAC-to-XML-Guidance | vendor IWXXM 2025-2 |
| `iwxxm_us` | FMH-1 / NWS + Annex 3 core | `extension` via iwxxm-us 3.0 | WMO base + US catalogs |

---

## 5. Workbench surfaces → sources

### 5.1 Product / profile / IWXXM version pickers

- **UI:** selects feed convert/lint/validate requests.  
- **Sources:** F6 product model [Corpus: product §F6]; version policy
  [VERSION_SUPPORT_POLICY.md](../domain/iwxxm/VERSION_SUPPORT_POLICY.md); pin in manifest.

### 5.2 Manual TAC input modes (TAC / AHL / COLLECT)

- **UI:** mode switch + auto-detect (ADR-024 / UJ-025).  
- **Sources:** AHL format from WMO community AHL page + WMO-No. 386 heading pattern
  (see PPT-02 mining notes §Exchange / AHL); COLLECT packing per OPMET IWXXM Exchange
  Guidelines (public PDF — [RULE_SOURCE_URLS](../domain/rules/RULE_SOURCE_URLS.md)).  
- **Engine:** bulletin helpers in `tac2iwxxm`; COLLECT member extract may still 501 for
  some paths (documented deferred).

### 5.3 CodeMirror editor + span highlights

- **UI:** live editor; highlights lint/validate `start`/`end`.  
- **Sources:** F7.b/#702 spans; issue codes from [ISSUE_CATALOG](../domain/rules/ISSUE_CATALOG.md)
  (`packages/tac-validate`).  
- **Stack:** CodeMirror 6 — [Corpus: tech-spec] dependency-inventory.

### 5.4 Decode panel (Code | Explanation) + plain-language summary

- **UI:** token segments + F9 value-aware summary.  
- **API:** `POST /api/v1/decode-tac` — [Corpus: api].  
- **Sources:** explanations are **operator-facing paraphrases**, not Annex 3 reprints;
  residual undecoded tokens stay explicit (F7 G4). Normative templates remain Annex 3 /
  WMO-306 (cite only).

### 5.5 Lint console + issue catalog

- **UI:** one line per issue; catalog shows WMO/ICAO/IWXXM source attribution (EV-040).  
- **Sources:** ISSUE_CATALOG ↔ [RULE_SOURCE_URLS](../domain/rules/RULE_SOURCE_URLS.md) ↔
  [PROVENANCE_MAP](../domain/rules/PROVENANCE_MAP.md) (S043 / EV-035).  
- **API:** lint-tac + `/lint-issue-catalog`.

### 5.6 Soft-fail preview / Failed-TAC cue

- **UI:** best-effort IWXXM + failed-span markers; distinct failure cue (F7.c / F10).  
- **Sources:** translation-failure retention pattern (`translationFailedTAC`) described in
  OPMET/IWXXM practice and informative PPT-02 slide 9 — prefer vendored `common.xsd`
  attribute names; [IWXXM_CONVERSION.md](../domain/IWXXM_CONVERSION.md).

### 5.7 Live IWXXM preview + Strict Validation

- **UI:** debounced convert/validate; optional XSD+Schematron on hard Convert.  
- **Sources:** vendored XSD + `rule/iwxxm.sch` + offline RDF — [IWXXM_VALIDATION.md](../domain/IWXXM_VALIDATION.md).

### 5.8 Examples catalog (golden / official demos)

- **UI:** load TAC, AHL, Collect, product goldens (F7.g; EV-040 official AHL/Collect).  
- **Sources:** WMO example trees under pin (`examples/`); US fixtures where labeled;
  catalog rows should show provenance — do not invent TAC.

### 5.9 Dissemination drawer (optional)

- **UI:** one-shot BYOC destinations (memory-only credentials).  
- **Sources:** [Corpus: product] F16–F19; ADR-029/030; egress allowlist — **not** F8 auto-push.
- **Ops:** see dissemination docs in tech-spec / feature-list; do not store pasted secrets.

### 5.10 Sessions / history

- Guest: IndexedDB; Logged-in: DO Postgres via Auth (F31).  
- **Sources:** [Corpus: product] F5/F7/F31; privacy F22.

---

## 6. “Where did this rule come from?”

1. Note the **issue code** in the lint console or catalog.  
2. Open [ISSUE_CATALOG.md](../domain/rules/ISSUE_CATALOG.md) (or JSON twin).  
3. Follow links into [RULE_SOURCE_URLS.md](../domain/rules/RULE_SOURCE_URLS.md) and
   [PROVENANCE_MAP.md](../domain/rules/PROVENANCE_MAP.md).  
4. For dig detail, open the matching file under [docs/domain/mining/](../domain/mining/).  
5. If Access = **paywall**, obtain the official ICAO Store / WMO Library edition — the repo
   will not contain the PDF prose.

---

## 7. Citation and paywall policy (operators)

| Source class | Access | Operator action |
|--------------|--------|-----------------|
| ICAO Annex 3, Doc 8896 / 10003 | Paywall | Cite title + section; purchase for full text |
| WMO-No. 306 Vol I.3 | Library / captcha | Use library landing; local extracts stay gitignored |
| codes.wmo.int / schemas.wmo.int | Public | Prefer HTTPS landings; consume via vendor pin in CI |
| FMH-1 / iwxxm-us | Public | US profile only; still no need to paste full handbooks |
| Workshop PPT-02 | Public informative | Never treat as encode/validate SoT |

Full policy: [ACCESS_AND_CITATION.md](../domain/rules/ACCESS_AND_CITATION.md).

---

## 8. Typical operator flows (short)

1. **Happy path** — Select product + profile + version → paste/load TAC → review decode +
   lint → Convert (Strict on if you need Schematron) → download / disseminate.  
2. **Repair loop** — Click lint span → fix TAC → watch live preview.  
3. **Bulletin** — Switch to AHL or COLLECT mode → use official examples first → convert.  
4. **US REMARKS** — Profile `iwxxm_us` → expect FMH-1 / iwxxm-us extension path.

Detailed E2E IDs: [Corpus: journeys] UJ-013–021, UJ-025, UJ-032.

---

## 9. Deploy / env pointers (not duplicated here)

| Need | Doc |
|------|-----|
| Deploy topology | [deploy.md](../deploy.md) |
| Env sync | [env-sync-runbook.md](./env-sync-runbook.md) |
| Config / env names | [Corpus: tech-spec] → env-contract / config-spec |
| Local development | [DEVELOPMENT.md](./DEVELOPMENT.md) |

---

## 10. Briefing deck

For stakeholder presentations on **sources used to build the tool**, use
[../guides/operator-sources-pptx/](../guides/operator-sources-pptx/) and follow
`build-walkthrough.md`. Do not commit the finished `.pptx` unless explicitly requested.
