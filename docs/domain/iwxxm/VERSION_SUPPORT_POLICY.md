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
2. **ICAO Doc 10003**: Recommends supporting latest + 1 prior version
3. **Regional Compliance**: EUR/NAM regions have moved to 2023-1+ only

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
- [WMO No.306 Volume I.3](https://library.wmo.int/index.php?lvl=notice_display&id=19508) - Manual on Codes, Part D
- [IWXXM Community Platform](https://community.wmo.int/activity-areas/wis/iwxxm) - WMO IWXXM resources
- [VERSION_MANIFEST.json](../schemas/VERSION_MANIFEST.json) - Technical version registry

---

**Last Updated**: 2026-02-13  
**Policy Version**: 2.0  
**Next Review**: After next WMO amendment release
