"""Public ``validate()`` entrypoint for IWXXM XSD + Schematron (F2)."""

from __future__ import annotations

from collections.abc import Sequence

from iwxxm_validate.models import Issue, ValidationReport
from iwxxm_validate.paths import ca_xsd_path, us_catalog_path
from iwxxm_validate.schematron import validate_schematron
from iwxxm_validate.xsd import validate_xsd

_DEFAULT_LEVELS: tuple[str, ...] = ("xsd", "schematron")
_VALID_PROFILES = frozenset({"annex3", "iwxxm_us", "ca_eccc"})
_CA_ECCC_IWXXM_VERSION = "3.0.0"
_VALID_LEVELS = frozenset({"xsd", "schematron"})


def validate(
    xml_content: str,
    *,
    iwxxm_version: str,
    profile: str = "annex3",
    levels: Sequence[str] | None = None,
) -> ValidationReport:
    """
    Validate IWXXM XML against vendored XSD and/or Schematron.

    Parameters
    ----------
    xml_content :
        IWXXM XML document.
    iwxxm_version :
        Release line (e.g. ``2023-1``).
    profile :
        ``annex3`` (default), ``iwxxm_us`` (requires vendored US catalog), or
        ``ca_eccc`` (requires vendored ``iwxxm-ca`` pin; IWXXM version ``3.0.0``).
    levels :
        Subset of ``xsd`` / ``schematron``. Default runs both.

    Returns
    -------
    ValidationReport
        ``ok`` is ``False`` when any error-severity issue is present.
        XSLT2 Schematron yields non-blocking ``SCHEMATRON_SKIPPED`` (D-S008-T21-sch).
    """
    if profile not in _VALID_PROFILES:
        return ValidationReport(
            ok=False,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[
                Issue(
                    severity="error",
                    code="INVALID_PROFILE",
                    message=f"Unknown profile {profile!r}; expected annex3|iwxxm_us|ca_eccc",
                    layer="xsd",
                )
            ],
        )

    selected = tuple(levels) if levels is not None else _DEFAULT_LEVELS
    unknown = [level for level in selected if level not in _VALID_LEVELS]
    if unknown:
        return ValidationReport(
            ok=False,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[
                Issue(
                    severity="error",
                    code="INVALID_LEVELS",
                    message=f"Unknown validation levels: {unknown}",
                    layer="xsd",
                )
            ],
        )

    issues: list[Issue] = []

    if profile == "ca_eccc":
        if ca_xsd_path() is None:
            issues.append(
                Issue(
                    severity="error",
                    code="CA_SCHEMA_NOT_FOUND",
                    message="profile=ca_eccc but vendor iwxxm-ca schema pin is missing",
                    layer="xsd",
                )
            )
            return ValidationReport(
                ok=False,
                iwxxm_version=iwxxm_version,
                profile=profile,
                issues=issues,
            )
        if iwxxm_version != _CA_ECCC_IWXXM_VERSION:
            issues.append(
                Issue(
                    severity="error",
                    code="INVALID_IWXXM_VERSION",
                    message=(
                        f"profile=ca_eccc requires iwxxm_version {_CA_ECCC_IWXXM_VERSION!r}, got {iwxxm_version!r}"
                    ),
                    layer="xsd",
                )
            )
            return ValidationReport(
                ok=False,
                iwxxm_version=iwxxm_version,
                profile=profile,
                issues=issues,
            )

    if profile == "iwxxm_us" and us_catalog_path() is None:
        issues.append(
            Issue(
                severity="error",
                code="US_CATALOG_NOT_FOUND",
                message="profile=iwxxm_us but vendor iwxxm-us catalog is missing",
                layer="xsd",
            )
        )
        return ValidationReport(
            ok=False,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=issues,
        )

    if "xsd" in selected:
        issues.extend(validate_xsd(xml_content, iwxxm_version))
        # Malformed XML already reported — skip Schematron
        if any(issue.code == "XML_SYNTAX_ERROR" for issue in issues):
            return ValidationReport(
                ok=False,
                iwxxm_version=iwxxm_version,
                profile=profile,
                issues=issues,
            )

    if "schematron" in selected:
        # Skip Schematron when XSD already failed hard on syntax
        if not any(issue.code == "XML_SYNTAX_ERROR" for issue in issues):
            issues.extend(validate_schematron(xml_content, iwxxm_version))

    ok = not any(issue.severity == "error" for issue in issues)
    return ValidationReport(
        ok=ok,
        iwxxm_version=iwxxm_version,
        profile=profile,
        issues=issues,
    )


__all__ = ["validate"]
