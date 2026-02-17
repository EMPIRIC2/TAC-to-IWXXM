"""
Version Migration Utilities

Handles breaking changes when converting between IWXXM versions,
especially for data transformation from older versions to newer ones.
"""

import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional
from copy import deepcopy

from src.config.iwxxm_versions import get_breaking_changes

logger = logging.getLogger(__name__)


class VersionMigrationWarning:
    """Represents a breaking change that was handled during migration."""
    
    def __init__(self, element: str, xpath: str, action: str, reason: str):
        self.element = element
        self.xpath = xpath
        self.action = action
        self.reason = reason
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response."""
        return {
            "element": self.element,
            "xpath": self.xpath,
            "action": self.action,
            "reason": self.reason
        }


class VersionMigrator:
    """
    Handles IWXXM XML migration between versions.
    
    Currently supports migration FROM 2023-1 TO 2025-2,
    with automatic removal of breaking change elements.
    """
    
    def __init__(self):
        self.warnings: List[VersionMigrationWarning] = []
        self.xml_namespaces = {
            'iwxxm': 'http://icao.int/iwxxm',
            'gml': 'http://www.opengis.net/gml/3.2',
            'aixm': 'http://www.aixm.aero/schema/5.1.1'
        }
    
    def migrate(
        self,
        xml_content: str,
        from_version: str,
        to_version: str
    ) -> Tuple[str, List[Dict]]:
        """
        Migrate IWXXM XML from one version to another.
        
        Args:
            xml_content: XML string in IWXXM format
            from_version: Source IWXXM version (e.g., "2023-1")
            to_version: Target IWXXM version (e.g., "2025-2")
            
        Returns:
            Tuple of:
            - Migrated XML string
            - List of warning dictionaries for elements that were removed/modified
            
        Raises:
            ValueError: If migration not supported for version pair
            ET.ParseError: If XML is malformed
        """
        # Reset warnings for this migration
        self.warnings = []
        
        # Get breaking changes
        changes = get_breaking_changes(from_version, to_version)
        
        if not changes:
            logger.debug(f"No breaking changes from {from_version} to {to_version}")
            return xml_content, []
        
        logger.info(f"Migrating IWXXM from {from_version} to {to_version}")
        
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise ET.ParseError(f"Invalid XML: {e}")
        
        # Apply each breaking change
        for change in changes:
            if change["action"] == "remove":
                self._remove_elements(root, change)
        
        # Serialize back to string
        migrated_xml = ET.tostring(root, encoding="unicode")
        
        # Return with warnings
        warnings_list = [w.to_dict() for w in self.warnings]
        
        logger.info(
            f"Migration complete. {len(warnings_list)} breaking changes handled."
        )
        
        return migrated_xml, warnings_list
    
    def _remove_elements(self, root: ET.Element, change: Dict) -> None:
        """
        Remove elements matching the specified XPath and register warning.
        
        Args:
            root: XML root element
            change: Breaking change definition with element, xpath, action, reason
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
                warning = VersionMigrationWarning(
                    element=element_name,
                    xpath=xpath,
                    action="remove",
                    reason=reason
                )
                self.warnings.append(warning)
                logger.warning(
                    f"Removed {removed_count} instance(s) of {element_name}: {reason}"
                )
        except Exception as e:
            logger.error(f"Error removing {element_name}: {e}")
    
    def _remove_elements_by_tag(self, root: ET.Element, tag: str) -> int:
        """
        Recursively find and remove all elements with specified tag.
        
        Handles both prefixed (iwxxm:runwayState) and unprefixed tags.
        
        Args:
            root: Root element to search from
            tag: Tag name to match (can include prefix like 'iwxxm:runwayState')
            
        Returns:
            Number of elements removed
        """
        removed = 0
        
        # Extract prefix and local name
        if ':' in tag:
            prefix, localname = tag.split(':', 1)
        else:
            localname = tag
        
        # Traverse tree and remove matching elements
        for parent in root.iter():
            children_to_remove = []
            for child in parent:
                # Check both prefixed and unprefixed names
                if self._tag_matches(child.tag, localname):
                    children_to_remove.append(child)
            
            for child in children_to_remove:
                parent.remove(child)
                removed += 1
        
        return removed
    
    def _tag_matches(self, full_tag: str, localname: str) -> bool:
        """
        Check if a full tag (with namespace) matches the local name.
        
        Args:
            full_tag: Full tag from ElementTree (e.g., '{http://icao.int/iwxxm/2023-1}runwayState')
            localname: Local name to match (e.g., 'runwayState')
            
        Returns:
            True if tag matches
        """
        # ElementTree represents namespaced tags as {namespace}localname
        if '}' in full_tag:
            return full_tag.split('}', 1)[1] == localname
        else:
            return full_tag == localname


# Global instance
_migrator_instance: Optional[VersionMigrator] = None


def get_migrator() -> VersionMigrator:
    """Get singleton instance of VersionMigrator."""
    global _migrator_instance
    if _migrator_instance is None:
        _migrator_instance = VersionMigrator()
    return _migrator_instance


def migrate_xml(
    xml_content: str,
    from_version: str,
    to_version: str
) -> Tuple[str, List[Dict]]:
    """
    Migrate IWXXM XML from one version to another.
    
    Convenience function wrapping the singleton migrator.
    
    Args:
        xml_content: XML string in IWXXM format
        from_version: Source IWXXM version
        to_version: Target IWXXM version
        
    Returns:
        Tuple of (migrated_xml_string, warnings_list)
    """
    migrator = get_migrator()
    return migrator.migrate(xml_content, from_version, to_version)
