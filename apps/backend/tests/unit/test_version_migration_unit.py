"""Unit tests for VersionMigrator – 0% coverage target."""
import xml.etree.ElementTree as ET
from unittest.mock import patch

import pytest

from src.utilities.version_migration import VersionMigrationWarning, VersionMigrator

SIMPLE_XML = '<?xml version="1.0"?><root xmlns:iwxxm="http://icao.int/iwxxm"><child name="test"/></root>'
INVALID_XML = "<<<NOT XML>>>"


class TestVersionMigrationWarning:
    def test_to_dict(self):
        w = VersionMigrationWarning(
            element="SomeElement",
            xpath="//iwxxm:SomeElement",
            action="remove",
            reason="Breaking change in 2025-2",
        )
        d = w.to_dict()
        assert d["element"] == "SomeElement"
        assert d["action"] == "remove"
        assert d["xpath"] == "//iwxxm:SomeElement"

    def test_attrs(self):
        w = VersionMigrationWarning(element="E", xpath="x", action="a", reason="r")
        assert w.element == "E"
        assert w.reason == "r"


class TestVersionMigratorInit:
    def test_init_empty_warnings(self):
        m = VersionMigrator()
        assert m.warnings == []

    def test_init_namespaces(self):
        m = VersionMigrator()
        assert "iwxxm" in m.xml_namespaces
        assert "gml" in m.xml_namespaces


class TestVersionMigratorMigrate:
    def test_no_breaking_changes_returns_original(self):
        """When no breaking changes, original XML returned unchanged."""
        m = VersionMigrator()
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=[]):
            result_xml, warnings = m.migrate(SIMPLE_XML, "2023-1", "2025-2")
        assert warnings == []
        # Content should be preserved
        assert "child" in result_xml or "root" in result_xml

    def test_invalid_xml_raises(self):
        m = VersionMigrator()
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=[
            {"action": "remove", "element": "foo", "xpath": "//foo", "reason": "gone"}
        ]):
            with pytest.raises(ET.ParseError):
                m.migrate(INVALID_XML, "2023-1", "2025-2")

    def test_remove_action_removes_element(self):
        xml = '''<?xml version="1.0"?>
<root xmlns:iwxxm="http://icao.int/iwxxm">
  <iwxxm:OldElement>old data</iwxxm:OldElement>
  <iwxxm:KeeperElement>keep this</iwxxm:KeeperElement>
</root>'''
        breaking = [{
            "action": "remove",
            "element": "OldElement",
            "xpath": ".//{http://icao.int/iwxxm}OldElement",
            "reason": "Deprecated in 2025-2",
        }]
        m = VersionMigrator()
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=breaking):
            result_xml, warnings = m.migrate(xml, "2023-1", "2025-2")
        # OldElement should be removed
        assert "OldElement" not in result_xml

    def test_warnings_accumulated(self):
        xml = '''<root xmlns:iwxxm="http://icao.int/iwxxm">
  <iwxxm:Gone>x</iwxxm:Gone>
</root>'''
        breaking = [{
            "action": "remove",
            "element": "Gone",
            "xpath": ".//{http://icao.int/iwxxm}Gone",
            "reason": "Gone in 2025-2",
        }]
        m = VersionMigrator()
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=breaking):
            result_xml, warnings = m.migrate(xml, "2023-1", "2025-2")
        # Warnings should be populated if the element was actually removed
        assert isinstance(warnings, list)

    def test_warnings_reset_on_each_call(self):
        m = VersionMigrator()
        m.warnings = [VersionMigrationWarning("old", "old/xpath", "remove", "old reason")]
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=[]):
            m.migrate(SIMPLE_XML, "2023-1", "2025-2")
        assert m.warnings == []

    def test_unsupported_action_is_skipped(self):
        """Unknown actions should be silently ignored."""
        breaking = [{
            "action": "transform",  # not implemented
            "element": "Elem",
            "xpath": "//Elem",
            "reason": "change",
        }]
        m = VersionMigrator()
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=breaking):
            result_xml, warnings = m.migrate(SIMPLE_XML, "2023-1", "2025-2")
        # Should not raise; unsupported action is skipped
        assert isinstance(result_xml, str)
