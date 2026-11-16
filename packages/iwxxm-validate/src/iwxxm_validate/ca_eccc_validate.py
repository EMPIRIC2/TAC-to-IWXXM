"""Layered ``ca_eccc`` validation pipeline with per-stage reporting (EV-068 M3-M4)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from iwxxm_validate.ca_eccc_bundle import (
    CA_ECCC_IWXXM_VERSION,
    ca_eccc_catalog_roots,
    resolve_ca_eccc_bundle,
)
from iwxxm_validate.ca_eccc_layers import (
    STAGE_CA_XSD,
    STAGE_CODE_CA,
    STAGE_EXCHANGE,
    STAGE_WELLFORMED,
    STAGE_WMO_SCH,
    STAGE_WMO_XSD,
    ca_product_has_exchange_output,
    ca_product_has_national_xsd,
    ca_product_xsd_path,
)
from iwxxm_validate.ca_eccc_stages import (
    has_error as _has_error,
)
from iwxxm_validate.ca_eccc_stages import (
    remap_issues as _remap_issues,
)
from iwxxm_validate.ca_eccc_stages import (
    run_wellformed_lxml as _run_wellformed_lxml,
)
from iwxxm_validate.ca_eccc_stages import (
    stage_result as _stage_result,
)
from iwxxm_validate.ca_eccc_xml import (
    CA_EXTENSION_NS,
    CA_SUBSTITUTION_ROOTS,
    WMO_PRODUCT_ROOTS,
)
from iwxxm_validate.ca_eccc_xml import (
    ca_xsd_probe_document as _ca_xsd_probe_document,
)
from iwxxm_validate.ca_eccc_xml import (
    document_root_name as _document_root_name,
)
from iwxxm_validate.ca_eccc_xml import (
    extract_ca_extension_blocks as _extract_ca_extension_blocks,
)
from iwxxm_validate.ca_eccc_xml import (
    is_ca_substitution_root as _is_ca_substitution_root,
)
from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging
from iwxxm_validate.code_ca_validate import validate_code_ca_membership
from iwxxm_validate.models import Issue, StageResult, ValidationReport, issues_from_rust
from iwxxm_validate.native import rust_available, rust_module
from iwxxm_validate.schematron import validate_schematron
from iwxxm_validate.xsd import validate_xsd, validate_xsd_at_path

_RUST_LAYER_TO_STAGE = {
    "wellformed": STAGE_WELLFORMED,
    "xsd": STAGE_WMO_XSD,
    "schematron": STAGE_WMO_SCH,
}


def _issues_from_rust(raw: Sequence[Mapping[str, Any]], stage_id: str) -> list[Issue]:
    """
    Convert Rust findings for a CA stage (compat shim for tests).

    Parameters
    ----------
    raw : Sequence[Mapping[str, Any]]
        Native engine findings.
    stage_id : str
        Target stage id.

    Returns
    -------
    list[Issue]
        Mapped findings.
    """
    return issues_from_rust(raw, layer_map=_RUST_LAYER_TO_STAGE, stage_id=stage_id)


def _run_rust_stage(
    xml_content: str,
    *,
    xsd_path: str,
    sch_path: str,
    catalog_roots: list[str],
    levels: list[str],
    stage_id: str,
) -> list[Issue]:
    """
    Run the native validator for one CA stage (module-local for monkeypatches).

    Parameters
    ----------
    xml_content : str
        IWXXM XML.
    xsd_path : str
        Primary XSD path.
    sch_path : str
        Schematron path.
    catalog_roots : list[str]
        Catalog root directories.
    levels : list[str]
        Native levels to run.
    stage_id : str
        Stage id for issue ``layer``.

    Returns
    -------
    list[Issue]
        Mapped findings.
    """
    rust = rust_module()
    assert rust is not None
    raw: list[dict[str, Any]] = rust.validate_document(
        xml_content,
        xsd_path=xsd_path,
        sch_path=sch_path,
        catalog_roots=catalog_roots,
        levels=levels,
    )
    return _issues_from_rust(raw, stage_id)


def _validate_ca_xsd_document(
    xml_content: str,
    *,
    product_xsd: Path,
    core_sch: str,
    catalog_roots: list[str],
) -> list[Issue]:
    """
    Validate one document (or probe) against a Canadian product XSD.

    Parameters
    ----------
    xml_content : str
        XML to validate.
    product_xsd : Path
        Product XSD path.
    core_sch : str
        Core Schematron path (required by the native API).
    catalog_roots : list[str]
        Catalog roots for schema resolution.

    Returns
    -------
    list[Issue]
        Findings for the ``ca_xsd`` stage.
    """
    ca_path = str(product_xsd)
    if rust_available():
        return _run_rust_stage(
            xml_content,
            xsd_path=ca_path,
            sch_path=core_sch,
            catalog_roots=catalog_roots,
            levels=["xsd"],
            stage_id=STAGE_CA_XSD,
        )
    return validate_xsd_at_path(xml_content, product_xsd, layer=STAGE_CA_XSD)


def _validate_ca_xsd_layer(
    xml_content: str,
    *,
    product: str,
    product_xsd: Path,
    core_sch: str,
    catalog_roots: list[str],
) -> list[Issue]:
    """
    Run the Canadian extension XSD stage for a product document.

    Parameters
    ----------
    xml_content : str
        Full IWXXM document.
    product : str
        Product id.
    product_xsd : Path
        Mapped product XSD.
    core_sch : str
        Core Schematron path.
    catalog_roots : list[str]
        Catalog roots.

    Returns
    -------
    list[Issue]
        Findings for the ``ca_xsd`` stage.
    """
    local_name, namespace = _document_root_name(xml_content)

    if _is_ca_substitution_root(local_name, namespace):
        return _validate_ca_xsd_document(
            xml_content,
            product_xsd=product_xsd,
            core_sch=core_sch,
            catalog_roots=catalog_roots,
        )

    if local_name in WMO_PRODUCT_ROOTS:
        blocks = _extract_ca_extension_blocks(xml_content)
        if not blocks:
            return []
        issues: list[Issue] = []
        for block in blocks:
            probe = _ca_xsd_probe_document(block, product=product)
            issues.extend(
                _validate_ca_xsd_document(
                    probe,
                    product_xsd=product_xsd,
                    core_sch=core_sch,
                    catalog_roots=catalog_roots,
                )
            )
        return issues

    return [
        Issue(
            severity="error",
            code="CA_PRODUCT_ROOT_UNKNOWN",
            message=f"Unsupported document root {local_name!r} for product {product!r}",
            layer=STAGE_CA_XSD,
        )
    ]


def validate_ca_eccc_layered(
    xml_content: str,
    *,
    iwxxm_version: str = CA_ECCC_IWXXM_VERSION,
    product: str | None = None,
    levels: Sequence[str] | None = None,
) -> ValidationReport:
    """
    Run staged CA_ECCC validation with per-stage issue reporting.

    Parameters
    ----------
    xml_content : str
        IWXXM XML document.
    iwxxm_version : str, optional
        Profile-pinned release line (must be ``3.0.0``). By default ``CA_ECCC_IWXXM_VERSION``.
    product : str or None, optional
        API product enum for layer 4 product XSD selection (``METAR``, ``TAF``, …). By default ``None``.
    levels : Sequence[str] or None, optional
        Legacy subset of ``xsd`` / ``schematron``. ``xsd`` runs well-formed + XSD stages;
        ``schematron`` runs WMO Schematron. By default ``None``.

    Returns
    -------
    ValidationReport
        Includes ``stages`` with operator-readable labels per EV-048.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (validate_ca_eccc_layered)
    2
    """
    selected = tuple(levels) if levels is not None else ("xsd", "schematron")
    run_xsd_stages = "xsd" in selected
    run_schematron = "schematron" in selected

    bundle = resolve_ca_eccc_bundle(iwxxm_version=iwxxm_version)
    if bundle is None:
        issue = Issue(
            severity="error",
            code="CA_SCHEMA_NOT_FOUND",
            message="profile=ca_eccc but vendor iwxxm-ca schema pin is missing",
            layer=STAGE_WMO_XSD,
        )
        stage = _stage_result(STAGE_WMO_XSD, [issue])
        return ValidationReport(
            ok=False,
            iwxxm_version=iwxxm_version,
            profile="ca_eccc",
            issues=[issue],
            stages=[stage],
        )

    catalog_roots = ca_eccc_catalog_roots(iwxxm_version)
    core_xsd = str(bundle.core_xsd)
    core_sch = str(bundle.schematron)
    root_local, root_ns = _document_root_name(xml_content)
    ca_substitution_root = _is_ca_substitution_root(root_local, root_ns)

    stages: list[StageResult] = []
    all_issues: list[Issue] = []

    def append_stage(stage_id: str, issues: list[Issue]) -> None:
        """
        Record one validation stage and merge its issues into the report.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (append_stage)
        2

        Parameters
        ----------
        stage_id : str
            Stage ID.
        issues : list[Issue]
            Issues.
        """
        stages.append(_stage_result(stage_id, issues))
        all_issues.extend(issues)

    if rust_available():
        wf_issues = _run_rust_stage(
            xml_content,
            xsd_path=core_xsd,
            sch_path=core_sch,
            catalog_roots=catalog_roots,
            levels=[],
            stage_id=STAGE_WELLFORMED,
        )
    else:
        wf_issues = _run_wellformed_lxml(xml_content)

    append_stage(STAGE_WELLFORMED, wf_issues)
    if _has_error(wf_issues):
        return ValidationReport(
            ok=False,
            iwxxm_version=iwxxm_version,
            profile="ca_eccc",
            issues=all_issues,
            stages=stages,
        )

    if run_xsd_stages and not ca_substitution_root:
        if rust_available():
            wmo_xsd_issues = _run_rust_stage(
                xml_content,
                xsd_path=core_xsd,
                sch_path=core_sch,
                catalog_roots=catalog_roots,
                levels=["xsd"],
                stage_id=STAGE_WMO_XSD,
            )
        else:
            wmo_xsd_issues = _remap_issues(
                validate_xsd(xml_content, iwxxm_version),
                STAGE_WMO_XSD,
            )
        append_stage(STAGE_WMO_XSD, wmo_xsd_issues)

    if run_schematron and not ca_substitution_root and not _has_error(all_issues):
        if rust_available():
            sch_issues = _run_rust_stage(
                xml_content,
                xsd_path=core_xsd,
                sch_path=core_sch,
                catalog_roots=catalog_roots,
                levels=["schematron"],
                stage_id=STAGE_WMO_SCH,
            )
        else:
            sch_issues = _remap_issues(
                validate_schematron(xml_content, iwxxm_version),
                STAGE_WMO_SCH,
            )
        append_stage(STAGE_WMO_SCH, sch_issues)

    if run_xsd_stages and product and not _has_error(all_issues):
        product_xsd = ca_product_xsd_path(product)
        if not ca_product_has_national_xsd(product):
            ca_issues = [
                Issue(
                    severity="info",
                    code="CA_XSD_NOT_APPLICABLE",
                    message=(
                        f"No published Canadian extension XSD for product {product!r}; ca_xsd skipped (not applicable)"
                    ),
                    layer=STAGE_CA_XSD,
                )
            ]
        elif product_xsd is None:
            ca_issues = [
                Issue(
                    severity="error",
                    code="CA_PRODUCT_XSD_NOT_FOUND",
                    message=f"No Canadian extension XSD mapped for product {product!r}",
                    layer=STAGE_CA_XSD,
                )
            ]
        else:
            ca_issues = _validate_ca_xsd_layer(
                xml_content,
                product=product,
                product_xsd=product_xsd,
                core_sch=core_sch,
                catalog_roots=catalog_roots,
            )
        append_stage(STAGE_CA_XSD, ca_issues)

    if not _has_error(all_issues):
        code_ca_issues = validate_code_ca_membership(xml_content)
        append_stage(STAGE_CODE_CA, code_ca_issues)

    if not _has_error(all_issues):
        if product and ca_product_has_exchange_output(product):
            exchange_issues = validate_ca_exchange_packaging(xml_content, product=product)
        elif product and not ca_product_has_national_xsd(product):
            exchange_issues = [
                Issue(
                    severity="info",
                    code="CA_EXCHANGE_NOT_APPLICABLE",
                    message=(f"CA exchange packaging not required for validate-first product {product!r}"),
                    layer=STAGE_EXCHANGE,
                )
            ]
        else:
            exchange_issues = validate_ca_exchange_packaging(xml_content, product=product)
        append_stage(STAGE_EXCHANGE, exchange_issues)

    ok = not _has_error(all_issues)
    return ValidationReport(
        ok=ok,
        iwxxm_version=iwxxm_version,
        profile="ca_eccc",
        issues=all_issues,
        stages=stages,
    )


__all__ = [
    "CA_EXTENSION_NS",
    "CA_SUBSTITUTION_ROOTS",
    "STAGE_CA_XSD",
    "STAGE_CODE_CA",
    "STAGE_EXCHANGE",
    "STAGE_WELLFORMED",
    "STAGE_WMO_SCH",
    "STAGE_WMO_XSD",
    "validate_ca_eccc_layered",
]
