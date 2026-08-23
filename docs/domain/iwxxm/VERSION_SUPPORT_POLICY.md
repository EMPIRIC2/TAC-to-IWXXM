# IWXXM Version Support Policy

## Deprecation Date: February 13, 2026

### Immediately Deprecated Versions

The following IWXXM versions are **no longer supported** as of February 13, 2026:

- **IWXXM 2021-2** (WMO Amendment 73)
- **IWXXM 2018 / 2018-2** (WMO Amendment 78-draft)
- **IWXXM 2016 / 2016-1** (WMO Amendment 77)
- **IWXXM 3.0.0 and 3.0-dev** (Legacy versioning scheme)

### Currently Supported Versions

| Version | Status | WMO Amendment | Release Date | Support Until |
|---------|--------|---------------|--------------|---------------|
| **2025-2** | Latest (Default) | 82 | 2025-11-25 | Active |
| **2023-1** | Previous | 78 | 2023-06-02 | 18 months after next WMO amendment |

### Default Behavior

- All conversions use **IWXXM 2025-2** by default
- Users can explicitly request **IWXXM 2023-1** for legacy system compatibility
- Requests for deprecated versions will receive **HTTP 400 Bad Request** with error message

**Validate against the requested year line only:** XSD + Schematron from that vendored tree
(`2025-2/…` or `2023-1/…`) — never mix SCH across lines
([../IWXXM_VALIDATION.md](../IWXXM_VALIDATION.md) §Validation strategy). Package × line numbers:
[Appendix A](#appendix-a--package--iwxxm-line-matrix-informative).

### Profile-scoped operational lines (not global defaults)

Some **semantic profiles** pin a different IWXXM year line than the app default **2025-2**:

| Profile | Operational line | Vendor core | National extension | API trigger |
|---------|------------------|-------------|-------------------|-------------|
| `CA_ECCC` | IWXXM **3.0.0** (`http://icao.int/iwxxm/3.0`) | `vendor/schemas/iwxxm/3.0.0/` | `vendor/schemas/iwxxm-ca/3.0/` | `semantic_profile=CA_ECCC` (+ optional `extensions: [IWXXM_CA]`) |

**Important:** 3.0.0 is **not** a globally selectable convert default — it is profile-scoped per
[ADR-036](../../../adr/ADR-036-semantic-vs-exchange-profiles.md). Requests with `iwxxm_version`
other than `3.0.0` while `semantic_profile=CA_ECCC` are rejected (fail-closed).

Manifest truth today: `iwxxm-ca` is pinned in `vendor/manifest.json`; 3.0.0 core co-locates
under `vendor/schemas/iwxxm/3.0.0/` (integrity test in `tests/vendor/`). EV-068 may formalize
a separate manifest bundle entry for the 3.0.0 line (#1027).

## Support Window Policy

### Standard Support Window
- **Latest version** + **1 prior version** (currently 2025-2 + 2023-1)
- Total support window: **18 months** from next WMO amendment release
- Aligns with ICAO transition period requirements

### Deprecation Process
When a new IWXXM version is released:
1. New version becomes "latest"
2. Previous "latest" becomes "previous" 
3. Previous "previous" enters 6-month deprecation warning period
4. After 6 months, unsupported version is fully deprecated

**Example Timeline:**
```
2025-11-25: 2025-2 released → becomes "latest"
            2023-1 remains "previous"
            2021-2 deprecated immediately (>18 months old)

Future (2027+): When next version releases:
            New version → "latest"
            2025-2 → "previous"
            2023-1 → 6-month warning → deprecated
```

## Rationale for Deprecation

### Technical Reasons
1. **Code Complexity**: Supporting multiple versions increases maintenance burden by ~30%
2. **Test Coverage**: Removes 75+ obsolete test cases
3. **Breaking Changes**: Pre-2023 versions have incompatible validation rules
4. **Schema Evolution**: 2021-2 and earlier lack modern codelist structures

### Standards Alignment
1. **WMO Amendment Cycle**: ICAO/WMO update standards every 12-18 months
2. **ICAO / OPMET version framing**: Project policy aligns to **latest + 1 prior** version. The public [OPMET IWXXM Exchange Guidelines 5th Ed. (Oct 2023)](../mining/OPMET-IWXXM-Exchange-Guidelines-5th-mining-notes.md) §3.1.7 points operators to the WMO **community compatibility table** for which package is operational after each Annex 3 applicability date — it does **not** itself define an “N and N−1” support window, nor (in that edition) PPT-02’s “deprecate ≤2021-2 after 2025-2” wording. Doc 10003 Advance 2014 also lacks a version window ([notes](../mining/ICAO-Doc-10003-draft-2014-mining-notes.md)). Prefer community table + this project policy for runtime; confirm any Doc 10003 wording against the purchased published edition before citing it as sole SoT.
3. **PPT-02 deck corroboration (informative, 2025-10-22)**: Workshop slide “Operational IWXXM versions for use after Nov 2025” shows exactly the **2023-1** and **2025-2** package columns as the post–Nov 2025 operational pair — consistent with this policy’s supported set. Full amendment history and package numbers: see [Appendix A](#appendix-a--package--iwxxm-line-matrix-informative) and [PPT-02 mining notes](../mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md).
4. **Regional Compliance**: EUR/NAM regions have moved to 2023-1+ only

### Operational Benefits
1. **Faster Validation**: Simplified version detection and schema loading
2. **Better Statistics**: Focus metrics on actively-used versions
3. **Clearer Documentation**: Remove legacy version references

## Migration Path for Users

### If You Were Using 2021-2 or Earlier

**Option 1: Use Default (Recommended)**
- All conversions automatically use IWXXM 2025-2
- No action required
- Best for new integrations

**Option 2: Request 2023-1**
- Add parameter: `iwxxm_version=2023-1` to API requests
- Use for legacy systems needing temporary compatibility
- Plan migration to 2025-2 within 18 months

**Option 3: Convert via Reference System**
- Use WMO reference translation service for old-version data
- Re-process historical archives if needed
- One-time conversion to 2025-2 format

### Breaking Changes to Review

If migrating from 2021-2 → 2023-1:
- Review METAR/SPECI format changes per WMO Amendment 78
- No major breaking changes (primarily codelist updates)

If migrating from 2023-1 → 2025-2:
- **Runway state removed** (`iwxxm:runwayState` element)
- **measures.xsd removed** (features moved to common.xsd)
- See [docs/BREAKING_CHANGES_REGISTRY.json](./BREAKING_CHANGES_REGISTRY.json) for details

## API Error Messages

### Deprecated Version Request
```json
{
  "error": "VersionDeprecatedError",
  "message": "IWXXM version '2021-2' is no longer supported as of 2026-02-13. Pre-2023 versions no longer supported. Supported versions: ['2025-2', '2023-1']",
  "supported_versions": ["2025-2", "2023-1"],
  "deprecated_date": "2026-02-13"
}
```

HTTP Status: **400 Bad Request**

### Unknown Version Request
```json
{
  "error": "ValueError",
  "message": "IWXXM version '2024-1' is not supported. Supported versions: ['2025-2', '2023-1']"
}
```

HTTP Status: **400 Bad Request**

## Frequently Asked Questions

### Q: Why immediate deprecation instead of a grace period?

**A:** Pre-2023 versions have been available for 3+ years. The 18-month support window already provides ample transition time. Immediate deprecation simplifies codebase and reduces technical debt.

### Q: What if I have archived data in old formats?

**A:** Historical data can remain in old formats. When re-processing or distributing, convert to 2025-2 using current conversion service. Original TAC messages can be re-converted at any time.

### Q: Will 2023-1 support be extended?

**A:** 2023-1 will be supported for 18 months after the next WMO amendment (likely until late 2027). After that, only the latest 2 versions will be supported per policy.

### Q: Can I request re-enabling old version support?

**A:** No. Deprecated versions are removed from the codebase. For specialized needs, consider running a private fork with legacy support, or use WMO reference translation services.

## Contact & Support

For questions about version support policy:
- **Technical Support**: [NOC_EMAIL]
- **Standards Compliance**: [STANDARDS_EMAIL]
- **WMO Amendment Information**: https://community.wmo.int/activity-areas/wis/iwxxm

## References

- [ICAO Doc 10003](https://store.icao.int/en/manual-on-the-icao-meteorological-information-exchange-model-doc-10003) - Manual on the Digital Exchange of Aeronautical Meteorological Information
- [WMO No.306 Volume I.3](https://library.wmo.int/idurl/4/35769) - Manual on Codes, Part D (2023)
- [Focused mining notes (METAR/SPECI + nilReason)](../mining/WMO-306-vI-3-2023-mining-notes.md)
- [IWXXM Community Platform](https://community.wmo.int/iwxxm) — intended WMO IWXXM hub + compatibility table (**HTTP 404** as of 2026-07-14; use [Wayback 2026-03-14](https://web.archive.org/web/20260314162354/https://community.wmo.int/iwxxm) or Appendix A) — [mining notes](../mining/community-wmo-iwxxm-wayback-mining-notes.md)
- [PPT-02 IWXXM Framework mining notes](../mining/PPT-02-IWXXM-Framework-WMO-mining-notes.md) - informative workshop capture (2025-10-22)
- [VERSION_MANIFEST.json](../schemas/VERSION_MANIFEST.json) - Technical version registry
- Runtime pin: `vendor/manifest.json` → `iwxxm` **v2025-2**
- **Engineering adopt / deprecate runbooks + blast radius:** [RELEASE_LINE_ADOPTABILITY.md](./RELEASE_LINE_ADOPTABILITY.md) (#808 / S040 / EV-032)
- **Operator / non-technical staff guide:** [RELEASE_LINE_STAFF_GUIDE.md](./RELEASE_LINE_STAFF_GUIDE.md) (#847 / S040 / EV-032)

---

## Appendix A — Package × IWXXM-line matrix (informative)

Recovered from the WMO community IWXXM “Package compatibility” table (Wayback [2026-03-14 capture](https://web.archive.org/web/20260314162354/https://community.wmo.int/iwxxm) of https://community.wmo.int/iwxxm; page dated **26 November 2025**). Independently matches PPT-02 slide 5 (TT-AvData, 2025-10-22) package numbers. **Live community page was HTTP 404 as of 2026-07-14** — see [mining/community-wmo-iwxxm-wayback-mining-notes.md](../mining/community-wmo-iwxxm-wayback-mining-notes.md). **Not** machine SoT — if this conflicts with vendored XSD `version=` attrs or a restored community table, **defer to vendor pin / restored community table**.

| Package | 1.1 | 2.1 | 3.0 | 2021-2 | 2023-1 | 2025-2 |
|---------|-----|-----|-----|--------|--------|--------|
| METAR and SPECI | 1.1.0 | 2.1.1 | 3.0.0 | 3.1.0 | 3.1.0 | 3.2.0 |
| TAF | 1.1.0 | 2.1.1 | 3.0.0 | 3.0.1 | 3.0.1 | 3.0.2 |
| SIGMET | 1.1.0 | 2.1.1 | 3.0.0 | 4.0.0 | 4.0.1 | 4.0.2 |
| AIRMET | — | 2.1.1 | 3.0.0 | 3.1.0 | 3.1.1 | 3.1.2 |
| Tropical Cyclone Advisory | — | 2.1.1 | 3.0.0 | 3.1.0 | 3.1.0 | 3.1.1 |
| Volcanic Ash Advisory | — | 2.1.1 | 3.0.0 | 3.1.0 | 3.1.0 | 3.2.0 |
| Space Weather Advisory | — | — | 3.0.0 | 3.0.1 | 3.0.1 | 3.1.0 |
| WAFS SIGWX Forecast | — | — | — | 1.0.0 | 1.1.0 | 1.2.0 |
| Quantitative Volcanic Ash Concentration Information | — | — | — | — | — | 1.0.0 |
| Volcano Observatory Notice for Aviation | — | — | — | — | — | 1.0.0 |
| **ICAO Annex 3 Amendment** | **76** | **77** | **78** | **79–80** | **79–81** | **82** |
| **PANS-MET Edition** | — | — | — | — | — | **first** |

**2026-07-14 vendor check:** `2023-1` and `2025-2` columns match `vendor/schemas/iwxxm/{2023-1,2025-2}/IWXXM/*.xsd` package versions (`qvaci`/`vona` absent under 2023-1).

---

**Last Updated**: 2026-07-14  
**Policy Version**: 2.1  
**Next Review**: After next WMO amendment release
