"""F13 SDK entrypoint ``validate_iwxxm`` — Rust hot path with lxml fallback (E10-22 / E10-36)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from iwxxm_validate.api import validate
from iwxxm_validate.ca_eccc_bundle import CA_ECCC_IWXXM_VERSION, ca_eccc_catalog_roots
from iwxxm_validate.ca_eccc_validate import validate_ca_eccc_layered
from iwxxm_validate.codelists import validate_codelist_references
from iwxxm_validate.gml import validate_gml_references
from iwxxm_validate.models import Issue, ValidationReport
from iwxxm_validate.native import rust_available, rust_module
from iwxxm_validate.paths import (
    ca_xsd_path,
    codelists_dir,
    repo_root,
    schematron_path,
    us_catalog_path,
    vendor_iwxxm_root,
    version_dir,
    xsd_path,
)
from iwxxm_validate.wellformed import run_wellformed_lxml

_DEFAULT_LEVELS: tuple[str, ...] = ("xsd", "schematron")
_VALID_PROFILES = frozenset({"annex3", "iwxxm_us", "ca_eccc"})
_VALID_LEVELS = frozenset({"wellformed", "xsd", "schematron", "gml", "codelists"})
_RUST_LEVELS = frozenset({"wellformed", "xsd", "schematron"})
_LXML_LEVELS = frozenset({"xsd", "schematron"})


def _catalog_roots(iwxxm_version: str, *, profile: str = "annex3") -> list[str]:
    """Return directory roots for xmloxide ``SchemaResolver`` (packaged / vendor).

    Runtime subset (E10-34) ships ``iwxxm/externalSchema`` only — no translation
    modelling bulk. Monorepo may still resolve translation as a last resort.
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
    if profile == "ca_eccc":
        return ca_eccc_catalog_roots(iwxxm_version)
    return [str(p) for p in candidates if p.is_dir()]


def _issues_from_rust(raw: Sequence[dict[str, Any]]) -> list[Issue]:
    """Map Rust issue dicts to msgspec ``Issue`` structs."""
    out: list[Issue] = []
    for item in raw:
        out.append(
            Issue(
                severity=str(item.get("severity", "error")),
                code=str(item.get("code", "NATIVE_ISSUE")),
                message=str(item.get("message", "")),
                layer=str(item.get("layer", "xsd")),
                location=item.get("location"),
            )
        )
    return out


def _append_extended_levels(
    issues: list[Issue],
    xml_content: str,
    *,
    iwxxm_version: str,
    selected: tuple[str, ...],
) -> list[Issue]:
    """Run GML / codelist layers and merge with existing issues."""
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


def _report_from_issues(
    issues: list[Issue],
    *,
    iwxxm_version: str,
    profile: str,
) -> ValidationReport:
    ok = not any(issue.severity == "error" for issue in issues)
    return ValidationReport(
        ok=ok,
        iwxxm_version=iwxxm_version,
        profile=profile,
        issues=issues,
    )


def _validate_core_levels(
    xml_content: str,
    *,
    iwxxm_version: str,
    profile: str,
    selected: tuple[str, ...],
) -> ValidationReport:
    """Run wellformed / XSD / Schematron via Rust or lxml fallback."""
    rust_levels = [level for level in selected if level in _RUST_LEVELS]
    lxml_levels = [level for level in selected if level in _LXML_LEVELS]

    if profile == "iwxxm_us" and us_catalog_path() is None:
        return ValidationReport(
            ok=False,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=[
                Issue(
                    severity="error",
                    code="US_CATALOG_NOT_FOUND",
                    message="profile=iwxxm_us but vendor iwxxm-us catalog is missing",
                    layer="xsd",
                )
            ],
        )

    only_extended = not rust_levels and not lxml_levels
    if only_extended:
        issues = _append_extended_levels([], xml_content, iwxxm_version=iwxxm_version, selected=selected)
        return _report_from_issues(issues, iwxxm_version=iwxxm_version, profile=profile)

    if rust_available() and rust_levels:
        rust = rust_module()
        assert rust is not None
        try:
            xsd = str(xsd_path(iwxxm_version))
            sch = str(schematron_path(iwxxm_version))
        except FileNotFoundError as exc:
            return ValidationReport(
                ok=False,
                iwxxm_version=iwxxm_version,
                profile=profile,
                issues=[
                    Issue(
                        severity="error",
                        code="SCHEMA_NOT_AVAILABLE",
                        message=str(exc),
                        layer="xsd",
                    )
                ],
            )
        raw = rust.validate_document(
            xml_content,
            xsd_path=xsd,
            sch_path=sch,
            catalog_roots=_catalog_roots(iwxxm_version, profile=profile),
            levels=rust_levels,
        )
        issues = _issues_from_rust(raw)
    else:
        issues: list[Issue] = []
        if "wellformed" in selected:
            issues.extend(run_wellformed_lxml(xml_content))
        if lxml_levels and not any(i.severity == "error" for i in issues):
            lxml_report = validate(
                xml_content,
                iwxxm_version=iwxxm_version,
                profile=profile,
                levels=tuple(lxml_levels),
            )
            issues.extend(lxml_report.issues)

    merged = _append_extended_levels(issues, xml_content, iwxxm_version=iwxxm_version, selected=selected)
    return _report_from_issues(merged, iwxxm_version=iwxxm_version, profile=profile)


def validate_iwxxm(
    xml_content: str,
    *,
    iwxxm_version: str,
    profile: str = "annex3",
    levels: Sequence[str] | None = None,
    product: str | None = None,
) -> ValidationReport:
    """
    Validate IWXXM XML using the native Rust engine when available.

    Prefers ``iwxxm_validate._rust.validate_document`` (xmloxide: well-formed + XSD +
    native Schematron). Falls back to the lxml ``validate()`` path when the extension
    is not built (D-S014-T33-crates / E10-36).

    Parameters
    ----------
    xml_content :
        IWXXM XML document.
    iwxxm_version :
        Release line (e.g. ``2023-1``).
    profile :
        ``annex3`` (default), ``iwxxm_us``, or ``ca_eccc`` (MSC operational line).
    levels :
        Subset of ``wellformed``, ``xsd``, ``schematron``, ``gml``, ``codelists``.
        Default runs ``xsd`` and ``schematron``.
    product :
        API product enum for Canadian extension XSD selection when ``profile=ca_eccc``.

    Returns
    -------
    ValidationReport
        ``ok`` is ``False`` when any error-severity issue is present.
        Native Schematron does **not** emit ``SCHEMATRON_SKIPPED``.
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

    if profile == "ca_eccc":
        if ca_xsd_path() is None:
            return ValidationReport(
                ok=False,
                iwxxm_version=iwxxm_version,
                profile=profile,
                issues=[
                    Issue(
                        severity="error",
                        code="CA_SCHEMA_NOT_FOUND",
                        message="profile=ca_eccc but vendor iwxxm-ca schema pin is missing",
                        layer="xsd",
                    )
                ],
            )
        if iwxxm_version != CA_ECCC_IWXXM_VERSION:
            return ValidationReport(
                ok=False,
                iwxxm_version=iwxxm_version,
                profile=profile,
                issues=[
                    Issue(
                        severity="error",
                        code="INVALID_IWXXM_VERSION",
                        message=(
                            f"profile=ca_eccc requires iwxxm_version {CA_ECCC_IWXXM_VERSION!r}, got {iwxxm_version!r}"
                        ),
                        layer="wmo_xsd",
                    )
                ],
            )
        core_levels = tuple(level for level in selected if level in _RUST_LEVELS | _LXML_LEVELS)
        report = validate_ca_eccc_layered(
            xml_content,
            iwxxm_version=iwxxm_version,
            product=product,
            levels=core_levels or selected,
        )
        merged = _append_extended_levels(
            list(report.issues), xml_content, iwxxm_version=iwxxm_version, selected=selected
        )
        ok = not any(issue.severity == "error" for issue in merged)
        return ValidationReport(
            ok=ok,
            iwxxm_version=iwxxm_version,
            profile=profile,
            issues=merged,
            stages=report.stages,
        )

    return _validate_core_levels(
        xml_content,
        iwxxm_version=iwxxm_version,
        profile=profile,
        selected=selected,
    )


__all__ = ["validate_iwxxm"]
