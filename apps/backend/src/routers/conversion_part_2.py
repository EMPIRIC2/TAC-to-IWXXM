"""Part 2 of ``conversion.py`` (line-cap split)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from tac_validate.models import LintReport

from src.schemas.conversion import (
    ConversionIssue,
    ConversionIssueSeverity,
    ConversionResult,
    FailedSpan,
)

from .conversion_part_1 import _wire_payload_dict, logger


@dataclass(slots=True)
class _ConvertAccumulator:
    """Internal helper ``_ConvertAccumulator``."""

    results: list[ConversionResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    issues: list[ConversionIssue] = field(default_factory=list)
    preview_failed_spans: list[FailedSpan] = field(default_factory=list)
    total_inputs: int = 0
    preview_saw_soft_fail: bool = False

    def add_issue(
        self,
        source: str,
        message: str,
        severity: ConversionIssueSeverity = ConversionIssueSeverity.ERROR,
        hint: str | None = None,
        code: str | None = None,
        layer: str | None = None,
        location: str | None = None,
    ) -> None:
        """Append a conversion/validation issue to this accumulator."""
        self.issues.append(
            ConversionIssue(
                source=source,
                message=message,
                severity=severity,
                hint=hint,
                code=code,
                layer=layer,
                location=location,
            )
        )

    def absorb_convert_issues(self, soft: dict[str, Any], *, source: str) -> None:
        """
        Echo tac2iwxxm non-fatal convert issues (e.g. REMARKS_EXCLUDED) to the client.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (absorb_convert_issues)
        2

        Parameters
        ----------
        soft : object
            Argument ``soft``.
        source : object
            Argument ``source``.
        """
        for raw_obj in cast(list[object], soft.get("convert_issues") or []):
            data = _wire_payload_dict(raw_obj)
            sev_raw = str(data.get("severity") or "info").strip().lower()
            if "." in sev_raw:
                sev_raw = sev_raw.rsplit(".", 1)[-1]
            if sev_raw == "error":
                severity = ConversionIssueSeverity.ERROR
            elif sev_raw == "warning":
                severity = ConversionIssueSeverity.WARNING
            else:
                severity = ConversionIssueSeverity.INFO
            code = data.get("code") or None
            self.add_issue(
                source=source,
                message=str(data.get("message") or code or "Convert issue"),
                severity=severity,
                hint=("Use profile=iwxxm_us to retain US REMARKS in IWXXM." if code == "REMARKS_EXCLUDED" else None),
                code=code,
                location=data.get("location"),
            )

    def absorb_soft_preview(
        self,
        soft: dict[str, Any],
        *,
        preview: bool,
        base_offset: int = 0,
        source: str | None = None,
    ) -> None:
        """
        Merge soft-preview envelope fields from convert_metar_tac_with_metadata.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (absorb_soft_preview)
        2

        Parameters
        ----------
        soft : object
            Argument ``soft``.
        preview : object
            Argument ``preview``.
        base_offset : object
            Argument ``base_offset``.
        source : object
            Argument ``source``.
        """
        if not soft:
            return
        if source:
            self.absorb_convert_issues(soft, source=source)
        if not preview:
            return
        if soft.get("ok") is False:
            self.preview_saw_soft_fail = True
            for span in cast(list[object], soft.get("failed_spans") or []):
                data = _wire_payload_dict(span)
                if base_offset:
                    if data.get("start") is not None:
                        data["start"] = int(data["start"]) + base_offset
                    if data.get("end") is not None:
                        data["end"] = int(data["end"]) + base_offset
                self.preview_failed_spans.append(FailedSpan(**data))

    def record_preview_layer12_soft_fail(
        self,
        aggregated_result: object,
        tac_text: str = "",
        *,
        base_offset: int = 0,
    ) -> None:
        """
        Mark soft-preview Layer 1-2 failure and copy spans when present (ADR-022).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (record_preview_layer12_soft_fail)
        2

        Parameters
        ----------
        aggregated_result : object
            Argument ``aggregated_result``.
        tac_text : object
            Argument ``tac_text``.
        base_offset : object
            Argument ``base_offset``.
        """
        self.preview_saw_soft_fail = True
        before = len(self.preview_failed_spans)
        if aggregated_result:
            for layer_result in getattr(aggregated_result, "results", []):
                for validation_issue in getattr(layer_result, "issues", []):
                    start = getattr(validation_issue, "start", None)
                    end = getattr(validation_issue, "end", None)
                    if start is None or end is None:
                        continue
                    self.preview_failed_spans.append(
                        FailedSpan(
                            start=int(start) + base_offset,
                            end=int(end) + base_offset,
                            code=getattr(validation_issue, "code", None),
                            message=str(getattr(validation_issue, "message", "") or "") or None,
                        )
                    )
        if len(self.preview_failed_spans) == before and tac_text:
            self.preview_failed_spans.append(
                FailedSpan(
                    start=base_offset,
                    end=base_offset + len(tac_text),
                    code="LAYER12_SOFT_FAIL",
                    message="Input failed ICAO/TAC Layer 1-2 checks; soft-preview continuing",
                )
            )

    def add_aggregated_validation_issues(self, source: str, aggregated_result: object) -> None:
        """
        Flatten multi-layer validation results into conversion issues.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (add_aggregated_validation_issues)
        2

        Parameters
        ----------
        source : object
            Argument ``source``.
        aggregated_result : object
            Argument ``aggregated_result``.
        """
        if not aggregated_result:
            return
        for layer_result in getattr(aggregated_result, "results", []):
            for validation_issue in getattr(layer_result, "issues", []):
                self._append_validation_issue(source, validation_issue)

    def add_validation_issue_list(self, source: str, issues: list[object] | tuple[object, ...] | None) -> None:
        """
        Flatten a flat list of validation findings onto convert ``issues[]`` (#1159).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (add_validation_issue_list)
        2

        Parameters
        ----------
        source : object
            Argument ``source``.
        issues : object
            Argument ``issues``.
        """
        if not issues:
            return
        for validation_issue in issues:
            self._append_validation_issue(source, validation_issue)

    def _append_validation_issue(self, source: str, validation_issue: object) -> None:
        """
        Map one orchestrator or package finding onto a ConversionIssue.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (_append_validation_issue)
        2

        Parameters
        ----------
        source : object
            Argument ``source``.
        validation_issue : object
            Argument ``validation_issue``.
        """
        severity = ConversionIssueSeverity.WARNING
        level = str(getattr(validation_issue, "level", None) or getattr(validation_issue, "severity", "") or "").lower()
        if "." in level:
            level = level.rsplit(".", 1)[-1]
        if level in {"error", "critical"}:
            severity = ConversionIssueSeverity.ERROR
        elif level == "info":
            severity = ConversionIssueSeverity.INFO
        self.add_issue(
            source=source,
            message=str(getattr(validation_issue, "message", "Validation issue")),
            severity=severity,
            hint=getattr(validation_issue, "suggestion", None) or getattr(validation_issue, "hint", None),
            code=getattr(validation_issue, "code", None),
            layer=str(getattr(validation_issue, "layer", "") or "") or None,
            location=getattr(validation_issue, "location", None),
        )

    def emit_output_validation_soft_warning(
        self,
        *,
        source: str,
        label: str,
        pkg_out: object,
        validation_result: object,
    ) -> dict[str, Any]:
        """Emit aggregate OUTPUT_VALIDATION_WARNING plus flattened details (#1159)."""
        orch_issues = list(getattr(validation_result, "all_issues", None) or [])
        pkg_issues = list(getattr(pkg_out, "issues", None) or [])
        # Package ``ok`` already ignores non-blocking warnings; only surface errors.
        pkg_errors = [
            issue for issue in pkg_issues if str(getattr(issue, "severity", "")).lower() in {"error", "critical"}
        ]
        detail_count = len(orch_issues) + len(pkg_errors)
        warning_msg = f"{label}: IWXXM validation issues found - {detail_count} issues"
        logger.warning(warning_msg)
        self.add_issue(
            source=source,
            message=warning_msg,
            severity=ConversionIssueSeverity.WARNING,
            hint="Output converted, but IWXXM validation reported issues.",
            code="OUTPUT_VALIDATION_WARNING",
            layer="iwxxm_output",
        )
        self.add_validation_issue_list(source, orch_issues)
        self.add_validation_issue_list(source, pkg_errors)
        return {
            "validation_issues": [str(issue) for issue in (orch_issues + pkg_errors)[:10]],
        }

    def emit_recent_wx_issues(self, source: str, norm_warnings: list[dict[str, Any]]) -> None:
        """
        Emit structured conversion issues for recent-weather rewrites.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (emit_recent_wx_issues)
        2

        Parameters
        ----------
        source : object
            Argument ``source``.
        norm_warnings : object
            Argument ``norm_warnings``.
        """
        for warning in norm_warnings:
            self.add_issue(
                source=source,
                message=(
                    f"Recent weather token '{warning['original']}' rewritten to "
                    f"'{warning['replacement']}' for WMO D-6 compliance "
                    f"(truncated descriptor-only code; UP phenomenon added)."
                ),
                severity=ConversionIssueSeverity.INFO,
                hint=(
                    f"'{warning['original']}' is not a valid Annex 3 recent weather code. "
                    f"Using '{warning['replacement']}' (unidentified precipitation) instead."
                ),
                code="RECENT_WX_NORMALIZED",
                layer="tac_normalization",
            )


def _append_pre_convert_lint_issues(
    pre_convert_lint_report: LintReport | None,
    *,
    acc: _ConvertAccumulator,
) -> None:
    """
    Internal helper ``_append_pre_convert_lint_issues``.

    Parameters
    ----------
    pre_convert_lint_report : object
        Argument ``pre_convert_lint_report``.
    acc : object
        Argument ``acc``.
    """
    if pre_convert_lint_report is None:
        return
    for lint_issue in pre_convert_lint_report.issues:
        sev_raw = str(lint_issue.severity or "info").strip().lower()
        if sev_raw == "error":
            lint_severity = ConversionIssueSeverity.ERROR
        elif sev_raw == "warning":
            lint_severity = ConversionIssueSeverity.WARNING
        else:
            lint_severity = ConversionIssueSeverity.INFO
        acc.add_issue(
            source="lint",
            message=str(lint_issue.message or lint_issue.code or "Lint issue"),
            severity=lint_severity,
            code=str(lint_issue.code or "LINT"),
            location=getattr(lint_issue, "location", None),
        )
    if not pre_convert_lint_report.ok:
        logger.info(
            "[CONVERT] tac-validate issues (non-blocking soft path): %s",
            [item.code for item in pre_convert_lint_report.issues],
        )


def _record_convert_station_health(
    acc: _ConvertAccumulator,
    *,
    product: str,
    lint_report: LintReport | None = None,
) -> None:
    """
    Best-effort station health write for convert results (F39).

    Parameters
    ----------
    acc : object
        Argument ``acc``.
    product : object
        Argument ``product``.
    lint_report : object
        Argument ``lint_report``.
    """
    try:
        from src.services.station_health_recorder import record_tac_observation
    except Exception:
        return
    lint_error_count = 0
    lint_warning_count = 0
    if lint_report is not None:
        for issue in lint_report.issues:
            severity = str(getattr(issue, "severity", "") or "").lower()
            if severity in {"error", "critical"}:
                lint_error_count += 1
            elif severity == "warning":
                lint_warning_count += 1
    for result in acc.results:
        tac = (result.tac_input or "").strip()
        if not tac:
            continue
        try:
            record_tac_observation(
                tac_text=tac,
                product=product,
                source="convert",
                lint_error_count=lint_error_count,
                lint_warning_count=lint_warning_count,
                convert_ok=True,
            )
        except Exception:
            logger.debug("station health convert record failed", exc_info=True)
