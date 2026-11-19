"""Shared validation-level helpers for ``validate_iwxxm``."""

from __future__ import annotations

from iwxxm_validate.ca_eccc_bundle import ca_eccc_catalog_roots
from iwxxm_validate.codelists import validate_codelist_references
from iwxxm_validate.gml import validate_gml_references
from iwxxm_validate.models import Issue, ValidationReport
from iwxxm_validate.paths import (
    codelists_dir,
    repo_root,
    vendor_iwxxm_root,
    version_dir,
)


def catalog_roots(iwxxm_version: str, *, profile: str = "annex3") -> list[str]:
    """
    Return schema catalog roots for the native / lxml resolvers.

    Parameters
    ----------
    iwxxm_version : str
        IWXXM release line.
    profile : str, optional
        Validation profile. By default ``'annex3'``.

    Returns
    -------
    list[str]
        Existing catalog root directory paths.
    """
    vdir = version_dir(iwxxm_version)
    root = vendor_iwxxm_root()
    candidates = [
        vdir / "IWXXM",
        vdir,
        root / "externalSchema",
        root / "externalSchema" / "schemas.opengis.net",
        root / "externalSchema" / "schemas.wmo.int",
        root,
        # Optional monorepo-only fallback (excluded from the wheel subset).
        repo_root() / "vendor" / "schemas" / "iwxxm-translation" / "externalSchema",
    ]
    if profile in {"ca_eccc", "ca_msc_sigmet"}:
        return ca_eccc_catalog_roots(iwxxm_version)
    return [str(p) for p in candidates if p.is_dir()]


def append_extended_levels(
    issues: list[Issue],
    xml_content: str,
    *,
    iwxxm_version: str,
    selected: tuple[str, ...],
) -> list[Issue]:
    """
    Append GML / codelist findings when those levels are selected.

    Parameters
    ----------
    issues : list[Issue]
        Existing findings.
    xml_content : str
        IWXXM XML.
    iwxxm_version : str
        IWXXM release line.
    selected : tuple[str, ...]
        Selected validation levels.

    Returns
    -------
    list[Issue]
        Merged findings.
    """
    out = list(issues)
    try:
        cl_dir = codelists_dir(iwxxm_version)
    except FileNotFoundError:
        cl_dir = None
    if "gml" in selected:
        out.extend(validate_gml_references(xml_content, codelists_dir=cl_dir))
    if "codelists" in selected:
        if cl_dir is not None:
            out.extend(validate_codelist_references(xml_content, codelists_dir=cl_dir))
        else:
            out.append(
                Issue(
                    severity="warning",
                    code="CODELIST_DIR_NOT_FOUND",
                    message=f"Codelists directory not found for {iwxxm_version}",
                    layer="codelists",
                )
            )
    return out


def report_from_issues(
    issues: list[Issue],
    *,
    iwxxm_version: str,
    profile: str,
) -> ValidationReport:
    """
    Build a :class:`ValidationReport` from a flat issue list.

    Parameters
    ----------
    issues : list[Issue]
        Findings.
    iwxxm_version : str
        IWXXM release line.
    profile : str
        Profile id.

    Returns
    -------
    ValidationReport
        Aggregate report.
    """
    ok = not any(issue.severity == "error" for issue in issues)
    return ValidationReport(
        ok=ok,
        iwxxm_version=iwxxm_version,
        profile=profile,
        issues=issues,
    )


__all__ = ["append_extended_levels", "catalog_roots", "report_from_issues"]
