"""
IWXXM Version Detection Utility

Detects available IWXXM versions from git submodule tags and compares against
configured versions to identify upgrade opportunities.
"""

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..config.iwxxm_versions import SUPPORTED_VERSIONS, normalize_version

logger = logging.getLogger(__name__)


@dataclass
class VersionInfo:
    """Information about an IWXXM version."""

    version: str
    tag: str
    is_configured: bool
    is_latest: bool
    schemas_path: Path | None = None
    schematron_path: Path | None = None
    has_codelists: bool = False


class VersionDetector:
    """Detects available IWXXM versions from git submodule."""

    def __init__(self, schemas_root: Path | None = None) -> None:
        """
        Initialize version detector.

        Args:
            schemas_root: Root directory of schemas (defaults to project schemas/)
        """
        if schemas_root is None:
            # Default to project root/schemas
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent
            schemas_root = project_root / "schemas"

        self.schemas_root = schemas_root
        self.iwxxm_path = schemas_root / "iwxxm"
        self.codelists_path = schemas_root / "iwxxm-codelists"
        self.modelling_path = schemas_root / "iwxxm-modelling"

    def get_available_tags(self) -> list[str]:
        """
        Get all available version tags from iwxxm git submodule.

        Returns:
            List of git tags (e.g., ['v2025-2', 'v2023-1', 'v2021-2'])
        """
        try:
            # Get all tags from the submodule
            result = subprocess.run(
                ["git", "tag", "-l", "v*"], cwd=self.iwxxm_path, capture_output=True, text=True, check=True, timeout=10
            )

            tags = [tag.strip() for tag in result.stdout.split("\n") if tag.strip()]

            # Filter to version tags (v20XX-X format)
            version_tags = [tag for tag in tags if tag.startswith("v") and "-" in tag]

            if version_tags:
                return sorted(version_tags, reverse=True)  # Newest first

        except subprocess.CalledProcessError as e:
            logger.debug(f"Failed to get git tags: {e}")
        except subprocess.TimeoutExpired:
            logger.debug("Git tag command timed out")
        except Exception as e:
            logger.debug(f"Unexpected error getting tags: {e}")

        # Fallback: Check for versioned directories (used with git archive)
        try:
            available_dirs: list[Any] = []
            if self.iwxxm_path.exists():
                for item in self.iwxxm_path.iterdir():
                    if item.is_dir() and item.name.startswith(("v", "20")):
                        # Convert directory name to tag format
                        dir_name = item.name
                        if not dir_name.startswith("v"):
                            dir_name = f"v{dir_name}"
                        available_dirs.append(dir_name)

            if available_dirs:
                return sorted(available_dirs, reverse=True)
        except Exception as e:
            logger.debug(f"Failed to read versioned directories: {e}")

        return []

    def get_latest_version(self) -> str | None:
        """
        Read LATEST_VERSION file to get current official WMO version.

        Returns:
            Version string (e.g., '2025-2') or None if not found
        """
        latest_file = self.iwxxm_path / "LATEST_VERSION"

        if not latest_file.exists():
            logger.warning(f"LATEST_VERSION file not found: {latest_file}")
            return None

        try:
            content = latest_file.read_text().strip()
            # File format: "2025-2|IWXXM" or just "2025-2"
            version = content.split("|")[0].strip()
            return version
        except Exception as e:
            logger.error(f"Error reading LATEST_VERSION: {e}")
            return None

    def tag_to_version(self, tag: str) -> str:
        """
        Convert git tag to version string.

        Args:
            tag: Git tag (e.g., 'v2025-2')

        Returns:
            Version string (e.g., '2025-2')
        """
        # Remove 'v' prefix
        return tag.lstrip("v")

    def version_to_tag(self, version: str) -> str:
        """
        Convert version string to git tag.

        Args:
            version: Version string (e.g., '2025-2')

        Returns:
            Git tag (e.g., 'v2025-2')
        """
        if not version.startswith("v"):
            return f"v{version}"
        return version

    def check_version_files(self, version: str) -> dict[str, bool]:
        """
        Check if required files exist for a version.

        Args:
            version: IWXXM version (e.g., '2025-2')

        Returns:
            Dict with file existence flags
        """
        iwxxm_dir = self.iwxxm_path / "IWXXM"

        return {
            "xsd": (iwxxm_dir / "iwxxm.xsd").exists(),
            "metar_xsd": (iwxxm_dir / "metarSpeci.xsd").exists(),
            "schematron": (iwxxm_dir / "rule" / "iwxxm.sch").exists(),
            "codelists": (iwxxm_dir / "rule").exists() and any((iwxxm_dir / "rule").glob("*.rdf")),
        }

    def detect_versions(self) -> list[VersionInfo]:
        """
        Detect all available IWXXM versions and their configuration status.

        Returns:
            List of VersionInfo objects with details about each version
        """
        available_tags = self.get_available_tags()
        latest_version = self.get_latest_version()
        configured_versions = set(SUPPORTED_VERSIONS.keys())

        version_infos: list[Any] = []

        for tag in available_tags:
            version = self.tag_to_version(tag)
            normalized = normalize_version(version)

            # Check if version is configured
            is_configured = normalized in configured_versions
            is_latest = version == latest_version

            # Check file existence (this would require checking out the tag)
            # For now, assume files exist if it's a known tag

            info = VersionInfo(
                version=version,
                tag=tag,
                is_configured=is_configured,
                is_latest=is_latest,
                has_codelists=True,  # Assume true for tagged versions
            )

            version_infos.append(info)

        return version_infos

    def get_unconfigured_versions(self) -> list[VersionInfo]:
        """
        Get versions that are available but not yet configured.

        Returns:
            List of VersionInfo for unconfigured versions
        """
        all_versions = self.detect_versions()
        return [v for v in all_versions if not v.is_configured]

    def get_new_versions_since(self, current_version: str) -> list[VersionInfo]:
        """
        Get versions newer than the specified version.

        Args:
            current_version: Reference version (e.g., '2023-1')

        Returns:
            List of VersionInfo for newer versions
        """
        all_versions = self.detect_versions()

        # Simple string comparison (works for YYYY-N format)
        newer_versions = [v for v in all_versions if v.version > current_version]

        return sorted(newer_versions, key=lambda v: v.version, reverse=True)

    def generate_version_report(self) -> str:
        """
        Generate a human-readable report of IWXXM versions.

        Returns:
            Formatted report string
        """
        versions = self.detect_versions()
        latest = self.get_latest_version()
        unconfigured = self.get_unconfigured_versions()

        report = ["=" * 60]
        report.append("IWXXM Version Report")
        report.append("=" * 60)
        report.append("")

        report.append(f"Latest WMO Version: {latest or 'Unknown'}")
        report.append(f"Total Available: {len(versions)}")
        report.append(f"Configured: {len([v for v in versions if v.is_configured])}")
        report.append(f"Unconfigured: {len(unconfigured)}")
        report.append("")

        if unconfigured:
            report.append("⚠️  Unconfigured Versions Available:")
            for v in unconfigured:
                marker = "📍 LATEST" if v.is_latest else ""
                report.append(f"  - {v.version} (tag: {v.tag}) {marker}")
            report.append("")

        report.append("All Available Versions:")
        report.append("-" * 60)
        for v in versions:
            status = "✅ Configured" if v.is_configured else "❌ Not Configured"
            latest_marker = " [LATEST]" if v.is_latest else ""
            report.append(f"  {v.version:<10} {status:<20} {latest_marker}")

        report.append("=" * 60)

        return "\n".join(report)


def detect_available_versions() -> list[VersionInfo]:
    """
    Convenience function to detect available IWXXM versions.

    Returns:
        List of VersionInfo objects
    """
    detector = VersionDetector()
    return detector.detect_versions()


def check_for_updates() -> bool:
    """
    Check if there are new IWXXM versions available.

    Returns:
        True if unconfigured versions exist
    """
    detector = VersionDetector()
    unconfigured = detector.get_unconfigured_versions()
    return len(unconfigured) > 0
