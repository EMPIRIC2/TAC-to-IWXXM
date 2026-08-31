"""Layered ``ca_eccc`` validation pipeline with per-stage reporting (EV-068 M3-M4)."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import lxml.etree as _lxml_etree

from iwxxm_validate.ca_eccc_bundle import (
    CA_ECCC_IWXXM_VERSION,
    ca_eccc_catalog_roots,
    resolve_ca_eccc_bundle,
)
from iwxxm_validate.ca_eccc_layers import (
    CA_STAGE_LABELS,
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
from iwxxm_validate.ca_exchange_validate import validate_ca_exchange_packaging
from iwxxm_validate.code_ca_validate import validate_code_ca_membership
from iwxxm_validate.models import Issue, StageResult, ValidationReport
from iwxxm_validate.native import rust_available, rust_module
from iwxxm_validate.schematron import validate_schematron
from iwxxm_validate.xsd import validate_xsd, validate_xsd_at_path

CA_EXTENSION_NS = "https://dd.meteo.gc.ca/today/aviation/iwxxm/"
CA_SUBSTITUTION_ROOTS = frozenset({"LWIS", "SAWR"})
_WMO_PRODUCT_ROOTS = frozenset({"METAR", "SPECI", "TAF", "AIRMET"})
_IWXXM_NS = "http://icao.int/iwxxm/3.0"

# lxml ships without complete type stubs; bind as Any for strict basedpyright.
etree: Any = _lxml_etree

_RUST_LAYER_TO_STAGE = {
    "wellformed": STAGE_WELLFORMED,
    "xsd": STAGE_WMO_XSD,
    "schematron": STAGE_WMO_SCH,
}


def _has_error(issues: Sequence[Issue]) -> bool:
    return any(issue.severity == "error" for issue in issues)


def _remap_issues(issues: Sequence[Issue], stage_id: str) -> list[Issue]:
    return [
        Issue(
            severity=issue.severity,
            code=issue.code,
            message=issue.message,
            layer=stage_id,
            location=issue.location,
            start=issue.start,
            end=issue.end,
        )
        for issue in issues
    ]


def _stage_result(stage_id: str, issues: list[Issue]) -> StageResult:
    return StageResult(
        stage=stage_id,
        label=CA_STAGE_LABELS[stage_id],
        ok=not _has_error(issues),
        issues=issues,
    )


def _issues_from_rust(raw: Sequence[dict[str, Any]], stage_id: str) -> list[Issue]:
    issues: list[Issue] = []
    for item in raw:
        rust_layer = str(item.get("layer", "xsd"))
        mapped_stage = _RUST_LAYER_TO_STAGE.get(rust_layer, stage_id)
        issues.append(
            Issue(
                severity=str(item.get("severity", "error")),
                code=str(item.get("code", "NATIVE_ISSUE")),
                message=str(item.get("message", "")),
                layer=mapped_stage if stage_id == mapped_stage else stage_id,
                location=item.get("location"),
            )
        )
    return issues


def _run_rust_stage(
    xml_content: str,
    *,
    xsd_path: str,
    sch_path: str,
    catalog_roots: list[str],
    levels: list[str],
    stage_id: str,
) -> list[Issue]:
    rust = rust_module()
    assert rust is not None
    raw = rust.validate_document(
        xml_content,
        xsd_path=xsd_path,
        sch_path=sch_path,
        catalog_roots=catalog_roots,
        levels=levels,
    )
    return _issues_from_rust(raw, stage_id)


def _run_wellformed_lxml(xml_content: str) -> list[Issue]:
    try:
        etree.fromstring(xml_content.encode("utf-8"))
        return []
    except etree.XMLSyntaxError as exc:
        return [
            Issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML parsing failed: {exc}",
                layer=STAGE_WELLFORMED,
                location=f"line {getattr(exc, 'lineno', '?')}",
            )
        ]


def _document_root_name(xml_content: str) -> tuple[str | None, str | None]:
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError:
        return None, None
    qname = etree.QName(root)
    return qname.localname, qname.namespace


def _is_ca_substitution_root(local_name: str | None, namespace: str | None) -> bool:
    return namespace == CA_EXTENSION_NS and local_name in CA_SUBSTITUTION_ROOTS


def _extract_ca_extension_blocks(xml_content: str) -> list[str]:
    """Return serialized ``iwxxm-ca`` extension payloads from ``iwxxm:extension`` children."""
    try:
        root = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError:
        return []

    blocks: list[str] = []
    for extension in root.iter(f"{{{_IWXXM_NS}}}extension"):
        for child in extension:
            if etree.QName(child).namespace != CA_EXTENSION_NS:
                continue
            blocks.append(etree.tostring(child, encoding="unicode"))
    return blocks


def _ca_xsd_probe_document(fragment_xml: str, *, product: str) -> str:
    """
    Build a standalone document for layer-4 product XSD validation.

    ``metar-speci-ca`` declares LWIS/SAWR substitution roots; ``taf-ca`` declares
    extension elements such as ``NonConvectiveLowLevelWindShear`` only.
    """
    product_u = product.upper()
    if product_u in {"TAF", "AIRMET"}:
        return f'<?xml version="1.0" encoding="UTF-8"?>\n{fragment_xml}'
    return _wrap_ca_lwis_extension_block(fragment_xml)


def _wrap_ca_lwis_extension_block(fragment_xml: str) -> str:
    """Wrap a METAR/SPECI CA extension fragment in a minimal LWIS shell."""
    designator = "CYXX"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm-ca:LWIS xmlns:iwxxm="http://icao.int/iwxxm/3.0"
    xmlns:iwxxm-ca="{CA_EXTENSION_NS}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    gml:id="ca.extension.probe"
    reportStatus="NORMAL"
    permissibleUsage="OPERATIONAL"
    automatedStation="true">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>2023-01-01T00:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
  <iwxxm:aerodrome>
    <aixm:AirportHeliport gml:id="ad.probe">
      <aixm:timeSlice>
        <aixm:AirportHeliportTimeSlice gml:id="ad.ts.probe">
          <gml:validTime/>
          <aixm:interpretation>SNAPSHOT</aixm:interpretation>
          <aixm:designator>{designator}</aixm:designator>
          <aixm:locationIndicatorICAO>{designator}</aixm:locationIndicatorICAO>
        </aixm:AirportHeliportTimeSlice>
      </aixm:timeSlice>
    </aixm:AirportHeliport>
  </iwxxm:aerodrome>
  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>2023-01-01T00:00:00Z</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
  <iwxxm:observation>
    <iwxxm:MeteorologicalAerodromeObservation gml:id="obs.probe" cloudAndVisibilityOK="false">
      <iwxxm:extension>{fragment_xml}</iwxxm:extension>
    </iwxxm:MeteorologicalAerodromeObservation>
  </iwxxm:observation>
</iwxxm-ca:LWIS>"""


def _validate_ca_xsd_document(
    xml_content: str,
    *,
    product_xsd: Path,
    core_sch: str,
    catalog_roots: list[str],
) -> list[Issue]:
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
    local_name, namespace = _document_root_name(xml_content)

    if _is_ca_substitution_root(local_name, namespace):
        return _validate_ca_xsd_document(
            xml_content,
            product_xsd=product_xsd,
            core_sch=core_sch,
            catalog_roots=catalog_roots,
        )

    if local_name in _WMO_PRODUCT_ROOTS:
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
    xml_content :
        IWXXM XML document.
    iwxxm_version :
        Profile-pinned release line (must be ``3.0.0``).
    product :
        API product enum for layer 4 product XSD selection (``METAR``, ``TAF``, …).
    levels :
        Legacy subset of ``xsd`` / ``schematron``. ``xsd`` runs well-formed + XSD stages;
        ``schematron`` runs WMO Schematron.

    Returns
    -------
    ValidationReport
        Includes ``stages`` with operator-readable labels per EV-048.
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
        """Record one validation stage and merge its issues into the report."""
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


__all__ = ["validate_ca_eccc_layered"]
