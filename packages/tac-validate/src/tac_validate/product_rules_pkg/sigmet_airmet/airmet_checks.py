"""Product rules - sigmet_airmet."""
# ruff: noqa: F403, F405
# pyright: reportWildcardImportFromLibrary=false, reportUnusedFunction=false
# pyright: reportWildcardImportFromLibrary=false, reportConstantRedefinition=false, reportUnknownVariableType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportInvalidTypeForm=false, reportUnusedImport=false, reportPrivateUsage=false, reportGeneralTypeIssues=false

from __future__ import annotations

from tac_validate.models import Issue
from tac_validate.product_rules_pkg._common import *
from tac_validate.product_rules_pkg.sigmet_airmet.common_sigmet import *


def _check_airmet_a1(*, start: int, end: int, upper: str) -> list[Issue]:
    """
    Internal helper ``_check_airmet_a1``.

    Parameters
    ----------
    start : object
        Argument ``start``.
    end : object
        Argument ``end``.
    upper : object
        Argument ``upper``.

    Returns
    -------
    object
        Return value.
    """
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    seq = _AIRMET_SEQ.search(core)
    if seq is not None:
        _emit_token_info(
            issues,
            code="SIGMET_SEQUENCE",
            message="AIRMET sequence number present",
            core=core,
            body_start=start,
            body_end=end,
            token=seq.group(1),
        )
    elif _AIRMET_NO_SEQ.search(core):
        _emit_token_info(
            issues,
            code="MISSING_SEQUENCE",
            message="AIRMET missing sequence number after AIRMET",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    fir = _SIGMET_FIR_CTA.search(core)
    if fir is not None:
        _emit_token_info(
            issues,
            code="FIR_OR_CTA",
            message="AIRMET FIR/CTA/UIR airspace identity",
            core=core,
            body_start=start,
            body_end=end,
            token=fir.group(0).split("/")[0],
        )
    else:
        _emit_token_info(
            issues,
            code="MISSING_FIR_OR_CTA",
            message="AIRMET missing FIR/CTA/UIR airspace identity",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    return issues


def _check_airmet_a2(*, start: int, end: int, upper: str) -> list[Issue]:
    """
    Internal helper ``_check_airmet_a2``.

    Parameters
    ----------
    start : object
        Argument ``start``.
    end : object
        Argument ``end``.
    upper : object
        Argument ``upper``.

    Returns
    -------
    object
        Return value.
    """
    issues: list[Issue] = []
    core = upper[:-1] if upper.endswith("=") else upper

    if _SIGMET_STNR.search(core):
        if _SIGMET_MOV_STNR_ADJACENT.search(core) and not _SIGMET_MOV_DIR.search(core):
            _emit_token_info(
                issues,
                code="STNR_MOVEMENT",
                message="AIRMET STNR stationary movement",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )
        elif _SIGMET_MOV.search(core):
            _emit_token_info(
                issues,
                code="INVALID_STNR_MOVEMENT",
                message="AIRMET STNR conflicts with MOV",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )
        else:
            _emit_token_info(
                issues,
                code="STNR_MOVEMENT",
                message="AIRMET STNR stationary movement",
                core=core,
                body_start=start,
                body_end=end,
                token="STNR",
            )

    if _SIGMET_TOP_ABV_BLW.search(core):
        _emit_token_info(
            issues,
            code="TOP_ABV_OR_BLW",
            message="AIRMET TOP ABV/BLW level grammar",
            core=core,
            body_start=start,
            body_end=end,
            token="TOP",
        )

    obs = _SIGMET_OBS_FCST.search(core)
    if obs is not None:
        _emit_token_info(
            issues,
            code="OBS_OR_FCST",
            message="AIRMET OBS or FCST analysis",
            core=core,
            body_start=start,
            body_end=end,
            token=obs.group(0),
        )
    else:
        _emit_token_info(
            issues,
            code="MISSING_OBS_OR_FCST",
            message="AIRMET missing OBS or FCST",
            core=core,
            body_start=start,
            body_end=end,
            token="AIRMET",
        )

    intensity = _SIGMET_INTENSITY.search(core)
    if intensity is not None:
        _emit_token_info(
            issues,
            code="INTENSITY_CHANGE",
            message="AIRMET intensity change INTSF/WKN/NC",
            core=core,
            body_start=start,
            body_end=end,
            token=intensity.group(0),
        )

    return issues


__all__ = [
    "Issue",
    "_check_airmet_a1",
    "_check_airmet_a2",
]
