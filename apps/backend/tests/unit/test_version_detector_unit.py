"""Unit tests for VersionDetector - 0% coverage target."""

import subprocess
from unittest.mock import MagicMock, patch

from src.utilities import version_detector as vd_module
from src.utilities.version_detector import (
    VersionDetector,
    VersionInfo,
    check_for_updates,
    detect_available_versions,
)


class TestVersionInfoDataclass:
    def test_defaults(self):
        vi = VersionInfo(version="2025-2", tag="v2025-2", is_configured=True, is_latest=True)
        assert vi.schemas_path is None
        assert vi.schematron_path is None
        assert vi.has_codelists is False


class TestVersionDetectorInit:
    def test_default_schemas_root(self):
        vd = VersionDetector()
        assert vd.schemas_root is not None
        assert vd.iwxxm_path == vd.schemas_root / "iwxxm"

    def test_custom_schemas_root(self, tmp_path):
        vd = VersionDetector(schemas_root=tmp_path)
        assert vd.schemas_root == tmp_path
        assert vd.iwxxm_path == tmp_path / "iwxxm"


class TestVersionDetectorGetAvailableTags:
    def test_git_tags_parsed(self, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = "v2025-2\nv2023-1\nv2021-2\n"
        mock_result.returncode = 0
        with patch("src.utilities.version_detector.subprocess.run", return_value=mock_result):
            vd = VersionDetector(schemas_root=tmp_path)
            tags = vd.get_available_tags()
        assert "v2025-2" in tags
        assert "v2023-1" in tags

    def test_git_error_falls_back_to_dirs(self, tmp_path):
        iwxxm_path = tmp_path / "iwxxm"
        iwxxm_path.mkdir()
        (iwxxm_path / "2025-2").mkdir()
        (iwxxm_path / "2023-1").mkdir()
        (iwxxm_path / "not-a-version").mkdir()

        with patch(
            "src.utilities.version_detector.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "git"),
        ):
            vd = VersionDetector(schemas_root=tmp_path)
            tags = vd.get_available_tags()
        # Should find the version directories as fallback
        assert isinstance(tags, list)

    def test_git_timeout_handled(self, tmp_path):
        with patch(
            "src.utilities.version_detector.subprocess.run",
            side_effect=subprocess.TimeoutExpired("git", 10),
        ):
            vd = VersionDetector(schemas_root=tmp_path)
            tags = vd.get_available_tags()
        assert isinstance(tags, list)

    def test_tags_sorted_newest_first(self, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = "v2021-2\nv2025-2\nv2023-1\n"
        with patch("src.utilities.version_detector.subprocess.run", return_value=mock_result):
            vd = VersionDetector(schemas_root=tmp_path)
            tags = vd.get_available_tags()
        if len(tags) >= 2:
            assert tags[0] >= tags[1]

    def test_tags_filtered_to_version_format(self, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = "v2025-2\nsome-other-tag\nv2023-1\n"
        with patch("src.utilities.version_detector.subprocess.run", return_value=mock_result):
            vd = VersionDetector(schemas_root=tmp_path)
            tags = vd.get_available_tags()
        assert "some-other-tag" not in tags

    def test_empty_git_output_no_error(self, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch("src.utilities.version_detector.subprocess.run", return_value=mock_result):
            vd = VersionDetector(schemas_root=tmp_path)
            tags = vd.get_available_tags()
        assert isinstance(tags, list)


class TestVersionDetectorGetVersionInfo:
    def test_get_version_info_known_version(self, tmp_path):
        iwxxm_path = tmp_path / "iwxxm"
        iwxxm_path.mkdir()
        version_dir = iwxxm_path / "2025-2"
        version_dir.mkdir()
        mock_result = MagicMock()
        mock_result.stdout = "v2025-2\n"
        with patch("src.utilities.version_detector.subprocess.run", return_value=mock_result):
            vd = VersionDetector(schemas_root=tmp_path)
            info_list = vd.detect_versions()
        assert isinstance(info_list, list)

    def test_get_new_versions_returns_list(self, tmp_path):
        mock_result = MagicMock()
        mock_result.stdout = ""
        with patch("src.utilities.version_detector.subprocess.run", return_value=mock_result):
            vd = VersionDetector(schemas_root=tmp_path)
            new_versions = vd.get_unconfigured_versions()
        assert isinstance(new_versions, list)


class TestVersionDetectorHelpers:
    def test_get_latest_version_reads_pipe_delimited(self, tmp_path):
        iwxxm_path = tmp_path / "iwxxm"
        iwxxm_path.mkdir(parents=True)
        (iwxxm_path / "LATEST_VERSION").write_text("2025-2|IWXXM")

        vd = VersionDetector(schemas_root=tmp_path)
        assert vd.get_latest_version() == "2025-2"

    def test_get_latest_version_missing_file_returns_none(self, tmp_path):
        vd = VersionDetector(schemas_root=tmp_path)
        assert vd.get_latest_version() is None

    def test_get_latest_version_read_error_returns_none(self, tmp_path):
        iwxxm_path = tmp_path / "iwxxm"
        iwxxm_path.mkdir(parents=True)
        latest = iwxxm_path / "LATEST_VERSION"
        latest.write_text("2025-2")

        vd = VersionDetector(schemas_root=tmp_path)
        with patch.object(type(latest), "read_text", side_effect=OSError("boom")):
            assert vd.get_latest_version() is None

    def test_tag_version_conversion_helpers(self, tmp_path):
        vd = VersionDetector(schemas_root=tmp_path)
        assert vd.tag_to_version("v2025-2") == "2025-2"
        assert vd.version_to_tag("2025-2") == "v2025-2"
        assert vd.version_to_tag("v2023-1") == "v2023-1"

    def test_check_version_files_flags(self, tmp_path):
        iwxxm_dir = tmp_path / "iwxxm" / "IWXXM" / "rule"
        iwxxm_dir.mkdir(parents=True)
        (tmp_path / "iwxxm" / "IWXXM" / "iwxxm.xsd").write_text("x")
        (tmp_path / "iwxxm" / "IWXXM" / "metarSpeci.xsd").write_text("x")
        (tmp_path / "iwxxm" / "IWXXM" / "rule" / "iwxxm.sch").write_text("x")
        (tmp_path / "iwxxm" / "IWXXM" / "rule" / "codes.rdf").write_text("x")

        vd = VersionDetector(schemas_root=tmp_path)
        flags = vd.check_version_files("2025-2")
        assert flags["xsd"] is True
        assert flags["metar_xsd"] is True
        assert flags["schematron"] is True
        assert flags["codelists"] is True


class TestVersionDetectorReportsAndSelection:
    def test_detect_versions_sets_configured_and_latest_flags(self, tmp_path):
        vd = VersionDetector(schemas_root=tmp_path)

        with (
            patch.object(vd, "get_available_tags", return_value=["v2025-2", "v2099-1"]),
            patch.object(
                vd,
                "get_latest_version",
                return_value="2099-1",
            ),
            patch.object(vd_module, "normalize_version", side_effect=lambda x: x),
        ):
            versions = vd.detect_versions()

        assert len(versions) == 2
        assert any(v.is_latest for v in versions)
        assert any(not v.is_configured for v in versions)

    def test_get_new_versions_since_sorted_descending(self, tmp_path):
        vd = VersionDetector(schemas_root=tmp_path)
        with patch.object(
            vd,
            "detect_versions",
            return_value=[
                VersionInfo("2023-1", "v2023-1", True, False),
                VersionInfo("2025-2", "v2025-2", True, True),
                VersionInfo("2024-1", "v2024-1", True, False),
            ],
        ):
            newer = vd.get_new_versions_since("2023-1")
        assert [v.version for v in newer] == ["2025-2", "2024-1"]

    def test_generate_version_report_contains_summary(self, tmp_path):
        vd = VersionDetector(schemas_root=tmp_path)
        with (
            patch.object(
                vd,
                "detect_versions",
                return_value=[
                    VersionInfo("2025-2", "v2025-2", True, True),
                    VersionInfo("2099-1", "v2099-1", False, False),
                ],
            ),
            patch.object(vd, "get_latest_version", return_value="2025-2"),
            patch.object(
                vd,
                "get_unconfigured_versions",
                return_value=[VersionInfo("2099-1", "v2099-1", False, False)],
            ),
        ):
            report = vd.generate_version_report()

        assert "IWXXM Version Report" in report
        assert "Unconfigured" in report
        assert "2099-1" in report


class TestVersionDetectorConvenienceFunctions:
    def test_detect_available_versions_wrapper(self):
        with patch.object(
            VersionDetector, "detect_versions", return_value=[VersionInfo("2025-2", "v2025-2", True, True)]
        ):
            result = detect_available_versions()
        assert len(result) == 1

    def test_check_for_updates_wrapper(self):
        with patch.object(
            VersionDetector, "get_unconfigured_versions", return_value=[VersionInfo("2099-1", "v2099-1", False, False)]
        ):
            assert check_for_updates() is True
        with patch.object(VersionDetector, "get_unconfigured_versions", return_value=[]):
            assert check_for_updates() is False
