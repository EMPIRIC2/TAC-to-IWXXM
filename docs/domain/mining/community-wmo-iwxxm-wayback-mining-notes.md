# Community WMO IWXXM home (Wayback) — focused mining notes

**Status:** working notes (not normative). Live page **404** as of 2026-07-14; this dig recovers the last useful snapshot.  
**Focus of this pass:** package × Annex 3 compatibility table · linked resource inventory · defer-to-latest vs PPT-02  
**Ticket:** [#719](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/719)  
**Local extracts (gitignored):** `.local/reference/community-wmo-iwxxm-wayback/`

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Domain hub | [../README.md](../README.md) |
| IWXXM validation | [../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) |
| IWXXM conversion | [../IWXXM_CONVERSION.md](../IWXXM_CONVERSION.md) |
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Version policy (ops) | [../iwxxm/VERSION_SUPPORT_POLICY.md](../iwxxm/VERSION_SUPPORT_POLICY.md) Appendix A |

| Item | Value |
|------|-------|
| Title | WMO community IWXXM overview (package compatibility) |
| Publisher | WMO |
| Official landing (intended) | https://community.wmo.int/iwxxm · https://community.wmo.int/en/activity-areas/wis/iwxxm |
| Best recovered snapshot | https://web.archive.org/web/20260314162354/https://community.wmo.int/iwxxm |
| Earlier snapshot | https://web.archive.org/web/20251015180706/https://community.wmo.int/en/activity-areas/wis/iwxxm |
| Pin / edition | Table column **2025-2** (final); Annex 3 Amd **82** |
| Date mined | 2026-07-14 |
| Access | Live **404**; Wayback **public**; local HTML under `.local/reference/community-wmo-iwxxm-wayback/` |
| Label | **informative** index (package matrix historically treated as ops SoT; runtime still vendor pin) |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| Human-readable IWXXM overview + **package compatibility** table vs Annex 3 amendments | Runtime XSD/Schematron (use `schemas.wmo.int` / vendor) |
| Link hub to GitHub schemas/modelling/codelists/translation, Manual I.3, Doc 10003, AHL page | Live page (broken 2026-07-14) |

---

## Product × artifact matrix

| Product | Input | Output package (2025-2 col) | Official / recovered | Gap vs GIFTs | Consumer |
|---------|-------|----------------------------|----------------------|--------------|----------|
| METAR/SPECI | — | **3.2.0** | Wayback table + vendor XSD | — | F4 / encode package select |
| TAF | — | **3.0.2** | same | — | same |
| SIGMET | — | **4.0.2** | same | outside GIFTs | same |
| AIRMET | — | **3.1.2** | same | outside GIFTs | same |
| TCA | — | **3.1.1** | same | outside GIFTs | same |
| VAA | — | **3.2.0** | same | outside GIFTs | same |
| SWX / WAFS / QVACI / VONA | — | 3.1.0 / 1.2.0 / 1.0.0 / 1.0.0 | same | IWXXM-only / non-F6 | optional |

Annex 3 Amendment row: **76…82** (2025-2 → Amd **82**).

---

## Key findings

### Live vs Wayback

- `https://community.wmo.int/iwxxm` and `/en/activity-areas/wis/iwxxm` → **HTTP 404** (2026-07-14).
- Closest useful capture of short URL: **2026-03-14** (page prose “last updated **26 November 2025**”).
- Oct 2025 capture of long URL still showed column **“2025-2 RC2”** and “Latest release” → `schemas.wmo.int/iwxxm/2023-1/` — **superseded** by Nov 2025 final text/table.

### Package compatibility (final 2025-2)

Matches PPT-02 Appendix capture and vendored XSD package versions for **2023-1** / **2025-2** columns (QVACI/VONA only on 2025-2). Full table: `.local/…/extracts/package-compatibility-20260314.md`.

### Linked resources (from snapshot)

Aligned with reference-set §1: `schemas.wmo.int/iwxxm/2025-2/`, `wmo-im/{iwxxm,iwxxm-modelling,iwxxm-codelists,iwxxm-translation}`, `codes.wmo.int/`, Manual I.3 library idurl, Doc 10003 store, AHL page (still live via knowledge-hub redirect).  
`iwxxm-release-communication-plan` also **404** live.

---

## Catalog paste rows

```text
### WMO community IWXXM home (Wayback recovery)
- Publisher: WMO
- URL: https://web.archive.org/web/20260314162354/https://community.wmo.int/iwxxm
- Access: Wayback public; live community path 404
- Applies to: products=[all F6+]; role=[conversion, iwxxm-validation] (package×Amd index)
- Label: informative
- Caveats: Prefer vendor pin for CI; use this snapshot only while live page is down
```

---

## Domain-knowledge cross-check

| Older claim | This source finding | Action |
|-------------|---------------------|--------|
| Community page is live overview + table | Live **404**; Wayback 2026-03-14 has final **2025-2** table | Cite Wayback; keep vendor pin primary |
| Oct 2025 long-URL snapshot / PPT-02 “RC” era | Final column is **2025-2** (not RC2); latest release URL is `/2025-2/` | Defer to Nov 2025 / March Wayback |
| PPT-02 Appendix A matrix | Byte-for-byte same package numbers vs Wayback final table | Corroborated — informative both ways; vendor wins on conflict |

---

## Implications for this repo

- **F4 / VERSION_SUPPORT_POLICY:** Appendix A remains valid corroboration; update “live community table” wording to Wayback while 404 persists.
- **iwxxm-validate / tac2iwxxm:** unchanged — validate/encode against vendored **v2025-2**.
- **Caveats / TBD:** re-check live URL periodically; do not treat Wayback HTML as forever-stable.

---

## Suggested next mining passes

1. When community page returns, re-diff the table against vendor XSD `version=` attrs
2. Drop local HTML after a live re-mine if desired
