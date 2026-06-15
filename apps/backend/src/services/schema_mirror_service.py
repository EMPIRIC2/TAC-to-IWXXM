"""
IWXXM Schema Mirroring Service

Downloads and stores IWXXM schema releases (XSD, Schematron, codelists) locally
with integrity verification via SHA256 checksums and lockfile management.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Set
from urllib.parse import urljoin, urlparse

import httpx

logger = logging.getLogger(__name__)


class SchemaMirrorService:
    """
    Mirrors IWXXM schema trees from remote URLs to local storage.

    Handles recursive XSD imports/includes, computes checksums, and maintains
    manifest and lockfile for reproducible validation.
    """

    def __init__(
        self,
        base_path: Path,
        timeout_seconds: int = 60
    ):
        """
        Initialize the mirror service.

        Args:
            base_path: Root directory for mirrored schemas (e.g., PROJECT_ROOT/schemas/iwxxm)
            timeout_seconds: HTTP request timeout
        """
        self.base_path = Path(base_path)
        self.timeout_seconds = timeout_seconds
        self.downloaded_files: Set[str] = set()
        self.current_version_dir: Optional[Path] = None  # Track current version being mirrored

    async def mirror_version(
        self,
        version: str,
        root_xsd_url: str,
        include_examples: bool = True,
        include_html: bool = True,
        include_xmi: bool = True
    ) -> Dict[str, any]:
        """
        Mirror a complete schema version tree.

        Args:
            version: IWXXM version string (e.g., "2025-2RC1")
            root_xsd_url: URL to root XSD file (e.g., ".../iwxxm.xsd")
            include_examples: Download examples/ directory (recommended)
            include_html: Download html/ UML documentation
            include_xmi: Download XMI/ UML model exports

        Returns:
            Dictionary with mirroring results and manifest
        """
        logger.info(f"Starting mirror for IWXXM {version} from {root_xsd_url}")

        version_dir = self.base_path / version
        version_dir.mkdir(parents=True, exist_ok=True)

        # Track version dir for relative path calculations
        self.current_version_dir = version_dir

        # Derive base URL from root XSD URL
        base_url = root_xsd_url.rsplit("/", 1)[0] + "/"

        # Reset download tracking
        self.downloaded_files.clear()

        # Download root XSD and recursively follow imports
        manifest = {}
        await self._download_xsd_tree(root_xsd_url, version_dir, manifest)

        # Download additional resources
        if include_examples:
            examples_url = urljoin(base_url, "examples/")
            await self._download_directory(examples_url, version_dir / "examples", manifest)

        if include_html:
            html_url = urljoin(base_url, "html/")
            await self._download_directory(html_url, version_dir / "html", manifest, skip_on_404=True)

        if include_xmi:
            xmi_url = urljoin(base_url, "XMI/")
            await self._download_directory(xmi_url, version_dir / "XMI", manifest, skip_on_404=True)

        # Write manifest with checksums
        manifest_data = {
            "version": version,
            "mirrored_at": datetime.now(timezone.utc).isoformat(),
            "root_url": root_xsd_url,
            "base_url": base_url,
            "resources": {
                "schemas": True,
                "examples": include_examples,
                "html": include_html,
                "xmi": include_xmi
            },
            "files": manifest
        }

        manifest_path = version_dir / ".manifest.json"
        with manifest_path.open("w") as f:
            json.dump(manifest_data, f, indent=2)

        logger.info(f"Mirror complete for {version}: {len(manifest)} files")

        # Update global lockfile
        await self._update_lockfile(version, manifest_data)

        return {
            "version": version,
            "files_mirrored": len(manifest),
            "manifest_path": str(manifest_path),
            "version_dir": str(version_dir)
        }

    async def _download_xsd_tree(
        self,
        xsd_url: str,
        target_dir: Path,
        manifest: Dict[str, Dict]
    ):
        """
        Recursively download XSD and all imports/includes.

        Args:
            xsd_url: URL to XSD file
            target_dir: Local directory for this file
            manifest: Dictionary to populate with file metadata
        """
        if xsd_url in self.downloaded_files:
            return

        self.downloaded_files.add(xsd_url)

        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            try:
                response = await client.get(xsd_url)
                response.raise_for_status()
                content = response.content

                # Determine local filename from URL
                parsed = urlparse(xsd_url)
                filename = Path(parsed.path).name

                # Handle subdirectories (e.g., rule/iwxxm.sch)
                if "/" in parsed.path:
                    rel_path = Path(parsed.path).relative_to(Path(parsed.path).parts[0])
                    local_file = target_dir / rel_path
                else:
                    local_file = target_dir / filename

                local_file.parent.mkdir(parents=True, exist_ok=True)

                # Write file
                with local_file.open("wb") as f:
                    f.write(content)

                # Compute SHA256
                sha256 = hashlib.sha256(content).hexdigest()

                # Add to manifest
                manifest[str(local_file.relative_to(target_dir))] = {
                    "url": xsd_url,
                    "sha256": sha256,
                    "size_bytes": len(content)
                }

                logger.debug(f"Downloaded: {xsd_url} -> {local_file}")

                # Parse for imports/includes (simple regex, not full XML parse)
                if filename.endswith(".xsd"):
                    await self._process_xsd_imports(
                        content.decode("utf-8", errors="ignore"),
                        xsd_url,
                        target_dir,
                        manifest
                    )

            except Exception as e:
                logger.error(f"Error downloading {xsd_url}: {e}")
                raise

    async def _process_xsd_imports(
        self,
        xsd_content: str,
        base_url: str,
        target_dir: Path,
        manifest: Dict
    ):
        """
        Extract and download XSD imports/includes.

        Args:
            xsd_content: XSD file content as string
            base_url: Base URL for resolving relative imports
            target_dir: Target directory
            manifest: Manifest dictionary
        """
        import re

        # Match <xs:import> and <xs:include> schemaLocation attributes
        pattern = re.compile(
            r'<(?:xs:)?(?:import|include)[^>]*?schemaLocation\s*=\s*["\']([^"\']+)["\']',
            re.IGNORECASE
        )

        for match in pattern.finditer(xsd_content):
            schema_location = match.group(1)

            # Resolve relative URLs
            if not schema_location.startswith(("http://", "https://")):
                schema_url = urljoin(base_url, schema_location)
            else:
                schema_url = schema_location

            # Skip external schemas we don't want to mirror (e.g., W3C)
            if "w3.org" in schema_url or "opengis.net" in schema_url:
                logger.debug(f"Skipping external schema: {schema_url}")
                continue

            # Recursively download
            await self._download_xsd_tree(schema_url, target_dir, manifest)

    async def _download_directory(
        self,
        directory_url: str,
        target_dir: Path,
        manifest: Dict,
        skip_on_404: bool = False
    ):
        """
        Download all files from a directory listing (Apache-style index).

        Args:
            directory_url: URL to directory (must end with /)
            target_dir: Local target directory
            manifest: Manifest dictionary to update
            skip_on_404: If True, silently skip if directory doesn't exist
        """
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            try:
                response = await client.get(directory_url)

                if response.status_code == 404 and skip_on_404:
                    logger.debug(f"Directory not found (skipping): {directory_url}")
                    return

                response.raise_for_status()
                html_content = response.text

                # Parse HTML directory listing for files and subdirectories
                import re

                # Match href links (Apache directory listing format)
                # Pattern matches: <a href="filename.ext">
                link_pattern = re.compile(r'<a\s+href="([^"]+)"[^>]*>', re.IGNORECASE)

                for match in link_pattern.finditer(html_content):
                    href = match.group(1)

                    # Skip parent directory links and query params
                    if href in ["../", "?", ""] or href.startswith("?"):
                        continue

                    file_url = urljoin(directory_url, href)

                    # Determine if it's a directory (ends with /)
                    if href.endswith("/"):
                        # Recursively download subdirectory
                        subdir_name = href.rstrip("/")
                        await self._download_directory(
                            file_url,
                            target_dir / subdir_name,
                            manifest,
                            skip_on_404=skip_on_404
                        )
                    else:
                        # Download file
                        await self._download_file(file_url, target_dir, manifest)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404 and skip_on_404:
                    logger.debug(f"Directory not found (skipping): {directory_url}")
                else:
                    logger.error(f"Error downloading directory {directory_url}: {e}")
                    raise
            except Exception as e:
                logger.error(f"Error parsing directory {directory_url}: {e}")
                if not skip_on_404:
                    raise

    async def _download_file(
        self,
        file_url: str,
        target_dir: Path,
        manifest: Dict
    ):
        """
        Download a single file and add to manifest.

        Args:
            file_url: URL to file
            target_dir: Local target directory
            manifest: Manifest dictionary to update
        """
        if file_url in self.downloaded_files:
            return

        self.downloaded_files.add(file_url)

        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=True) as client:
            try:
                response = await client.get(file_url)
                response.raise_for_status()
                content = response.content

                # Determine local filename from URL
                parsed = urlparse(file_url)
                filename = Path(parsed.path).name

                target_dir.mkdir(parents=True, exist_ok=True)
                local_file = target_dir / filename

                # Write file
                with local_file.open("wb") as f:
                    f.write(content)

                # Compute SHA256
                sha256 = hashlib.sha256(content).hexdigest()

                # Add to manifest (relative to version_dir)
                if self.current_version_dir:
                    try:
                        rel_path = local_file.relative_to(self.current_version_dir)
                    except ValueError:
                        # Fallback if file is outside version_dir
                        rel_path = local_file.relative_to(self.base_path)
                else:
                    rel_path = local_file.relative_to(self.base_path)

                manifest[str(rel_path)] = {
                    "url": file_url,
                    "sha256": sha256,
                    "size_bytes": len(content)
                }

                logger.debug(f"Downloaded: {file_url} -> {local_file}")

            except Exception as e:
                logger.error(f"Error downloading file {file_url}: {e}")
                raise

    async def _update_lockfile(self, version: str, manifest_data: Dict):
        """
        Update global schemas.lock.json with new version.

        Args:
            version: Version string
            manifest_data: Manifest data for this version
        """
        lockfile_path = self.base_path / "schemas.lock.json"

        # Load existing lockfile
        if lockfile_path.exists():
            with lockfile_path.open("r") as f:
                lockfile = json.load(f)
        else:
            lockfile = {
                "format_version": "1.0",
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "versions": {}
            }

        # Add/update version entry
        lockfile["versions"][version] = {
            "mirrored_at": manifest_data["mirrored_at"],
            "root_url": manifest_data["root_url"],
            "base_url": manifest_data.get("base_url"),
            "file_count": len(manifest_data["files"]),
            "resources": manifest_data.get("resources", {})
        }
        lockfile["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Write lockfile
        with lockfile_path.open("w") as f:
            json.dump(lockfile, f, indent=2)

        logger.info(f"Updated lockfile: {lockfile_path}")

    async def verify_integrity(self, version: str) -> bool:
        """
        Verify integrity of mirrored schema using manifest checksums.

        Args:
            version: Version to verify

        Returns:
            True if all checksums match, False otherwise
        """
        version_dir = self.base_path / version
        manifest_path = version_dir / ".manifest.json"

        if not manifest_path.exists():
            logger.error(f"Manifest not found for {version}")
            return False

        with manifest_path.open("r") as f:
            manifest_data = json.load(f)

        manifest = manifest_data.get("files", {})

        for rel_path, file_info in manifest.items():
            local_file = version_dir / rel_path

            if not local_file.exists():
                logger.error(f"Missing file: {local_file}")
                return False

            # Verify SHA256
            with local_file.open("rb") as f:
                content = f.read()
                sha256 = hashlib.sha256(content).hexdigest()

            if sha256 != file_info["sha256"]:
                logger.error(
                    f"Checksum mismatch for {rel_path}: "
                    f"expected {file_info['sha256']}, got {sha256}"
                )
                return False

        logger.info(f"Integrity verified for {version}: all checksums match")
        return True


async def mirror_schema_version(
    version: str,
    root_xsd_url: str,
    base_path: Path,
    include_examples: bool = True,
    include_html: bool = True,
    include_xmi: bool = True
) -> Dict:
    """
    Convenience function to mirror a single schema version.

    Args:
        version: IWXXM version string
        root_xsd_url: URL to root XSD
        base_path: Base path for mirrored schemas
        include_examples: Download examples/ directory
        include_html: Download html/ documentation
        include_xmi: Download XMI/ models

    Returns:
        Mirror results dictionary
    """
    service = SchemaMirrorService(base_path)
    return await service.mirror_version(
        version,
        root_xsd_url,
        include_examples=include_examples,
        include_html=include_html,
        include_xmi=include_xmi
    )
