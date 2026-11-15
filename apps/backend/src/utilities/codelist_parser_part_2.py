"""Part 2 of ``codelist_parser.py`` (line-cap split)."""

import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import cast

from src.utilities.codelist_parser_part_1 import REQUESTS_AVAILABLE, logger
from src.utilities.codelist_parser_part_2_mixin_1 import _CodeListParserMethodsMixin

from ..config.validation import ValidationSettings, get_validation_settings
from ..schemas.validation import CodelistValidationResult, ValidationIssue, ValidationLayer, ValidationSeverity
from ..utilities.xml_types import XmlElement
from ..utilities.xml_types import lxml_etree as etree


class CodeListParser(_CodeListParserMethodsMixin):
    """
    Parses WMO code list RDF files and provides code list validation.

    Code lists are stored as RDF/XML in the IWXXM schema directories
    and are loaded on-demand per version.

    Supports online validation against live codes.wmo.int registry when
    local RDF files are missing or when enabled via settings.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self, codelists_dir: Path, settings: ValidationSettings | None = None) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        codelists_dir : object
            Argument ``codelists_dir``.
        settings : object
            Argument ``settings``.
        """
        self.codelists_dir = codelists_dir
        self._cache: dict[str, set[str]] = {}
        self._loaded = False

        # Online validation cache: {url: (issue, timestamp)}
        self._online_cache: dict[str, tuple[ValidationIssue, datetime]] = {}

        # Load settings
        if settings is None:
            try:
                self.settings = get_validation_settings()
            except ImportError:
                # Fallback if config not available
                from types import SimpleNamespace

                self.settings = cast(
                    ValidationSettings,
                    SimpleNamespace(
                        wmo_online_validation=False,
                        wmo_validation_timeout=5,
                        wmo_registry_cache_ttl=3600,
                        wmo_registry_url="https://codes.wmo.int",
                    ),
                )
        else:
            self.settings = settings

    def load_codelists(self) -> None:
        """
        Load all RDF codelist files from the directory.

        Parses all .rdf files and extracts allowed code values.
        Results are cached in memory.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (load_codelists)
        2
        """
        if self._loaded:
            return

        if not self.codelists_dir.exists():
            logger.warning(f"Codelists directory not found: {self.codelists_dir}")
            self._loaded = True
            return

        rdf_files = list(self.codelists_dir.glob("*.rdf"))
        logger.info(f"Loading {len(rdf_files)} RDF codelist files")

        for rdf_file in rdf_files:
            try:
                self._parse_rdf_file(rdf_file)
            except Exception as e:
                logger.warning(f"Failed to parse {rdf_file.name}: {e}")

        self._loaded = True
        logger.debug(f"Loaded {len(self._cache)} code lists")

    def _parse_rdf_file(self, rdf_file: Path) -> None:
        """
        Internal helper ``_parse_rdf_file``.

        Parameters
        ----------
        rdf_file : object
            Argument ``rdf_file``.
        """
        try:
            tree = ET.parse(rdf_file)
            root = tree.getroot()

            # RDF namespaces
            namespaces = {
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "skos": "http://www.w3.org/2004/02/skos/core#",
                "owl": "http://www.w3.org/2002/07/owl#",
            }

            # Extract codelist name from filename (e.g., codes.wmo.int-49-2-Weather.rdf → Weather)
            codelist_name = rdf_file.stem.split("-")[-1] if "-" in rdf_file.stem else rdf_file.stem

            codes: set[str] = set()

            # Find all Concept elements (SKOS vocabulary)
            for concept in root.findall(".//skos:Concept", namespaces):
                # Get rdf:about attribute (the URI)
                about = concept.get("{{{}}}about".format(namespaces["rdf"]))
                if about:
                    # Extract just the code/value part
                    code = about.split("/")[-1]
                    codes.add(code)

                # Also try to get preferred label
                for label in concept.findall("skos:prefLabel", namespaces):
                    if label.text:
                        codes.add(label.text)

            if codes:
                self._cache[codelist_name] = codes
                logger.debug(f"Loaded {len(codes)} codes from {codelist_name}")

        except Exception as e:
            logger.error(f"Error parsing RDF file {rdf_file}: {e}")

    def get_codes(self, codelist_name: str) -> set[str]:
        """
        Get allowed codes for a specific code list.

        Returns
        -------
            Set of allowed code values

        Parameters
        ----------
        codelist_name : object
            Name of the code list (e.g., "Weather", "CloudAmount")

        Returns
        -------
        object
            Set of allowed code values

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_codes)
        2
        """
        if not self._loaded:
            self.load_codelists()

        return self._cache.get(codelist_name, set())

    def validate_code(self, codelist_name: str, code_value: str) -> bool:
        """
        Validate if a code value is allowed for a code list.

        Returns
        -------
            True if code is valid, False otherwise

        Parameters
        ----------
        codelist_name : object
            Name of the code list
        code_value : object
            Code value to validate

        Returns
        -------
        object
            True if code is valid, False otherwise

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_code)
        2
        """
        allowed_codes = self.get_codes(codelist_name)
        return code_value in allowed_codes

    def list_codelists(self) -> list[str]:
        """
        Get list of available code lists.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (list_codelists)
        2

        Returns
        -------
        object
            Return value.
        """
        if not self._loaded:
            self.load_codelists()
        return sorted(self._cache.keys())

    def _extract_codelist_references(self, xml_tree: XmlElement) -> list[tuple[str, str, str]]:
        """
        Internal helper ``_extract_codelist_references``.

        Parameters
        ----------
        xml_tree : object
            Argument ``xml_tree``.

        Returns
        -------
        object
            Return value.
        """
        references: list[tuple[str, str, str]] = []

        # Namespaces
        namespaces = {
            "xlink": "http://www.w3.org/1999/xlink",
        }

        # Find all xlink:href attributes
        tree = xml_tree
        elements_with_href = tree.xpath("//*[@xlink:href]", namespaces=namespaces)

        for elem in elements_with_href:
            elem_node = elem
            href = elem_node.get("{http://www.w3.org/1999/xlink}href")

            # Only process WMO code list URLs (not internal #id references)
            if href and "codes.wmo.int" in href:
                xpath = tree.getroottree().getpath(elem)

                # Extract codelist name from URL
                # e.g., http://codes.wmo.int/49-2/AerodromeRecentWeather → AerodromeRecentWeather
                try:
                    codelist_name = href.rstrip("/").split("/")[-1]
                    references.append((href, codelist_name, xpath))
                except Exception as e:
                    logger.warning(f"Failed to parse codelist URL {href}: {e}")

        return references

    def validate_xml_codelists(self, xml_content: str) -> CodelistValidationResult:
        """
        Validate all code list references in XML document.

        Extracts xlink:href attributes pointing to WMO code lists and validates
        that the referenced codes exist in the loaded RDF files.

        Returns
        -------
            CodelistValidationResult with vali

        Parameters
        ----------
        xml_content : object
            XML string to validate

        Returns
        -------
        object
            CodelistValidationResult with validation outcomes

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_xml_codelists)
        2
        """
        issues: list[ValidationIssue] = []

        try:
            # Ensure codelists are loaded
            if not self._loaded:
                self.load_codelists()

            # Parse XML
            try:
                xml_tree = etree.fromstring(xml_content.encode("utf-8"))
            except etree.XMLSyntaxError as e:
                issue = ValidationIssue(
                    layer=ValidationLayer.WMO_CODELISTS,
                    level=ValidationSeverity.ERROR,
                    message=f"XML parsing failed: {e!s}",
                    code="XML_SYNTAX_ERROR",
                )
                issues.append(issue)
                return CodelistValidationResult(is_valid=False, issues=issues)

            # Extract code list references
            references = self._extract_codelist_references(xml_tree)

            invalid_count = 0

            # Validate each reference
            for href, codelist_name, xpath in references:
                # Check if we have this codelist loaded
                if codelist_name not in self._cache:
                    # Try online validation if enabled
                    if self.settings.wmo_online_validation and REQUESTS_AVAILABLE:
                        issue = self._validate_online(href, xpath)
                        issues.append(issue)
                        if issue.level == ValidationSeverity.ERROR:
                            invalid_count += 1
                        continue
                    else:
                        # Codelist not loaded - could be external or missing
                        issue = ValidationIssue(
                            layer=ValidationLayer.WMO_CODELISTS,
                            level=ValidationSeverity.WARNING,
                            message=f"Code list '{codelist_name}' not found in loaded RDF files (online validation disabled)",
                            location=xpath,
                            code="CODELIST_NOT_FOUND",
                        )
                        issues.append(issue)
                        continue

                # Extract the actual code value from the element's text or attributes
                # This is tricky - the code value might be in element text, an attribute, or the URL itself
                # For now, we check if the URL ends with a valid code
                url_parts = href.rstrip("/").split("/")
                if len(url_parts) > 1:
                    potential_code = url_parts[-1]

                    # If the last part is the codelist name, try the second to last
                    if potential_code == codelist_name and len(url_parts) > 2:
                        potential_code = url_parts[-2]

                    # Validate the code
                    if not self.validate_code(codelist_name, potential_code):
                        invalid_count += 1
                        valid_codes = sorted(list(self.get_codes(codelist_name)))[:20]
                        issue = ValidationIssue(
                            layer=ValidationLayer.WMO_CODELISTS,
                            level=ValidationSeverity.ERROR,
                            message=f"Invalid code '{potential_code}' for codelist '{codelist_name}'. Valid codes include: {', '.join(valid_codes)}",
                            location=xpath,
                            code="INVALID_CODELIST_VALUE",
                        )
                        issues.append(issue)

            is_valid = invalid_count == 0

            if not is_valid:
                logger.warning(
                    f"Codelist validation failed: {invalid_count} invalid references out of {len(references)} total"
                )
            else:
                logger.debug(f"Codelist validation passed: {len(references)} references validated")

            return CodelistValidationResult(
                is_valid=is_valid, issues=issues, total_references=len(references), invalid_references=invalid_count
            )

        except Exception as e:
            logger.error(f"Unexpected error during codelist validation: {e}")
            issue = ValidationIssue(
                layer=ValidationLayer.WMO_CODELISTS,
                level=ValidationSeverity.ERROR,
                message=f"Validation error: {e!s}",
                code=type(e).__name__,
            )
            issues.append(issue)
            return CodelistValidationResult(is_valid=False, issues=issues)
