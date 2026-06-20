"""
IWXXM Schema Discovery Poller

Weekly poller service that detects new IWXXM schema releases (including RC versions)
from WMO schema repositories and triggers complete mirroring/artifact generation
with automated breaking change detection.
"""

import asyncio
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

import httpx

logger = logging.getLogger(__name__)

# WMO schema directory URLs to poll
WMO_SCHEMA_DIRECTORIES = [
    "https://schemas.wmo.int/iwxxm/",
    "https://raw.githubusercontent.com/wmo-im/iwxxm/master/",
]

# Version detection regex: matches 2025-2, 2025-2RC1, 2026-1, etc.
VERSION_PATTERN = re.compile(r"(20\d{2})-(1|2)(?:RC\d+)?", re.IGNORECASE)

# RC version specific pattern
RC_PATTERN = re.compile(r"(20\d{2})-(1|2)(RC\d+)", re.IGNORECASE)


class SchemaDiscoveryPoller:
    """
    Polls WMO schema directories to discover new IWXXM versions.

    Detects both stable releases (e.g., "2025-2") and RC versions (e.g., "2025-2RC1").
    When new versions detected:
    1. Emits discovery events
    2. Triggers complete mirroring (schemas + examples + html + xmi + RDF)
    3. Analyzes XMI for breaking changes
    4. Updates VERSION_DISCOVERY_METADATA
    """

    def __init__(
        self,
        poll_urls: Optional[List[str]] = None,
        timeout_seconds: int = 30,
        mirror_service: Optional[Any] = None,
        xmi_analyzer: Optional[Any] = None,
        base_schema_path: Optional[Path] = None,
    ):
        """
        Initialize the discovery poller.

        Args:
            poll_urls: List of WMO schema directory URLs to poll
            timeout_seconds: HTTP request timeout
            mirror_service: Optional SchemaMirrorService for auto-mirroring
            xmi_analyzer: Optional XMIModelAnalyzer for breaking change detection
            base_schema_path: Optional path to schemas directory
        """
        self.poll_urls = poll_urls or WMO_SCHEMA_DIRECTORIES
        self.timeout_seconds = timeout_seconds
        self.discovered_versions: Set[str] = set()
        self.last_poll_time: Optional[datetime] = None
        self.mirror_service = mirror_service
        self.xmi_analyzer = xmi_analyzer
        self.base_schema_path = base_schema_path or Path(__file__).parent.parent.parent / "schemas" / "iwxxm"
        self.on_new_version_callbacks: List[Callable] = []

    async def poll_once(self) -> dict[str, object]:
        """
        Execute a single poll cycle across all configured URLs.

        When new versions detected, optionally triggers mirroring and breaking change analysis.

        Returns:
            Dictionary with "new_stable" and "new_rc" lists of discovered versions
        """
        logger.info(f"Starting schema discovery poll at {datetime.now(timezone.utc)}")

        new_stable = []
        new_rc = []

        for url in self.poll_urls:
            try:
                versions = await self._poll_url(url)

                for version in versions:
                    if version not in self.discovered_versions:
                        logger.info(f"Discovered new IWXXM version: {version} from {url}")
                        self.discovered_versions.add(version)

                        if self._is_rc_version(version):
                            new_rc.append(version)
                        else:
                            new_stable.append(version)

                        # Trigger callbacks for new version
                        await self._emit_new_version_event(version, url)

            except Exception as e:
                logger.error(f"Error polling {url}: {e}")
                continue

        self.last_poll_time = datetime.now(timezone.utc)

        return {
            "new_stable": new_stable,
            "new_rc": new_rc,
            "poll_time": self.last_poll_time.isoformat(),
            "total_discovered": len(self.discovered_versions),
        }

    async def _emit_new_version_event(self, version: str, source_url: str) -> None:
        """
        Handle discovery of a new version.

        Triggers callbacks and optionally auto-mirrors with examples + XMI.

        Args:
            version: New version discovered
            source_url: URL where version was found
        """
        # Call registered callbacks
        for callback in self.on_new_version_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(version, source_url)
                else:
                    callback(version, source_url)
            except Exception as e:
                logger.error(f"Error in callback for {version}: {e}")

        # Auto-mirror if mirror_service available
        if self.mirror_service:
            await self._trigger_auto_mirror(version, source_url)

    async def _trigger_auto_mirror(self, version: str, source_url: str) -> None:
        """
        Trigger automatic mirroring of a new version.

        Downloads complete version bundle:
        - Schemas (XSD)
        - Examples (~60 XML/TAC pairs)
        - HTML documentation
        - XMI UML models
        - Rule directory (Schematron + RDF codelists)

        Args:
            version: Version to mirror
            source_url: Source URL
        """
        try:
            from ..config.iwxxm_versions import RC_VERSIONS, SUPPORTED_VERSIONS

            # Get root XSD URL from configured versions
            config = SUPPORTED_VERSIONS.get(version) or RC_VERSIONS.get(version)
            if not config:
                logger.warning(f"Version {version} not in configured versions, skipping auto-mirror")
                return

            root_xsd_url = config.get("schema_url")
            if not root_xsd_url:
                logger.warning(f"No schema_url for {version}, cannot mirror")
                return

            logger.info(f"Starting auto-mirror for {version}: {root_xsd_url}")

            # Mirror with all resources
            if self.mirror_service is None:
                logger.warning("Mirror service unavailable")
                return
            result = await self.mirror_service.mirror_version(
                version=version,
                root_xsd_url=root_xsd_url,
                include_examples=True,  # Include XML/TAC examples
                include_html=True,  # Include UML documentation
                include_xmi=True,  # Include UML models for diff analysis
            )

            logger.info(
                f"Auto-mirror completed for {version}: "
                f"{result.get('xsd_count', 0)} XSDs, "
                f"{result.get('example_count', 0)} examples, "
                f"{result.get('xmi_count', 0)} XMI files"
            )

            # Analyze XMI for breaking changes if available
            await self._analyze_breaking_changes(version)

        except Exception as e:
            logger.error(f"Failed to auto-mirror {version}: {e}")

    async def _analyze_breaking_changes(self, new_version: str) -> None:
        """
        Analyze XMI models to detect breaking changes from previous version.

        Args:
            new_version: New version to analyze
        """
        if not self.xmi_analyzer:
            logger.debug("XMI analyzer not available, skipping breaking change detection")
            return

        try:
            from ..config.iwxxm_versions import SUPPORTED_VERSIONS

            # Find previous stable version
            prev_version = None
            all_versions = list(SUPPORTED_VERSIONS.keys())
            try:
                idx = all_versions.index(new_version)
                if idx > 0:
                    prev_version = all_versions[idx - 1]
            except (ValueError, IndexError):
                logger.debug(f"Could not find previous version for {new_version}")

            if not prev_version:
                logger.debug(f"No previous version found for {new_version}")
                return

            # Find XMI files
            new_xmi = self.base_schema_path / new_version / "XMI" / "IWXXM.xmi"
            old_xmi = self.base_schema_path / prev_version / "XMI" / "IWXXM.xmi"

            if not new_xmi.exists():
                logger.warning(f"XMI not found for {new_version}: {new_xmi}")
                return

            if not old_xmi.exists():
                logger.warning(f"XMI not found for {prev_version}: {old_xmi}")
                return

            # Run analysis
            report = self.xmi_analyzer.analyze_xmi_versions(old_xmi, new_xmi, prev_version, new_version)

            logger.info(
                f"Breaking change analysis: {report.get('total_changes', 0)} changes detected "
                f"between {prev_version} → {new_version}"
            )

            # Update VERSION_DISCOVERY_METADATA
            self._update_version_metadata(new_version, new_version, report)

        except Exception as e:
            logger.warning(f"Failed to analyze breaking changes: {e}")

    def _update_version_metadata(self, new_version: str, prior_version: str, breaking_changes_report: Dict) -> None:
        """
        Update VERSION_DISCOVERY_METADATA with breaking changes.

        Args:
            new_version: New version discovered
            prior_version: Previous version for comparison
            breaking_changes_report: Breaking change report from XMI analyzer
        """
        try:
            from ..config.iwxxm_versions import SUPPORTED_VERSIONS

            config = SUPPORTED_VERSIONS.get(new_version)
            if not config:
                logger.warning(f"Version {new_version} not in SUPPORTED_VERSIONS")
                return

            # Convert report to VERSION_DISCOVERY_METADATA format
            breaking_changes = []
            for change in breaking_changes_report.get("details", []):
                breaking_changes.append(
                    {
                        "element": change.element,
                        "xpath": change.xpath or f".//iwxxm:{change.element}",
                        "action": "remove" if change.change_type == "removed" else "change",
                        "reason": change.reason,
                    }
                )

            # Update config
            if not config.get("breaking_changes_from_prior"):
                config["breaking_changes_from_prior"] = {}

            config["breaking_changes_from_prior"][prior_version] = breaking_changes

            logger.info(
                f"Updated VERSION_DISCOVERY_METADATA for {new_version}: "
                f"{len(breaking_changes)} breaking changes from {prior_version}"
            )

        except Exception as e:
            logger.warning(f"Failed to update version metadata: {e}")

    def register_new_version_callback(self, callback: Callable) -> None:
        """
        Register a callback to be invoked when a new version is discovered.

        Callback signature:
        - async: async def callback(version: str, source_url: str) -> None
        - sync: def callback(version: str, source_url: str) -> None

        Args:
            callback: Callable to invoke on new version discovery
        """
        self.on_new_version_callbacks.append(callback)
        logger.debug(f"Registered callback: {callback.__name__}")

    async def _poll_url(self, url: str) -> List[str]:
        """
        Poll a single URL for IWXXM version directories.

        Args:
            url: WMO schema directory URL

        Returns:
            List of detected version strings
        """
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()

                # Parse HTML/directory listing for version links
                content = response.text
                versions = self._extract_versions_from_html(content)

                logger.debug(f"Found {len(versions)} versions at {url}: {versions}")
                return versions

            except httpx.HTTPError as e:
                logger.error(f"HTTP error polling {url}: {e}")
                raise

    def _extract_versions_from_html(self, html_content: str) -> List[str]:
        """
        Extract IWXXM version strings from HTML directory listing.

        Args:
            html_content: HTML response body

        Returns:
            List of version strings found in links
        """
        versions = []

        # Find all matches of version pattern in the HTML
        matches = VERSION_PATTERN.findall(html_content)

        for match in matches:
            # match is a tuple: (year, release, [rc_suffix])
            if isinstance(match, tuple) and len(match) >= 2:
                year, release = match[0], match[1]
                version = f"{year}-{release}"

                # Check if this is an RC version by looking for RC in surrounding text
                # Search for full RC pattern
                rc_matches = RC_PATTERN.findall(html_content)
                for rc_match in rc_matches:
                    if isinstance(rc_match, tuple) and len(rc_match) == 3:
                        rc_year, rc_release, rc_suffix = rc_match
                        if rc_year == year and rc_release == release:
                            version = f"{year}-{release}{rc_suffix}"
                            break

                if version not in versions:
                    versions.append(version)

        # Also look for directory-style links: <a href="2025-2RC1/">
        link_pattern = re.compile(r'href=["\']([^"\']*?(20\d{2}-[12](?:RC\d+)?)[^"\']*?)["\']', re.IGNORECASE)
        for link_match in link_pattern.finditer(html_content):
            full_link = link_match.group(1)
            version_match = VERSION_PATTERN.search(full_link)
            if version_match:
                version = version_match.group(0)
                if version not in versions:
                    versions.append(version)

        return list(set(versions))  # Deduplicate

    def _is_rc_version(self, version: str) -> bool:
        """
        Check if a version string represents a Release Candidate.

        Args:
            version: Version string (e.g., "2025-2RC1", "2025-2")

        Returns:
            True if version is an RC, False otherwise
        """
        return bool(RC_PATTERN.match(version))

    async def poll_with_retry(self, max_retries: int = 3, retry_delay_seconds: int = 60) -> dict[str, object] | None:
        """
        Poll with automatic retry on failure.

        Args:
            max_retries: Maximum number of retry attempts
            retry_delay_seconds: Delay between retries

        Returns:
            Discovery results dictionary, or None when max_retries is 0
        """
        if max_retries <= 0:
            return None

        for attempt in range(max_retries):
            try:
                return await self.poll_once()
            except Exception as e:
                logger.warning(f"Poll attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay_seconds} seconds...")
                    await asyncio.sleep(retry_delay_seconds)
                else:
                    logger.error("All poll attempts failed")
                    raise

    def get_discovered_versions(self, channel: Optional[str] = None) -> List[str]:
        """
        Get all discovered versions, optionally filtered by channel.

        Args:
            channel: Channel filter ("stable", "rc", or None for all)

        Returns:
            List of discovered version strings
        """
        if channel == "stable":
            return [v for v in self.discovered_versions if not self._is_rc_version(v)]
        elif channel == "rc":
            return [v for v in self.discovered_versions if self._is_rc_version(v)]
        else:
            return list(self.discovered_versions)


async def discover_schemas() -> dict[str, object]:
    """
    Convenience function to run a single discovery poll.

    Returns:
        Discovery results with new stable and RC versions
    """
    poller = SchemaDiscoveryPoller()
    return await poller.poll_once()


async def discover_schemas_with_retry(max_retries: int = 3, retry_delay: int = 60) -> dict[str, object] | None:
    """
    Convenience function to run discovery with retry logic.

    Args:
        max_retries: Maximum retry attempts
        retry_delay: Delay between retries in seconds

    Returns:
        Discovery results
    """
    poller = SchemaDiscoveryPoller()
    return await poller.poll_with_retry(max_retries, retry_delay)


def extract_version_from_url(url: str) -> Optional[str]:
    """
    Extract IWXXM version from a schema URL.

    Args:
        url: Schema URL (e.g., "https://schemas.wmo.int/iwxxm/2025-2RC1/iwxxm.xsd")

    Returns:
        Version string or None if not found
    """
    match = VERSION_PATTERN.search(url)
    return match.group(0) if match else None
