#!/usr/bin/env python3
"""
Mirror complete IWXXM version bundles from schemas.wmo.int

Downloads schemas, examples, HTML docs, XMI models, and RDF codelists
for offline validation.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.schema_mirror_service import SchemaMirrorService
from src.config.iwxxm_versions import SUPPORTED_VERSIONS, RC_VERSIONS


async def mirror_all():
    """Mirror all stable versions and RC versions."""
    base_path = Path(__file__).parent.parent / "schemas" / "iwxxm"
    
    service = SchemaMirrorService(base_path=base_path)
    
    # Stable versions
    versions_to_mirror = [
        ("2023-1", SUPPORTED_VERSIONS["2023-1"]),
        ("2025-2", SUPPORTED_VERSIONS["2025-2"]),
    ]
    
    # RC versions (optional)
    # versions_to_mirror.extend([
    #     ("2025-2RC1", RC_VERSIONS["2025-2RC1"]),
    #     ("2025-2RC2", RC_VERSIONS["2025-2RC2"]),
    # ])
    
    for version, config in versions_to_mirror:
        print(f"\n{'='*60}")
        print(f"Mirroring {version}")
        print(f"{'='*60}")
        
        root_xsd_url = config["schema_url"]
        
        result = await service.mirror_version(
            version=version,
            root_xsd_url=root_xsd_url,
            include_examples=True,
            include_html=True,
            include_xmi=True
        )
        
        print(f"\n✓ Mirrored {version}:")
        print(f"  - {result.get('xsd_count', 0)} XSD files")
        print(f"  - {result.get('example_count', 0)} example files")
        print(f"  - {result.get('html_count', 0)} HTML files")
        print(f"  - {result.get('xmi_count', 0)} XMI files")


if __name__ == "__main__":
    asyncio.run(mirror_all())
