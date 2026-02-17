# IWXXM Schema Versions

This document tracks the specific commits/tags used for each IWXXM schema version.

## Directory Structure

Schemas are organized by version for independent schema management:

```
schemas/
├── iwxxm/
│   ├── 2025-2/          # Latest IWXXM version
│   │   └── IWXXM/       # Schema files
│   └── 2023-1/          # Previous IWXXM version
│       └── IWXXM/       # Schema files
├── iwxxm-modelling/
│   ├── 2025-2/          # Latest modelling version
│   └── 2023-1/          # Previous modelling version
└── iwxxm-codelists/     # Shared codelists (version-agnostic)
```

## IWXXM 2025-2

**Repository:** https://github.com/wmo-im/iwxxm

**Commit:** Current master (2c4db03)
**Tag:** v2025-2
**Release Date:** November 25, 2025
**WMO Amendment:** 82

**Key Changes from 2023-1:**
- Runway state removed from METAR products
- `measures.xsd` removed (merged into `common.xsd`)
- Split NIL codelists for better handling
- Updated namespace: `http://icao.int/iwxxm/2025-2`

## IWXXM 2023-1

**Repository:** https://github.com/wmo-im/iwxxm

**Commit:** e84bf544702e6a3c638e7ab5f02a9c930dda57f7
**Release:** IWXXM 2023-1 (#320)
**Release Date:** June 2, 2023
**WMO Amendment:** 78

**Features:**
- Includes `measures.xsd`
- Traditional NIL handling
- Full runway state support
- Namespace: `http://icao.int/iwxxm/2023-1`

## IWXXM Modelling 2025-2

**Repository:** https://github.com/wmo-im/iwxxm-modelling

**Commit:** Current master (4c7fbbf)
**Tag:** v2025-2
**Release Date:** November 25, 2025

**UML Models for IWXXM 2025-2 schemas**

## IWXXM Modelling 2023-1

**Repository:** https://github.com/wmo-im/iwxxm-modelling

**Commit:** 2c1edcdabf26792263ab214df9531665e3b5a867
**Release:** Merge pull request #25
**Date:** Prior to 2025-2 release

**UML Models for IWXXM 2023-1 schemas**

## Codelists

**Repository:** https://github.com/wmo-im/iwxxm-codelists

The codelists repository is version-agnostic and provides RDF codelist definitions used across all IWXXM versions.

## Updating Schemas

To update to a newer commit/tag:

1. Navigate to the schema directory:
   ```bash
   cd schemas
   ```

2. Run the reorganization script with new commits:
   ```bash
   ./reorganize_schemas.sh
   ```

3. Update commit references in this file

4. Verify schemas load correctly:
   ```bash
   cd ../backend
   pytest tests/test_metar_pairs_comprehensive.py -v
   ```

## Schema Validation

All schemas are validated during testing:
- XSD validation via `xsd_validator.py`
- Schematron validation via `schematron_validator.py`
- Version-specific paths in `config/iwxxm_versions.py`

Last Updated: 2026-02-14
