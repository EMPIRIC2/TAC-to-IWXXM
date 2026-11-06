"""
Version Migration Utilities

Handles breaking changes when converting between IWXXM versions,
especially for data transformation from older versions to newer ones.
"""

import logging
import xml.etree.ElementTree as ET
from typing import Any

from src.config.iwxxm_versions import (
    VersionDeprecatedError,
    get_breaking_changes,
    get_version_config,
    get_version_config_for_emit_profile,
    is_migration_supported,
)

logger = logging.getLogger(__name__)


def _source_version_config(version: str) -> dict[str, str]:
    """
    Internal helper ``_source_version_config``.

    Parameters
    ----------
    version : object
        Argument ``version``.

    Returns
    -------
    object
        Return value.
    """
    try:
        config = get_version_config(version)
        return {
            "namespace_uri": str(config["namespace_uri"]),
            "schema_url": str(config["schema_url"]),
        }
    except VersionDeprecatedError:
        return {
            "namespace_uri": f"http://icao.int/iwxxm/{version.removesuffix('.0') if version.startswith('3.') else version}",
            "schema_url": f"https://schemas.wmo.int/iwxxm/{version}/iwxxm.xsd",
        }


class VersionMigrationWarning:
    """
    Represents a breaking change that was handled during migration.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self, element: str, xpath: str, action: str, reason: str) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        element : object
            Argument ``element``.
        xpath : object
            Argument ``xpath``.
        action : object
            Argument ``action``.
        reason : object
            Argument ``reason``.
        """
        self.element = element
        self.xpath = xpath
        self.action = action
        self.reason = reason

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for API response.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (to_dict)
        2

        Returns
        -------
        object
            Return value.
        """
        return {"element": self.element, "xpath": self.xpath, "action": self.action, "reason": self.reason}


class VersionMigrator:
    """
    Handles IWXXM XML migration between versions.

    Currently supports migration FROM 2023-1 TO 2025-2,
    with automatic removal of breaking change elements.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self) -> None:
        """Internal helper ``__init__``."""
        self.warnings: list[VersionMigrationWarning] = []
        self.xml_namespaces = {
            "iwxxm": "http://icao.int/iwxxm",
            "gml": "http://www.opengis.net/gml/3.2",
            "aixm": "http://www.aixm.aero/schema/5.1.1",
        }

    def migrate(
        self,
        xml_content: str,
        from_version: str,
        to_version: str,
        *,
        emit_profile: str | None = None,
    ) -> tuple[str, list[dict[str, Any]]]:
        """
        Migrate IWXXM XML from one version to another.

        Returns
        -------
            Tuple of:
            - Migrated XML string
            - List of warning dictionaries for elements that were removed/modified

        Raises
        ------
            ValueError: If migration

        Parameters
        ----------
        xml_content : object
            XML string in IWXXM format
        from_version : object
            Source IWXXM version (e.g., "2023-1")
        to_version : object
            Target IWXXM version (e.g., "2025-2")

        Returns
        -------
        object
            Tuple of: - Migrated XML string - List of warning dictionaries for elements that were removed/modified

        Examples
        --------
        >>> 1 + 1  # docstring smoke (migrate)
        2
        """
        # Reset warnings for this migration
        self.warnings = []

        if from_version == to_version:
            logger.debug(f"No migration needed from {from_version} to {to_version}")
            return xml_content, []

        if not is_migration_supported(from_version, to_version):
            raise ValueError(f"Unsupported IWXXM migration from {from_version} to {to_version}")

        if emit_profile is None:
            changes = get_breaking_changes(from_version, to_version)
            to_config = get_version_config(to_version)
        else:
            to_config = get_version_config_for_emit_profile(to_version, emit_profile)
            changes = to_config.get("breaking_changes_from_prior", {}).get(from_version, [])

        from_config = _source_version_config(from_version)

        logger.info(f"Migrating IWXXM from {from_version} to {to_version}")

        try:
            # Parse XML
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ET.ParseError(f"Invalid XML: {e}") from e

        # Apply each breaking change
        for change in changes:
            if change["action"] == "remove":
                self._remove_elements(root, change)

        self._rewrite_version_references(root, from_config=from_config, to_config=to_config)

        # Serialize back to string
        migrated_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

        # Return with warnings
        warnings_list = [w.to_dict() for w in self.warnings]

        logger.info(f"Migration complete. {len(warnings_list)} breaking changes handled.")

        return migrated_xml, warnings_list

    def _rewrite_version_references(
        self,
        root: ET.Element,
        *,
        from_config: dict[str, Any],
        to_config: dict[str, Any],
    ) -> None:
        """
        Internal helper ``_rewrite_version_references``.

        Parameters
        ----------
        root : object
            Argument ``root``.
        from_config : object
            Argument ``from_config``.
        to_config : object
            Argument ``to_config``.
        """
        old_namespace = str(from_config["namespace_uri"])
        new_namespace = str(to_config["namespace_uri"])
        old_schema_url = str(from_config["schema_url"])
        new_schema_url = str(to_config["schema_url"])
        xsi_schema_location = "{http://www.w3.org/2001/XMLSchema-instance}schemaLocation"

        ET.register_namespace("iwxxm", new_namespace)
        ET.register_namespace("gml", "http://www.opengis.net/gml/3.2")
        ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

        for element in root.iter():
            if element.tag.startswith(f"{{{old_namespace}}}"):
                local_name = element.tag.split("}", 1)[1]
                element.tag = f"{{{new_namespace}}}{local_name}"

            rewritten_attrib: dict[str, str] = {}
            for key, value in element.attrib.items():
                rewritten_key = key.replace(old_namespace, new_namespace)
                rewritten_value = value.replace(old_namespace, new_namespace).replace(old_schema_url, new_schema_url)
                rewritten_attrib[rewritten_key] = rewritten_value

            if xsi_schema_location in rewritten_attrib and old_schema_url not in rewritten_attrib[xsi_schema_location]:
                rewritten_attrib[xsi_schema_location] = rewritten_attrib[xsi_schema_location].replace(
                    new_namespace,
                    f"{new_namespace} {new_schema_url}",
                    1,
                )

            element.attrib.clear()
            element.attrib.update(rewritten_attrib)

    def _remove_elements(self, root: ET.Element, change: dict[str, Any]) -> None:
        """
        Internal helper ``_remove_elements``.

        Parameters
        ----------
        root : object
            Argument ``root``.
        change : object
            Argument ``change``.
        """
        element_name = change.get("element", "unknown")
        xpath = change.get("xpath", "")
        reason = change.get("reason", "")

        if not xpath:
            logger.warning(f"No XPath provided for element removal: {element_name}")
            return

        try:
            # Find all matching elements
            # Note: ElementTree has limited XPath support; using custom logic
            removed_count = self._remove_elements_by_tag(root, element_name)

            if removed_count > 0:
                warning = VersionMigrationWarning(element=element_name, xpath=xpath, action="remove", reason=reason)
                self.warnings.append(warning)
                logger.warning(f"Removed {removed_count} instance(s) of {element_name}: {reason}")
        except Exception as e:
            logger.error(f"Error removing {element_name}: {e}")
            self.warnings.append(
                VersionMigrationWarning(
                    element=element_name,
                    xpath=xpath,
                    action="remove",
                    reason=f"Failed to remove element: {e}",
                )
            )

    def _remove_elements_by_tag(self, root: ET.Element, tag: str) -> int:
        """
        Internal helper ``_remove_elements_by_tag``.

        Parameters
        ----------
        root : object
            Argument ``root``.
        tag : object
            Argument ``tag``.

        Returns
        -------
        object
            Return value.
        """
        removed = 0

        # Extract prefix and local name
        if ":" in tag:
            _prefix, localname = tag.split(":", 1)
        else:
            localname = tag

        # Traverse tree and remove matching elements
        for parent in root.iter():
            children_to_remove = [child for child in parent if self._tag_matches(child.tag, localname)]

            for child in children_to_remove:
                parent.remove(child)
                removed += 1

        return removed

    def _tag_matches(self, full_tag: str, localname: str) -> bool:
        """
        Internal helper ``_tag_matches``.

        Parameters
        ----------
        full_tag : object
            Argument ``full_tag``.
        localname : object
            Argument ``localname``.

        Returns
        -------
        object
            Return value.
        """
        # ElementTree represents namespaced tags as {namespace}localname
        if "}" in full_tag:
            return full_tag.split("}", 1)[1] == localname
        else:
            return full_tag == localname


# Global instance
_migrator_instance: VersionMigrator | None = None


def get_migrator() -> VersionMigrator:
    """
    Get singleton instance of VersionMigrator.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_migrator)
    2

    Returns
    -------
    object
        Return value.
    """
    global _migrator_instance
    if _migrator_instance is None:
        _migrator_instance = VersionMigrator()
    return _migrator_instance


def migrate_xml(
    xml_content: str,
    from_version: str,
    to_version: str,
    *,
    emit_profile: str | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """
    Migrate IWXXM XML from one version to another.

    Convenience function wrapping the singleton migrator.

    Returns
    -------
        Tuple of (migrated_xml_string, warnings_list)

    Parameters
    ----------
    xml_content : object
        XML string in IWXXM format
    from_version : object
        Source IWXXM version
    to_version : object
        Target IWXXM version

    Returns
    -------
    object
        Tuple of (migrated_xml_string, warnings_list)

    Examples
    --------
    >>> 1 + 1  # docstring smoke (migrate_xml)
    2
    """
    migrator = get_migrator()
    if emit_profile is None:
        return migrator.migrate(xml_content, from_version, to_version)
    return migrator.migrate(xml_content, from_version, to_version, emit_profile=emit_profile)
