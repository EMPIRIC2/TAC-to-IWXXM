"""
OASIS XML Catalog Generator

Generates OASIS XML Catalog files for IWXXM schema versions to enable
offline validation by mapping remote schema URLs to local file paths.
"""

import logging
from pathlib import Path
from typing import List, Optional

from lxml import etree as ET

logger = logging.getLogger(__name__)

# OASIS XML Catalog namespace
CATALOG_NS = "urn:oasis:names:tc:entity:xmlns:xml:catalog"
CATALOG_NS_MAP = {None: CATALOG_NS}


class CatalogGenerator:
    """
    Generates OASIS XML Catalog files for IWXXM schema versions.

    Catalogs map remote WMO schema URLs to local mirrored copies, allowing
    XML validators to resolve imports without network access.
    """

    def __init__(self, schemas_base_path: Path):
        """
        Initialize catalog generator.

        Args:
            schemas_base_path: Base path to mirrored schemas directory
        """
        self.schemas_base_path = Path(schemas_base_path)

    def generate_catalog(self, version: str, remote_base_url: str, local_schema_dir: Optional[Path] = None) -> Path:
        """
        Generate OASIS XML Catalog for a specific IWXXM version.

        Args:
            version: IWXXM version string (e.g., "2025-2RC1")
            remote_base_url: Remote schema base URL (e.g., "https://schemas.wmo.int/iwxxm/2025-2RC1/")
            local_schema_dir: Local directory with mirrored schemas (auto-detected if None)

        Returns:
            Path to generated catalog.xml file
        """
        if local_schema_dir is None:
            local_schema_dir = self.schemas_base_path / version

        if not local_schema_dir.exists():
            raise FileNotFoundError(f"Schema directory not found: {local_schema_dir}")

        logger.info(f"Generating catalog for IWXXM {version}")

        # Create catalog root element
        catalog = ET.Element("{%s}catalog" % CATALOG_NS, nsmap=CATALOG_NS_MAP)

        # Add rewriteURI for main IWXXM schema directory
        self._add_rewrite_uri(
            catalog, uri_start_string=remote_base_url, rewrite_prefix=f"file://{local_schema_dir.absolute()}/"
        )

        # Add common schema dependencies (GML, AIXM, etc.)
        self._add_common_dependencies(catalog, local_schema_dir)

        # Write catalog file
        catalog_path = local_schema_dir / "catalog.xml"
        tree = ET.ElementTree(catalog)
        tree.write(str(catalog_path), encoding="utf-8", xml_declaration=True, pretty_print=True)

        logger.info(f"Generated catalog: {catalog_path}")
        return catalog_path

    def _add_rewrite_uri(self, catalog_elem: ET.Element, uri_start_string: str, rewrite_prefix: str):
        """
        Add rewriteURI element to catalog.

        Args:
            catalog_elem: Catalog root element
            uri_start_string: URL prefix to match
            rewrite_prefix: Local file:// prefix to rewrite to
        """
        rewrite_uri = ET.SubElement(catalog_elem, "{%s}rewriteURI" % CATALOG_NS)
        rewrite_uri.set("uriStartString", uri_start_string)
        rewrite_uri.set("rewritePrefix", rewrite_prefix)

    def _add_common_dependencies(self, catalog_elem: ET.Element, local_schema_dir: Path):
        """
        Add rewrite rules for common schema dependencies.

        Args:
            catalog_elem: Catalog root element
            local_schema_dir: Local schema directory
        """
        # Check for common dependencies and add rewrites
        dependencies = [
            {
                "uri_start": "http://www.opengis.net/gml/3.2",
                "local_path": local_schema_dir / "externalSchema" / "gml" / "3.2.1",
            },
            {
                "uri_start": "http://www.aixm.aero/schema/5.1",
                "local_path": local_schema_dir / "externalSchema" / "aixm" / "5.1",
            },
            {
                "uri_start": "http://www.isotc211.org/2005/gmd",
                "local_path": local_schema_dir / "externalSchema" / "iso" / "19139" / "20070417" / "gmd",
            },
            {
                "uri_start": "http://www.isotc211.org/2005/gco",
                "local_path": local_schema_dir / "externalSchema" / "iso" / "19139" / "20070417" / "gco",
            },
        ]

        for dep in dependencies:
            if dep["local_path"].exists():
                self._add_rewrite_uri(
                    catalog_elem,
                    uri_start_string=dep["uri_start"],
                    rewrite_prefix=f"file://{dep['local_path'].absolute()}/",
                )
                logger.debug(f"Added catalog entry for: {dep['uri_start']}")

    def generate_all_catalogs(self) -> List[Path]:
        """
        Generate catalogs for all mirrored schema versions.

        Returns:
            List of paths to generated catalog files
        """
        catalog_paths = []

        # Find all version directories
        for version_dir in self.schemas_base_path.iterdir():
            if not version_dir.is_dir():
                continue

            version = version_dir.name

            # Skip backup or template directories
            if "backup" in version.lower() or "template" in version.lower():
                continue

            # Detect remote base URL from manifest or config
            manifest_path = version_dir / ".manifest.json"
            if manifest_path.exists():
                import json

                with manifest_path.open("r") as f:
                    manifest = json.load(f)
                    root_url = manifest.get("root_url", "")
                    if root_url:
                        # Extract base URL from root URL
                        remote_base = root_url.rsplit("/", 1)[0] + "/"
                        try:
                            catalog_path = self.generate_catalog(version, remote_base, version_dir)
                            catalog_paths.append(catalog_path)
                        except Exception as e:
                            logger.error(f"Failed to generate catalog for {version}: {e}")

        return catalog_paths

    def validate_catalog(self, catalog_path: Path) -> bool:
        """
        Validate an OASIS XML Catalog file.

        Args:
            catalog_path: Path to catalog.xml file

        Returns:
            True if catalog is valid, False otherwise
        """
        try:
            tree = ET.parse(str(catalog_path))
            root = tree.getroot()

            # Check namespace
            if root.tag != "{%s}catalog" % CATALOG_NS:
                logger.error(f"Invalid catalog root element: {root.tag}")
                return False

            # Check for at least one rewriteURI
            rewrite_uris = root.findall("{%s}rewriteURI" % CATALOG_NS)
            if not rewrite_uris:
                logger.error("Catalog has no rewriteURI elements")
                return False

            logger.info(f"Catalog validation passed: {catalog_path}")
            return True

        except Exception as e:
            logger.error(f"Catalog validation failed: {e}")
            return False


def generate_catalog_for_version(version: str, remote_base_url: str, schemas_base_path: Path) -> Path:
    """
    Convenience function to generate a catalog for one version.

    Args:
        version: IWXXM version string
        remote_base_url: Remote schema base URL
        schemas_base_path: Base path to mirrored schemas

    Returns:
        Path to generated catalog.xml
    """
    generator = CatalogGenerator(schemas_base_path)
    return generator.generate_catalog(version, remote_base_url)


def generate_all_catalogs(schemas_base_path: Path) -> List[Path]:
    """
    Convenience function to generate catalogs for all versions.

    Args:
        schemas_base_path: Base path to mirrored schemas

    Returns:
        List of paths to generated catalogs
    """
    generator = CatalogGenerator(schemas_base_path)
    return generator.generate_all_catalogs()
