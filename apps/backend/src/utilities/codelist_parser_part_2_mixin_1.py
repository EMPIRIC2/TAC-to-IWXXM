"""Mixin extracted from ``codelist_parser_part_2.py``::CodeListParser."""

from datetime import UTC, datetime
from typing import cast

from ..schemas.validation import ValidationIssue, ValidationLayer, ValidationSeverity
from ..utilities.xml_types import lxml_etree as etree
from .codelist_parser_part_1 import REQUESTS_AVAILABLE, logger


def _requests_mod() -> object:
    """Prefer facade ``requests`` so unit tests can monkeypatch the package module."""
    import sys

    fac = sys.modules.get("src.utilities.codelist_parser")
    if fac is not None and hasattr(fac, "requests"):
        return fac.requests
    import requests as _requests

    return _requests


def _requests_available() -> bool:
    import sys

    fac = sys.modules.get("src.utilities.codelist_parser")
    if fac is not None and hasattr(fac, "REQUESTS_AVAILABLE"):
        return bool(fac.REQUESTS_AVAILABLE)
    return bool(REQUESTS_AVAILABLE)


class _CodeListParserMethodsMixin:
    """Methods mixin for ``CodeListParser``."""

    def _validate_online(self, code_url: str, xpath: str) -> ValidationIssue:
        """
        Internal helper ``_validate_online``.

        Parameters
        ----------
        code_url : object
            Argument ``code_url``.
        xpath : object
            Argument ``xpath``.

        Returns
        -------
        object
            Return value.
        """
        if not _requests_available():
            return ValidationIssue(
                layer=ValidationLayer.WMO_CODELISTS,
                level=ValidationSeverity.WARNING,
                message="Online validation unavailable (requests library not installed)",
                location=xpath,
                code="ONLINE_VALIDATION_UNAVAILABLE",
            )

        # Check cache with TTL
        if code_url in self._online_cache:
            cached_issue, cached_time = self._online_cache[code_url]
            age = (datetime.now(UTC).replace(tzinfo=None) - cached_time).total_seconds()
            if age < self.settings.wmo_registry_cache_ttl:
                logger.debug(f"Online validation cache hit: {code_url} (age: {age:.0f}s)")
                # Update location for cached issue
                cached_issue.location = xpath
                return cached_issue

        # Fetch from registry
        try:
            logger.info(f"Validating code online: {code_url}")
            if _requests_mod() is None:
                return ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.WARNING,
                    message="Online validation unavailable: requests library not installed",
                    location=xpath,
                    code="CODELIST_REQUESTS_UNAVAILABLE",
                )
            response = _requests_mod().get(
                code_url, timeout=self.settings.wmo_validation_timeout, headers={"Accept": "application/rdf+xml"}
            )

            if response.status_code == 200:
                # Parse RDF and extract status
                status = self._parse_rdf_status(response.content)

                if status in ["valid", "stable"]:
                    result = ValidationIssue(
                        layer=ValidationLayer.WMO_CODELISTS,
                        level=ValidationSeverity.INFO,
                        message=f"Code validated online: {code_url} (status: {status})",
                        location=xpath,
                        code="CODELIST_VALID_ONLINE",
                    )
                elif status in ["superseded", "deprecated"]:
                    result = ValidationIssue(
                        layer=ValidationLayer.WMO_CODELISTS,
                        level=ValidationSeverity.WARNING,
                        message=f"Code status '{status}': {code_url}",
                        location=xpath,
                        code="CODELIST_DEPRECATED",
                    )
                else:
                    result = ValidationIssue(
                        layer=ValidationLayer.WMO_CODELISTS,
                        level=ValidationSeverity.WARNING,
                        message=f"Code status unknown ('{status}'): {code_url}",
                        location=xpath,
                        code="CODELIST_STATUS_UNKNOWN",
                    )

                # Cache result
                self._online_cache[code_url] = (result, datetime.now(UTC).replace(tzinfo=None))
                return result

            elif response.status_code == 404:
                result = ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.ERROR,
                    message=f"Code not found in WMO registry: {code_url}",
                    location=xpath,
                    code="CODELIST_NOT_FOUND",
                )
                self._online_cache[code_url] = (result, datetime.now(UTC).replace(tzinfo=None))
                return result
            else:
                return ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.WARNING,
                    message=f"Registry returned {response.status_code}: {code_url}",
                    location=xpath,
                    code="CODELIST_ONLINE_ERROR",
                )

        except Exception as e:
            req = _requests_mod()
            timeout_error = None
            if req is not None:
                timeout_error = getattr(getattr(req, "exceptions", req), "Timeout", None)
                if timeout_error is None:
                    timeout_error = getattr(req, "Timeout", None)
            if timeout_error is not None and isinstance(e, timeout_error):
                logger.warning(f"Online validation timeout for {code_url}")
                return ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.WARNING,
                    message=f"Online validation timeout ({self.settings.wmo_validation_timeout}s): {code_url}",
                    location=xpath,
                    code="CODELIST_TIMEOUT",
                )
            logger.error(f"Online validation error: {e}")
            return ValidationIssue(
                layer=ValidationLayer.WMO_CODELISTS,
                level=ValidationSeverity.WARNING,
                message=f"Online validation failed: {e!s}",
                location=xpath,
                code="CODELIST_ONLINE_FAILED",
            )

    def _parse_rdf_status(self, rdf_content: bytes) -> str:
        """
        Internal helper ``_parse_rdf_status``.

        Parameters
        ----------
        rdf_content : object
            Argument ``rdf_content``.

        Returns
        -------
        object
            Return value.
        """
        try:
            root = etree.fromstring(rdf_content)

            # SKOS concept status in RDF
            # <skos:Concept>
            #   <reg:status rdf:resource="http://codes.wmo.int/common/reg-status/valid"/>
            # </skos:Concept>
            namespaces = {
                "reg": "http://purl.org/linked-data/registry#",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            }

            # Find status element
            status_elems = cast(list[str], root.xpath(".//reg:status/@rdf:resource", namespaces=namespaces))
            if status_elems:
                status_url = status_elems[0]
                # Extract last part: .../reg-status/valid -> "valid"
                status = status_url.split("/")[-1] if status_url else "unknown"
                logger.debug(f"Parsed RDF status: {status}")
                return status

            # Fallback: if no explicit status, assume valid if concept exists
            concepts = root.xpath(".//skos:Concept", namespaces=namespaces)
            if concepts:
                logger.debug("No explicit status, assuming 'valid' (concept exists)")
                return "valid"

            return "unknown"
        except Exception as e:
            logger.warning(f"Failed to parse RDF status: {e}")
            return "unknown"
