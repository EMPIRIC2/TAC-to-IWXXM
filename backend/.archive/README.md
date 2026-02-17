# Archived Files

This directory contains deprecated and backup files that should not be used in production.

## Files

### conversion.py.bak
**Original location:** `/backend/conversion.py`  
**Deprecated:** Yes  
**Reason:** Replaced by enhanced version at `src/utilities/conversion.py`

**Why it was kept:**
- Provides historical reference for wrapper logic
- GIFTs path resolution code may be useful

**What to use instead:**
```python
from src.utilities.conversion import convert_metar_tac
```

### schematron_validator.py.bak
**Original location:** `/backend/schematron_validator.py`  
**Deprecated:** Yes  
**Reason:** Replaced by improved version at `src/utilities/schematron_validator.py`

**Why it was kept:**
- Provides reference for validation patterns
- Docker validator improvements available in newer version

**What to use instead:**
```python
from src.utilities.schematron_validator import get_schematron_validator, SchematronValidationResult
from src.utilities.schematron_validator_docker import SchematronValidatorDocker
```

## Archive Policy

Files are moved to `.archive/` when:
1. Functionality is superseded by a better implementation
2. The original is being refactored
3. Legacy code is kept for reference only
4. Multiple versions need to be compared

### Handling Archived Files

**To reference archived code:**
```python
# Import from archive (not recommended)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / '.archive'))
import conversion  # ⚠️ Not recommended
```

**To restore archived files:**
```bash
# Copy from archive
cp .archive/conversion.py.bak conversion.py

# Or examine and migrate to current version
cat .archive/conversion.py.bak
# ...migrate logic to src/utilities/conversion.py
```

## Cleanup Schedule

Archived files are typically removed after:
- 1 release cycle (if referencing old API)
- 3 months (if kept for compatibility)
- Explicit deprecation notice (if part of breaking changes)

Current archived files have been in archive since **Jan 28, 2026** and can be removed after **Apr 28, 2026** if no longer needed.

## Best Practices

1. **Don't import from .archive/** - Use current implementations
2. **Don't modify archived files** - They're frozen as reference
3. **Document new archives** - Add entry to this README
4. **Review periodically** - Clean up unused archives quarterly

---

**Archive created:** February 17, 2026  
**Last updated:** February 17, 2026
