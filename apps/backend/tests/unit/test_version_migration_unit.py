"""Unit tests for VersionMigrator - 0% coverage target."""

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
        with (
            patch(
                "src.utilities.version_migration.get_breaking_changes",
                return_value=[{"action": "remove", "element": "foo", "xpath": "//foo", "reason": "gone"}],
            ),
            pytest.raises(ET.ParseError),
        ):
            m.migrate(INVALID_XML, "2023-1", "2025-2")

    def test_remove_action_removes_element(self):
        xml = """<?xml version="1.0"?>
<root xmlns:iwxxm="http://icao.int/iwxxm">
  <iwxxm:OldElement>old data</iwxxm:OldElement>
  <iwxxm:KeeperElement>keep this</iwxxm:KeeperElement>
</root>"""
        breaking = [
            {
                "action": "remove",
                "element": "OldElement",
                "xpath": ".//{http://icao.int/iwxxm}OldElement",
                "reason": "Deprecated in 2025-2",
            }
        ]
        m = VersionMigrator()
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=breaking):
            result_xml, _warnings = m.migrate(xml, "2023-1", "2025-2")
        # OldElement should be removed
        assert "OldElement" not in result_xml

    def test_warnings_accumulated(self):
        xml = """<root xmlns:iwxxm="http://icao.int/iwxxm">
  <iwxxm:Gone>x</iwxxm:Gone>
</root>"""
        breaking = [
            {
                "action": "remove",
                "element": "Gone",
                "xpath": ".//{http://icao.int/iwxxm}Gone",
                "reason": "Gone in 2025-2",
            }
        ]
        m = VersionMigrator()
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=breaking):
            result_xml, warnings = m.migrate(xml, "2023-1", "2025-2")
        assert "Gone" not in result_xml
        assert len(warnings) == 1
        assert warnings[0] == {
            "element": "Gone",
            "xpath": ".//{http://icao.int/iwxxm}Gone",
            "action": "remove",
            "reason": "Gone in 2025-2",
        }

    def test_warnings_reset_on_each_call(self):
        m = VersionMigrator()
        m.warnings = [VersionMigrationWarning("old", "old/xpath", "remove", "old reason")]
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=[]):
            m.migrate(SIMPLE_XML, "2023-1", "2025-2")
        assert m.warnings == []

    def test_unsupported_action_is_skipped(self):
        """Unknown actions should be silently ignored."""
        breaking = [
            {
                "action": "transform",  # not implemented
                "element": "Elem",
                "xpath": "//Elem",
                "reason": "change",
            }
        ]
        m = VersionMigrator()
        with patch("src.utilities.version_migration.get_breaking_changes", return_value=breaking):
            result_xml, _warnings = m.migrate(SIMPLE_XML, "2023-1", "2025-2")
        # Should not raise; unsupported action is skipped
        assert isinstance(result_xml, str)


class TestVersionMigratorRemoveElements:
    def test_remove_elements_skips_empty_xpath(self):
        m = VersionMigrator()
        root = ET.fromstring(SIMPLE_XML)
        m._remove_elements(root, {"element": "child", "xpath": "", "reason": "gone"})
        assert m.warnings == []

    def test_remove_elements_handles_internal_exception(self):
        m = VersionMigrator()
        root = ET.fromstring(SIMPLE_XML)
        with patch.object(m, "_remove_elements_by_tag", side_effect=RuntimeError("remove boom")):
            m._remove_elements(
                root,
                {"element": "child", "xpath": "//child", "action": "remove", "reason": "gone"},
            )
        assert len(m.warnings) == 1
        assert m.warnings[0].to_dict() == {
            "element": "child",
            "xpath": "//child",
            "action": "remove",
            "reason": "Failed to remove element: remove boom",
        }

    def test_remove_elements_by_tag_with_prefix(self):
        xml = """<root xmlns:iwxxm="http://icao.int/iwxxm">
  <iwxxm:runwayState>state</iwxxm:runwayState>
</root>"""
        m = VersionMigrator()
        root = ET.fromstring(xml)
        removed = m._remove_elements_by_tag(root, "iwxxm:runwayState")
        assert removed == 1
        assert "runwayState" not in ET.tostring(root, encoding="unicode")

    def test_tag_matches_unprefixed_tag(self):
        m = VersionMigrator()
        assert m._tag_matches("runwayState", "runwayState") is True
        assert m._tag_matches("other", "runwayState") is False

    def test_remove_elements_by_tag_without_prefix(self):
        xml = """<root xmlns:iwxxm="http://icao.int/iwxxm">
  <runwayState>state</runwayState>
</root>"""
        m = VersionMigrator()
        root = ET.fromstring(xml)
        removed = m._remove_elements_by_tag(root, "runwayState")
        assert removed == 1
        assert not any("runwayState" in el.tag for el in root.iter())


class TestVersionMigrationHelpers:
    def test_get_migrator_singleton(self):
        import src.utilities.version_migration as vm

        original = vm._migrator_instance
        try:
            vm._migrator_instance = None
            first = vm.get_migrator()
            second = vm.get_migrator()
            assert first is second
        finally:
            vm._migrator_instance = original

    def test_migrate_xml_convenience(self):
        import src.utilities.version_migration as vm

        migrator = vm.get_migrator()
        with patch.object(migrator, "migrate", return_value=("<xml/>", [{"element": "x"}])) as migrate_mock:
            result_xml, warnings = vm.migrate_xml(SIMPLE_XML, "2023-1", "2025-2")
        migrate_mock.assert_called_once_with(SIMPLE_XML, "2023-1", "2025-2")
        assert result_xml == "<xml/>"
        assert warnings == [{"element": "x"}]
