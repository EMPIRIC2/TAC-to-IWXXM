# IWXXM release-line adoptability (engineering)

> **Ticket**: [#808](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/808) · **Session**: S040 / EV-032 · **TC**: TC-EV032-004  
> **Audience**: engineers touching vendor pins, F4 enums, encode/validate, goldens, PyPI  
> **Non-technical companion**: [#847](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/847) (T3.2)  
> **Policy SoT**: [VERSION_SUPPORT_POLICY.md](./VERSION_SUPPORT_POLICY.md) — **latest + 1 prior**  
> **Architecture**: [IWXXM_VERSION_SWITCHING.md](./IWXXM_VERSION_SWITCHING.md) · ADR-001 · ADR-027  
> **Constraint**: this assessment does **not** re-pin or hand-edit `vendor/schemas/*`.

## Recommendation (product window)

**Keep latest + 1 prior** (today: **2025-2** default + **2023-1** previous).

| Option | Verdict |
|--------|---------|
| Keep latest+1 | **Recommended** — matches policy, PPT-02 operational pair, OPMET community framing; CI/fixture cost is known |
| Shrink to latest-only | Reject for now — operators still need 2023-1 during transition; FE/API already expose both |
| Expand to latest+2 | Reject — multiplies XSD+SCH+golden+codegen+wheel size without policy demand |

**Next-line readiness:** adoptability is **moderate friction, high blast radius, mostly checklist-driven**. A new WMO `YYYY-N` is feasible in one evolve/sync PR series if checklists below are followed; largest risks are ADR-032 golden churn, Schematron/xslt2 path, and FE/API enum drift — not the vendor sync script itself.

**Rough effort (one new line, keep prior):** 3–8 engineer-days depending on breaking XSD/SCH deltas and how many product goldens fail equality — exclusive of deep encode quality work for new product elements.

---

## Blast-radius map

Surfaces that **must** change (or be verified green) when adding or dropping an IWXXM year line:

| Layer | Paths / artifacts | What breaks if skipped |
|-------|-------------------|------------------------|
| **Vendor pin** | `vendor/manifest.json` · `vendor/schemas/iwxxm/{line}/` · sync `scripts/vendor/sync_iwxxm.py` / `sync-iwxxm.sh` · `check_upstream.py` | Wrong/missing XSD+SCH+examples |
| **Sibling pins** | `iwxxm-codelists`, `iwxxm-modelling` (often same tag family); `iwxxm-translation` (informative fixtures); **`iwxxm-us`** (NWS cadence — may lag) | Codelist hrefs / US extension mismatch |
| **F4 config** | `apps/backend/src/config/iwxxm_versions.py` (`SUPPORTED_VERSIONS`, `DEFAULT_VERSION`, remaps, breaking-change table) · `version_metadata.py` · `version_migration.py` · `version_detector.py` | 400 on valid line; silent remap bugs |
| **Schema resolve** | `apps/backend/src/utilities/schema_registry.py` · validation services / routers | Validate against wrong tree or mix lines |
| **Convert (F6)** | `packages/tac2iwxxm` (`iwxxm_version` on `convert`, namespaces, profile emit) · annex3 / iwxxm_us profiles | Wrong NS / element set for line |
| **Validate (F2/F13)** | `packages/iwxxm-validate` (`paths`, `xsd`, `schematron`, bundled schemas in wheels) | PyPI wheel ships stale schemas; SCH from wrong line |
| **Codegen** | ADR-027 · `scripts/codegen/iwxxm_xsd.py` · `packages/shared/.../iwxxm_xsd/` | Stale typed bindings |
| **API / OpenAPI** | Form field `iwxxm_version`; ICAO OPMET / stats schemas listing supported versions | Client enums diverge from runtime |
| **Frontend (F7)** | Workbench version `<select>`; prefs persistence + migrate unsupported → default; `api.ts` default `2025-2`; Examples goldens tied to pin examples | Operators stuck on deprecated; prefs strand |
| **Worker (F8)** | `apps/worker` settings / pipeline `iwxxm_version` | Ingest writes wrong line |
| **Goldens / CI** | `annex3_golden/*`, ADR-032 equality, `examplesCatalog.ts`, `wmo_official_tac_inventory.py`, path-filtered canaries, `make test-*-quality` | Red CI or silent `wmoReference` debt |
| **Docs** | This file · VERSION_SUPPORT_POLICY · CHANGELOG · FIXTURE_GAPS · COVERAGE_MATRIX example rows | Policy/ops drift |
| **Dissemination** | Optional `iwxxm_version` on send/preflight metadata | Metadata mismatch only (egress unchanged) |

**Does not require line bump by itself:** F16–F19 sink adapters, Supabase auth, dissemination allowlist.

---

## Overlap with #804 / #807

| Ticket | Role vs this assessment |
|--------|-------------------------|
| [#804](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/804) | Deep `IWXXM/` tree mine (examples/rules surfaces) — **evidence**, not adopt runbook |
| [#807](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/807) | Org / sibling refresh ranking — **evidence** for which repos to watch |
| **#808 (this)** | End-to-end **adopt/deprecate ops** + blast radius; **no** duplicate deep tree/org mining |

Pin-vs-tip watch: use `#804` / `#807` digs + `scripts/vendor/check_upstream.py` against `vendor/manifest.json` tags. Do not re-mine full trees inside #808.

---

## Pin vs tip / next-release watch (informative)

| Check | How |
|-------|-----|
| Manifest pin | `vendor/manifest.json` → `iwxxm.tag` (today **`v2025-2`**) |
| Upstream tip | `scripts/vendor/check_upstream.py` / GitHub `wmo-im/iwxxm` tags & ReleaseNotes |
| Breaking themes to triage | New/removed XSD types; Schematron assert IDs; example stem add/drop; namespace year; codelist URI drift; product roots (e.g. VONA entered 2025-2) |
| US pin | `iwxxm-us` **3.0** tarball — confirm NWS still targets same WMO base before assuming US encode still validates |
| **iwxxm-modelling** (corpus G8) | On **every vendor sync PR**: skim `wmo-im/iwxxm-modelling` tip vs `vendor/manifest.json` modelling pin — note UML/EA / Pattern-ID taxonomy deltas that inform **latest+1** adopt window. **Short watch only** — do **not** re-run full org mine [#807](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/807). Child [#861](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/861) · S046 / EV-038 · **TC-EV038-002** |

**No re-pin in EV-032 / #808.** File children when automation would reduce manual triage (T3.3).

---

## Adopt-new-line checklist

Ordered steps to add WMO line `YYYY-N` as **latest**, demoting current latest → **previous** (policy window stays two lines). Align with [VERSION_SUPPORT_POLICY.md](./VERSION_SUPPORT_POLICY.md) §Deprecation Process.

### A. Vendor & codegen

1. [ ] Read upstream ReleaseNotes / diff vs current pin (informative; cite #804 surfaces).
2. [ ] Sync `iwxxm` (and matching `iwxxm-modelling` / codelists as needed) via `scripts/vendor/sync_iwxxm.py` — **sync PR only**; never hand-edit under `vendor/schemas/*`.
3. [ ] **iwxxm-modelling delta watch (G8 / #861):** record tip-vs-pin Modelling/UML/Pattern-ID notes in the sync PR (or linked issue) — informs latest+1; **no** duplicate [#807](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/807) org mine.
4. [ ] Update `vendor/manifest.json` tag + SHA + tree hash.
5. [ ] Run ADR-027 xsdata codegen (`scripts/codegen/iwxxm_xsd.py`); commit generated status/artifacts.
6. [ ] Confirm `iwxxm-validate` wheel bundle / MANIFEST includes the new tree.

### B. Runtime enums & remaps

7. [ ] Add `YYYY-N` to `SUPPORTED_VERSIONS` in `apps/backend/src/config/iwxxm_versions.py`; set `DEFAULT_VERSION`.
8. [ ] Record breaking-change notes + any remap aliases (peer `2025-1`→`2025-2`).
9. [ ] Demote prior latest → previous; schedule old previous for 6-month warning (policy).
10. [ ] Smoke `normalize_version` / deprecated → HTTP 400 paths.

### C. Convert / validate

11. [ ] Convert smoke per product family on new default (METAR…VONA as in catalog).
12. [ ] XSD + Schematron on official peers for **that line only** (never mix SCH across lines).
13. [ ] Rebaseline or soft→strict ADR-032 goldens; update `wmoPass` / `wmoReference` intentionally.
14. [ ] Refresh `wmo_official_tac_inventory` / FIXTURE_GAPS / Examples catalog as peers appear.

### D. UI / worker / API

15. [ ] FE version picker options + prefs migration for dropped lines → new default.
16. [ ] Worker default `iwxxm_version` if deploy sets it.
17. [ ] OpenAPI / client docs for `iwxxm_version` enum.

### E. Docs & release

18. [ ] Update VERSION_SUPPORT_POLICY table + Appendix A package matrix if package numbers change.
19. [ ] CHANGELOG / deploy notes; link non-technical handoff (#847).
20. [ ] CI: `validate-fast` + relevant `make test-*-quality` / canaries green on sync PR.

---

## Deprecate-old-line checklist

When policy moves a line from **previous** → **warning** → **unsupported**:

1. [ ] **Open a tracked reminder** with
   [`.github/ISSUE_TEMPLATE/iwxxm_deprecation_warning.md`](../../../.github/ISSUE_TEMPLATE/iwxxm_deprecation_warning.md)
   when the line enters the **6-month warning** window ([#855](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/855) · **TC-EV038-003**).
   Fill VERSION_SUPPORT_POLICY + [RELEASE_LINE_STAFF_GUIDE](./RELEASE_LINE_STAFF_GUIDE.md) checklist fields.
2. [ ] Announce 6-month warning (CHANGELOG + operator-facing #847 copy); link the reminder issue.
3. [ ] Confirm FE prefs migrate unsupported values to default (existing tests cover legacy `2.1`→`2025-2` pattern).
4. [ ] Remove from `SUPPORTED_VERSIONS`; keep explicit `VersionDeprecatedError` / 400 message listing remaining supported.
5. [ ] Stop shipping removed tree in `iwxxm-validate` wheels (size + correctness).
6. [ ] Drop or archive line-specific goldens/CI that only exercised the dropped line.
7. [ ] Update VERSION_SUPPORT_POLICY “Currently Supported” + FAQ; remove picker option.
8. [ ] Grep for hard-coded version strings (`2023-1`, etc.) in apps/packages/tests/docs — fix stragglers.
9. [ ] Verify IndexedDB / work-session prefs do not strand operators (F7.h).

### Dry-run note (#855 — no fake deprecation)

**2026-08-05 (S046 / EV-038):** Template + checklist step documented only. Do **not** open a
live deprecation issue while `2023-1` remains supported **previous** under current policy.
First real use is when a line actually enters the warning window.

---

## Friction points (maintainability)

| Friction | Severity | Mitigation |
|----------|----------|------------|
| ADR-032 golden equality vs vendor XML | High | Soft→strict per stem; catalog tiers; path-filtered canaries |
| Dual-line CI time / disk | Medium | Keep window at 2; quality packs path-filtered |
| Manual ReleaseNotes triage | Medium | Child: structured triage template / CI tip-diff summary |
| `iwxxm-us` lag vs WMO line | Medium | Explicit check on every WMO adopt; child if US encode blocks |
| Enum duplication (backend vs FE defaults) | Medium | Child: single generated supported-versions artifact |
| Schematron xslt2 / Docker path | Medium | Line-local SCH only; keep smoke in canaries |
| Codelist URI drift vs codes.wmo.int | Low–Med | Periodic check (gap G6 → child under #846/#808) |

---

## Automation gaps → children (filed T3.3)

| Gap | Issue |
|-----|-------|
| Supported-versions single source (FE/OpenAPI) | [#851](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/851) |
| Sync PR tip-diff summary (+ golden fail list can ride along) | [#852](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/852) |
| iwxxm-us compatibility gate | [#853](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/853) |
| UX Latest/Previous picker labels | [#854](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/854) |
| Deprecation calendar / reminder template | [#855](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/855) — **template landed** S046/EV-038 |
| iwxxm-modelling delta watch (G8) | [#861](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/861) — sync-PR checklist step |

Related corpus residuals (G6 codelist drift) may fold into #852 or stay under #846.

---

## Index

| Doc | Role |
|-----|------|
| [VERSION_SUPPORT_POLICY.md](./VERSION_SUPPORT_POLICY.md) | Support window + deprecation process |
| [IWXXM_VERSION_SWITCHING.md](./IWXXM_VERSION_SWITCHING.md) | F4 architecture |
| This file | Engineering adopt/deprecate + blast radius |
| S040 [t3.1 report](../../sessions/S040-iwxxm-corpus-quality/reports/t3.1-808-adoptability.md) | Session close notes for T3.1 |

*Written 2026-08-04 — S040 / EV-032 T3.1.*
