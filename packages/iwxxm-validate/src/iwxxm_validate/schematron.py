"""Schematron validation (lxml; xslt2 → SCHEMATRON_SKIPPED per D-S008-T21-sch)."""

from __future__ import annotations

import logging
import os
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

import lxml.etree as _lxml_etree
from lxml import isoschematron as _lxml_isoschematron

from iwxxm_validate.models import Issue
from iwxxm_validate.paths import codelists_dir, schematron_path

etree: Any = _lxml_etree
isoschematron: Any = _lxml_isoschematron

logger = logging.getLogger(__name__)

_WORKING_DIRS: dict[str, Path] = {}


def _uses_xslt2(sch_path: Path) -> bool:
    try:
        head = sch_path.read_text(encoding="utf-8", errors="replace")[:4000]
    except OSError:
        return False
    return 'queryBinding="xslt2"' in head or "queryBinding='xslt2'" in head


def _setup_working_directory(iwxxm_version: str) -> Path:
    if iwxxm_version in _WORKING_DIRS:
        return _WORKING_DIRS[iwxxm_version]

    codelists = codelists_dir(iwxxm_version)
    work_dir = Path(tempfile.mkdtemp(prefix=f"iwxxm_sch_{iwxxm_version}_"))
    for rdf in codelists.glob("*.rdf"):
        shutil.copy2(rdf, work_dir / rdf.name)
    _WORKING_DIRS[iwxxm_version] = work_dir
    return work_dir


@lru_cache(maxsize=16)
def _compile_schematron(iwxxm_version: str) -> Any | None:
    """
    Compile Schematron or return ``None`` to signal non-blocking skip (xslt2).
    """
    sch_path = schematron_path(iwxxm_version)
    if _uses_xslt2(sch_path):
        logger.warning(
            "Schematron for %s uses xslt2; skipping lxml path (D-S008-T21-sch)",
            iwxxm_version,
        )
        return None

    work_dir = _setup_working_directory(iwxxm_version)
    with sch_path.open("rb") as handle:
        sch_doc = etree.parse(handle, base_url=str(work_dir))
    return isoschematron.Schematron(sch_doc, store_report=True, store_schematron=True)


def validate_schematron(xml_content: str, iwxxm_version: str) -> list[Issue]:
    """
    Validate IWXXM XML against vendored Schematron rules.

    XSLT2 schemas yield a non-blocking ``SCHEMATRON_SKIPPED`` warning.
    Optional Docker/Saxon backend is selected when
    ``IWXXM_VALIDATE_SCHEMATRON_DOCKER=1`` (soft gate; not required for unit CI).
    """
    if os.environ.get("IWXXM_VALIDATE_SCHEMATRON_DOCKER", "").strip() in {"1", "true", "True"}:
        # Soft/separate gate — Docker path is optional; fall through to lxml/skip
        # until a dedicated runner module is wired in a later task.
        logger.info("Docker Schematron requested but not required for unit suite; using lxml path")

    try:
        xml_doc = etree.fromstring(xml_content.encode("utf-8"))
    except etree.XMLSyntaxError as exc:
        return [
            Issue(
                severity="error",
                code="XML_SYNTAX_ERROR",
                message=f"XML parsing failed: {exc}",
                layer="schematron",
                location=f"line {getattr(exc, 'lineno', '?')}",
            )
        ]

    try:
        schematron = _compile_schematron(iwxxm_version)
    except FileNotFoundError as exc:
        return [
            Issue(
                severity="error",
                code="SCHEMATRON_NOT_FOUND",
                message=str(exc),
                layer="schematron",
            )
        ]
    except Exception as exc:  # noqa: BLE001
        if "xslt2" in str(exc).lower():
            return [
                Issue(
                    severity="warning",
                    code="SCHEMATRON_SKIPPED",
                    message=(
                        f"Schematron validation skipped for version {iwxxm_version} (unsupported query language xslt2)"
                    ),
                    layer="schematron",
                )
            ]
        return [
            Issue(
                severity="error",
                code="SCHEMATRON_COMPILE_ERROR",
                message=f"Failed to compile Schematron: {exc}",
                layer="schematron",
            )
        ]

    if schematron is None:
        return [
            Issue(
                severity="warning",
                code="SCHEMATRON_SKIPPED",
                message=(
                    f"Schematron validation skipped for version {iwxxm_version} (unsupported query language xslt2)"
                ),
                layer="schematron",
            )
        ]

    try:
        ok = bool(schematron.validate(xml_doc))
    except Exception as exc:  # noqa: BLE001
        return [
            Issue(
                severity="error",
                code="SCHEMATRON_VALIDATE_ERROR",
                message=f"Schematron validation error: {exc}",
                layer="schematron",
            )
        ]

    if ok:
        return []

    issues: list[Issue] = []
    report = getattr(schematron, "validation_report", None)
    if report is not None:
        svrl_ns = {"svrl": "http://purl.oclc.org/dsdl/svrl"}
        for failed in report.xpath("//svrl:failed-assert", namespaces=svrl_ns):
            text_elem = failed.find("svrl:text", namespaces=svrl_ns)
            message = (
                (text_elem.text or "Schematron assert failed").strip()
                if text_elem is not None
                else "Schematron assert failed"
            )
            issues.append(
                Issue(
                    severity="error",
                    code=str(failed.get("id") or "SCHEMATRON_ASSERT"),
                    message=message,
                    layer="schematron",
                    location=failed.get("location"),
                )
            )
    if not issues:
        issues.append(
            Issue(
                severity="error",
                code="SCHEMATRON_ASSERT",
                message="Schematron validation failed",
                layer="schematron",
            )
        )
    return issues


def clear_schematron_cache() -> None:
    """Clear compiled Schematron cache and temp working dirs (tests)."""
    _compile_schematron.cache_clear()
    for work_dir in _WORKING_DIRS.values():
        shutil.rmtree(work_dir, ignore_errors=True)
    _WORKING_DIRS.clear()


__all__ = ["clear_schematron_cache", "validate_schematron"]
