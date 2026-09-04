"""Unit tests for IWXXM version configuration helpers."""

from pathlib import Path

import pytest
from src.config import iwxxm_versions as versions


class TestProjectRootDetection:
    """Test environment-driven project root detection behavior."""

    def test_detect_project_root_from_env_project_root(self, monkeypatch, tmp_path):
        """Environment project root should win when it has versioned schemas."""
        root = tmp_path / "repo"
        (root / "schemas" / "iwxxm" / "2025-2" / "IWXXM").mkdir(parents=True)

        monkeypatch.setenv("IWXXM_PROJECT_ROOT", str(root))
        detected = versions._detect_project_root()

        assert detected == root.resolve()

    def test_detect_project_root_from_env_schemas_root(self, monkeypatch, tmp_path):
        """Environment schemas root should resolve to project root."""
        root = tmp_path / "repo"
        schemas_root = root / "schemas" / "iwxxm"
        (schemas_root / "2025-2" / "IWXXM").mkdir(parents=True)

        monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
        monkeypatch.setenv("IWXXM_SCHEMAS_ROOT", str(schemas_root))

        detected = versions._detect_project_root()

        assert detected == root.resolve()

    def test_detect_project_root_project_root_env_without_versioned_schemas_falls_through(self, monkeypatch, tmp_path):
        """If IWXXM_PROJECT_ROOT exists but lacks versioned schemas, detection continues."""
        bad_root = tmp_path / "bad-root"
        bad_root.mkdir(parents=True)
        fake_file = tmp_path / "x" / "y" / "z" / "iwxxm_versions.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("# fake", encoding="utf-8")

        monkeypatch.setattr(versions, "__file__", str(fake_file))
        monkeypatch.setenv("IWXXM_PROJECT_ROOT", str(bad_root))
        monkeypatch.setenv("IWXXM_SCHEMAS_ROOT", str(tmp_path / "missing-schemas"))

        detected = versions._detect_project_root()

        assert isinstance(detected, Path)

    def test_detect_project_root_schemas_env_existing_but_no_usable_layout(self, monkeypatch, tmp_path):
        """Existing IWXXM_SCHEMAS_ROOT should still fall through when layout checks fail."""
        root = tmp_path / "repo"
        schemas_root = root / "schemas" / "iwxxm"
        schemas_root.mkdir(parents=True)
        fake_file = tmp_path / "m" / "n" / "o" / "iwxxm_versions.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("# fake", encoding="utf-8")

        monkeypatch.setattr(versions, "__file__", str(fake_file))
        monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
        monkeypatch.setenv("IWXXM_SCHEMAS_ROOT", str(schemas_root))

        detected = versions._detect_project_root()

        assert isinstance(detected, Path)

    def test_detect_project_root_schemas_env_with_child_iwxxm_layout(self, monkeypatch, tmp_path):
        """When IWXXM_SCHEMAS_ROOT contains an iwxxm child, that branch should resolve root."""
        root = tmp_path / "root"
        schemas_candidate = root / "schemas"
        (schemas_candidate / "iwxxm" / "2025-2" / "IWXXM").mkdir(parents=True)

        monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
        monkeypatch.setenv("IWXXM_SCHEMAS_ROOT", str(schemas_candidate))

        detected = versions._detect_project_root()

        assert detected == root.resolve()

    def test_detect_project_root_fallback_any_schemas_iwxxm(self, monkeypatch, tmp_path):
        """Without env vars, fallback loop should return parent containing schemas/iwxxm."""
        fake_file = tmp_path / "a" / "b" / "c" / "iwxxm_versions.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("# fake", encoding="utf-8")
        (tmp_path / "a" / "schemas" / "iwxxm").mkdir(parents=True)

        monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
        monkeypatch.delenv("IWXXM_SCHEMAS_ROOT", raising=False)
        monkeypatch.setattr(versions, "__file__", str(fake_file))

        detected = versions._detect_project_root()

        assert detected == (tmp_path / "a").resolve()

    def test_detect_project_root_ultimate_fallback_parent_chain(self, monkeypatch, tmp_path):
        """When no schema layout exists, detector returns four-level parent fallback."""
        fake_file = tmp_path / "p" / "q" / "r" / "s" / "iwxxm_versions.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("# fake", encoding="utf-8")

        monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
        monkeypatch.delenv("IWXXM_SCHEMAS_ROOT", raising=False)
        monkeypatch.setattr(versions, "__file__", str(fake_file))

        detected = versions._detect_project_root()

        assert detected == fake_file.parent.parent.parent.parent

    def test_detect_project_root_prefers_vendor_iwxxm_subdirectory(self, monkeypatch, tmp_path):
        fake_file = tmp_path / "apps" / "backend" / "src" / "config" / "iwxxm_versions.py"
        fake_file.parent.mkdir(parents=True)
        fake_file.write_text("# fake", encoding="utf-8")
        vendor_iwxxm = tmp_path / "vendor" / "schemas" / "iwxxm"
        vendor_iwxxm.mkdir(parents=True)

        monkeypatch.delenv("IWXXM_PROJECT_ROOT", raising=False)
        monkeypatch.delenv("IWXXM_SCHEMAS_ROOT", raising=False)
        monkeypatch.setattr(versions, "__file__", str(fake_file))

        detected = versions._detect_project_root()

        assert detected == tmp_path.resolve()


class TestVersionHelpers:
    """Test pure helper functions and version classification."""

    def test_get_versions_by_channel(self):
        """Known channels should return version lists."""
        assert "2025-2" in versions.get_versions_by_channel("stable")
        assert isinstance(versions.get_versions_by_channel("rc"), list)
        assert isinstance(versions.get_versions_by_channel("all"), list)

    def test_get_versions_by_channel_unknown(self):
        """Unknown channels should return an empty list."""
        assert versions.get_versions_by_channel("does-not-exist") == []

    def test_rc_and_channel_helpers(self):
        """RC and channel helper behavior should be consistent."""
        assert versions.is_rc_version("2025-2RC1")
        assert not versions.is_rc_version("2025-2")
        assert versions.get_version_channel("2025-2") == "stable"
        assert versions.get_version_channel("2025-2RC1") == "rc"
        assert versions.get_version_channel("unknown") == "unknown"

    def test_get_discovery_date_for_known_and_unknown_versions(self):
        """Discovery metadata helper should return expected values."""
        assert versions.get_version_discovery_date("2025-2")
        assert versions.get_version_discovery_date("does-not-exist") == ""

    def test_namespace_schema_support_and_breaking_change_helpers(self):
        assert versions.get_namespace_uri("2025-2")
        assert versions.get_schema_url("2025-2")
        assert versions.is_version_supported("2025-2") is True
        assert versions.is_version_supported("definitely-not-supported") is False
        assert isinstance(versions.get_breaking_changes("2023-1", "2025-2"), list)


class TestGetVersionConfig:
    def test_deprecated_version_raises(self):
        with pytest.raises(versions.VersionDeprecatedError):
            versions.get_version_config("2021-2")

    def test_unsupported_version_raises(self):
        with pytest.raises(ValueError, match=r".*"):
            versions.get_version_config("2099-9")

    def test_valid_version_returns_config(self):
        cfg = versions.get_version_config("2025-2")
        assert cfg["name"].startswith("IWXXM")
        assert "namespace_uri" in cfg

    def test_normalized_deprecated_version_raises(self, monkeypatch):
        monkeypatch.setattr(versions, "VERSION_REMAPPING", {"legacy_alias": "2021-2"})

        with pytest.raises(versions.VersionDeprecatedError):
            versions.get_version_config("legacy_alias")


class TestNormalizeVersion:
    def test_empty_and_whitespace_default_to_latest(self):
        assert versions.normalize_version("") == versions.DEFAULT_VERSION
        assert versions.normalize_version("   ") == versions.DEFAULT_VERSION

    def test_remapped_version_returns_stable_target(self):
        assert versions.normalize_version("2025-1") == "2025-2"


class TestSchemaResolution:
    """Test schema path resolution and fallback behavior."""

    def test_resolve_schema_file_invalid_file_type(self):
        """Unknown file types should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown file type"):
            versions.resolve_schema_file("2025-2", "invalid-type")

    def test_resolve_schema_file_uses_fallback(self, monkeypatch, tmp_path):
        """Missing versioned schema should use fallback IWXXM directory."""
        fallback_base = tmp_path / "schemas" / "iwxxm" / "IWXXM"
        fallback_base.mkdir(parents=True)
        fallback_xsd = fallback_base / "iwxxm.xsd"
        fallback_xsd.write_text("<xsd:schema/>", encoding="utf-8")

        fake_config = {
            "local_schema_base": tmp_path / "missing" / "2025-2" / "IWXXM",
            "schema_file": "iwxxm.xsd",
            "schematron_file": "rule/iwxxm.sch",
            "codelists_dir": "rule",
        }

        monkeypatch.setattr(versions, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(versions, "get_version_config", lambda _version: fake_config)

        resolved = versions.resolve_schema_file("2025-2", "xsd")

        assert resolved == fallback_xsd

    def test_resolve_schema_file_uses_schematron_and_codelists(self, monkeypatch, tmp_path):
        schematron_path = tmp_path / "schemas" / "iwxxm" / "IWXXM" / "rule" / "iwxxm.sch"
        codelists_path = tmp_path / "schemas" / "iwxxm" / "IWXXM" / "rule"
        schematron_path.parent.mkdir(parents=True)
        schematron_path.write_text("<schema/>", encoding="utf-8")

        fake_config = {
            "local_schema_base": tmp_path / "missing" / "2025-2" / "IWXXM",
            "schema_file": "iwxxm.xsd",
            "schematron_file": "rule/iwxxm.sch",
            "codelists_dir": "rule",
        }

        monkeypatch.setattr(versions, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(versions, "get_version_config", lambda _version: fake_config)

        assert versions.resolve_schema_file("2025-2", "schematron") == schematron_path
        assert versions.resolve_schema_file("2025-2", "codelists") == codelists_path

    def test_resolve_schema_file_missing_everywhere_raises(self, monkeypatch, tmp_path):
        fake_config = {
            "local_schema_base": tmp_path / "missing" / "2025-2" / "IWXXM",
            "schema_file": "iwxxm.xsd",
            "schematron_file": "rule/iwxxm.sch",
            "codelists_dir": "rule",
        }

        monkeypatch.setattr(versions, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(versions, "get_version_config", lambda _version: fake_config)

        with pytest.raises(FileNotFoundError, match=r".*"):
            versions.resolve_schema_file("2025-2", "xsd")


class TestRegistrationAndMetadata:
    """Test dynamic RC registration and metadata assembly."""

    def test_register_rc_version_updates_channels(self):
        """RC registration should update all channel lists and registries."""
        version_name = "2099-1RC1"
        config = {
            "name": "IWXXM 2099-1 RC1",
            "namespace_uri": "http://icao.int/iwxxm/2099-1",
            "schema_url": "https://schemas.wmo.int/iwxxm/2099-1RC1/iwxxm.xsd",
            "local_schema_base": Path("/tmp/none"),
            "schema_file": "iwxxm.xsd",
            "schematron_file": "rule/iwxxm.sch",
            "codelists_dir": "rule",
            "status": "rc",
            "breaking_changes_from_prior": {},
        }

        # Make sure test can be run repeatedly.
        versions.RC_VERSIONS.pop(version_name, None)
        versions.ALL_VERSIONS.pop(version_name, None)
        if version_name in versions.SUPPORTED_VERSIONS_BY_CHANNEL.get("rc", []):
            versions.SUPPORTED_VERSIONS_BY_CHANNEL["rc"].remove(version_name)
        if version_name in versions.SUPPORTED_VERSIONS_BY_CHANNEL.get("all", []):
            versions.SUPPORTED_VERSIONS_BY_CHANNEL["all"].remove(version_name)

        versions.register_rc_version(version_name, config)

        assert version_name in versions.RC_VERSIONS
        assert version_name in versions.ALL_VERSIONS
        assert version_name in versions.get_versions_by_channel("rc")
        assert version_name in versions.get_supported_versions()

    def test_get_all_versions_with_metadata_contains_discovery(self):
        """Combined metadata output should include discovery metadata key."""
        combined = versions.get_all_versions_with_metadata()

        assert "2025-2" in combined
        assert "discovery_metadata" in combined["2025-2"]
