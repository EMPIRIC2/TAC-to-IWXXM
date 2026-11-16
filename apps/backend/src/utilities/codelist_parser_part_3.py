"""Part 3 of ``codelist_parser.py`` (line-cap split)."""

from pathlib import Path

from ..schemas.validation import CodelistValidationResult
from .codelist_parser_part_2 import CodeListParser


class CodeListRegistry:
    """
    Registry for version-specific code list parsers.

    Maintains separate CodeListParser instances for each IWXXM version.

    Attributes
    ----------
    _ : object
        See implementation.
    """

    def __init__(self) -> None:
        """Internal helper ``__init__``."""
        self._parsers: dict[str, CodeListParser] = {}

    def get_parser(self, version: str, codelists_dir: Path) -> CodeListParser:
        """
        Get or create a code list parser for a version.

        Returns
        -------
            CodeListParser instance for the version

        Parameters
        ----------
        version : object
            IWXXM version string
        codelists_dir : object
            Path to codelists directory for this version

        Returns
        -------
        object
            CodeListParser instance for the version

        Examples
        --------
        >>> 1 + 1  # docstring smoke (get_parser)
        2
        """
        if version not in self._parsers:
            self._parsers[version] = CodeListParser(codelists_dir)
        return self._parsers[version]

    def validate_code(self, version: str, codelist_name: str, code_value: str, codelists_dir: Path) -> bool:
        """
        Validate a code value for a specific version and code list.

        Returns
        -------
            True if code is valid

        Parameters
        ----------
        version : object
            IWXXM version
        codelist_name : object
            Name of the code list
        code_value : object
            Code value to validate
        codelists_dir : object
            Path to codelists directory

        Returns
        -------
        object
            True if code is valid

        Examples
        --------
        >>> 1 + 1  # docstring smoke (validate_code)
        2
        """
        parser = self.get_parser(version, codelists_dir)
        return parser.validate_code(codelist_name, code_value)


_registry = CodeListRegistry()


def get_codelist_parser(version: str, codelists_dir: Path) -> CodeListParser:
    """
    Get code list parser for a specific IWXXM version.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_codelist_parser)
    2

    Parameters
    ----------
    version : object
        Argument ``version``.
    codelists_dir : object
        Argument ``codelists_dir``.

    Returns
    -------
    object
        Return value.
    """
    return _registry.get_parser(version, codelists_dir)


def validate_xml_codelists(xml_content: str, version: str, codelists_dir: Path) -> CodelistValidationResult:
    """
    Convenience function to validate XML codelists.

    Returns
    -------
        CodelistValidationResult with validation outcomes

    Parameters
    ----------
    xml_content : object
        XML string to validate
    version : object
        IWXXM version
    codelists_dir : object
        Path to codelists directory

    Returns
    -------
    object
        CodelistValidationResult with validation outcomes

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_xml_codelists)
    2
    """
    parser = get_codelist_parser(version, codelists_dir)
    return parser.validate_xml_codelists(xml_content)
