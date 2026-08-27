"""EDIS → RTH Washington sink - WMO AHL formatting + SMTP submit (F18 / E14-05).

Messages are ASCII-only with a WMO abbreviated heading (``T1T2A1A2ii CCCC YYGGgg [BBB]``).
``edis_preflight`` is connect/login only (no ``send_message``). Inject
``dissemination.transports.AiosmtpClient`` or a test double; live BYOC remains
TC-F18-002.
"""

from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol

from dissemination.allowlist import Allowlist, EgressDenied, validate_egress_host
from dissemination.models import PreflightResponse
from dissemination.redact import redact_secrets


class SmtpClient(Protocol):
    """Minimal async SMTP client used by the EDIS sink."""

    async def connect(self) -> None: ...

    async def login(self, username: str, password: str) -> None: ...

    async def send_message(self, message: EmailMessage) -> object: ...

    async def quit(self) -> None: ...


@dataclass(frozen=True, slots=True)
class EdisParams:
    """BYOC EDIS/SMTP parameters (memory-only; never logged raw)."""

    smtp_host: str
    mail_from: str
    mail_to: str
    tt: str
    aa: str
    ii: str
    cccc: str
    yygggg: str
    smtp_port: int = 587
    username: str | None = None
    password: str | None = None
    use_tls: bool = True
    bbb: str | None = None
    subject: str | None = None


@dataclass(frozen=True, slots=True)
class EdisSubmitResult:
    """Result of an EDIS SMTP submit."""

    ok: bool
    ahl: str
    detail: str | None = None


def _require_ascii(value: str, *, field: str) -> str:
    if not value.isascii():
        raise ValueError(f"EDIS {field} must be ASCII-only")
    return value


def format_wmo_ahl(
    *,
    tt: str,
    aa: str,
    ii: str,
    cccc: str,
    yygggg: str,
    bbb: str | None = None,
) -> str:
    """
    Format a WMO abbreviated heading line (Manual on the GTS / WMO-No. 386 shape).

    Thin wrapper over :func:`tac2iwxxm.format_ahl` (EV-029 / E29-T2) so BBB /
    field rules stay shared with convert.

    Parameters
    ----------
    tt, aa, ii, cccc, yygggg :
        AHL designators (``T1T2``, ``A1A2``, ``ii``, originating centre, time group).
    bbb :
        Optional BBB amendment indicator (e.g. ``CCA``).

    Returns
    -------
    str
        Single AHL line, ASCII.

    Raises
    ------
    ValueError
        When a field is non-ASCII or fails the AHL shape.
    """
    from tac2iwxxm import (
        AhlParts,
        BulletinSplitError,
        bbb_to_report_status,
        format_ahl,
        map_t1t2,
    )

    tt_u = _require_ascii(tt.strip().upper(), field="tt")
    aa_u = _require_ascii(aa.strip().upper(), field="aa")
    ii_u = _require_ascii(ii.strip().upper(), field="ii")
    cccc_u = _require_ascii(cccc.strip().upper(), field="cccc")
    yy_u = _require_ascii(yygggg.strip().upper(), field="yygggg")
    bbb_u: str | None = None
    if bbb:
        bbb_u = _require_ascii(bbb.strip().upper(), field="bbb")
    try:
        iwxxm_tt = map_t1t2(tt_u)
    except ValueError:
        iwxxm_tt = tt_u
    try:
        status = bbb_to_report_status(bbb_u)
        parts = AhlParts(
            ahl="",
            tt=tt_u,
            aa=aa_u,
            ii=ii_u,
            cccc=cccc_u,
            yygggg=yy_u,
            iwxxm_tt=iwxxm_tt,
            report_status=status,
            bbb=bbb_u,
        )
        return format_ahl(parts)
    except BulletinSplitError as exc:
        raise ValueError(exc.message) from exc


def build_edis_message(params: EdisParams, *, tac_body: str) -> str:
    """
    Build an ASCII EDIS bulletin body: AHL line, blank line, TAC text.

    Raises
    ------
    ValueError
        When any part is non-ASCII or AHL fields are invalid.
    """
    ahl = format_wmo_ahl(
        tt=params.tt,
        aa=params.aa,
        ii=params.ii,
        cccc=params.cccc,
        yygggg=params.yygggg,
        bbb=params.bbb,
    )
    body = _require_ascii(tac_body, field="tac_body").strip()
    if not body:
        raise ValueError("EDIS tac_body must be non-empty")
    return f"{ahl}\n\n{body}\n"


def _redact_exc(exc: BaseException, params: EdisParams) -> str:
    text = redact_secrets(str(exc))
    if params.password:
        text = text.replace(params.password, "REDACTED")
    if params.username:
        text = text.replace(params.username, "REDACTED")
    return text


def _validate_edis_egress(params: EdisParams, allowlist: Allowlist) -> None:
    validate_egress_host(params.smtp_host, allowlist=allowlist)


async def edis_preflight(
    params: EdisParams,
    *,
    allowlist: Allowlist,
    smtp: SmtpClient,
) -> PreflightResponse:
    """
    Check allowlist + SMTP connect/login (no message send).

    Raises
    ------
    EgressDenied
        When the SMTP host is not allowlisted.
    ValueError
        When transport checks fail (secrets redacted).
    """
    _validate_edis_egress(params, allowlist)
    try:
        await smtp.connect()
        try:
            if params.username is not None and params.password is not None:
                await smtp.login(params.username, params.password)
        finally:
            await smtp.quit()
    except Exception as exc:
        raise ValueError(_redact_exc(exc, params)) from exc
    return PreflightResponse(
        ok=True,
        connectivity_ok=True,
        diffs=[],
        detail=None,
    )


async def edis_submit(
    params: EdisParams,
    *,
    tac_body: str,
    allowlist: Allowlist,
    smtp: SmtpClient,
) -> EdisSubmitResult:
    """
    Format an ASCII EDIS message and submit via SMTP.

    Raises
    ------
    EgressDenied
        When the SMTP host is not allowlisted.
    ValueError
        When format or transport fails (secrets redacted).
    """
    _validate_edis_egress(params, allowlist)
    bulletin = build_edis_message(params, tac_body=tac_body)
    ahl = bulletin.split("\n", 1)[0]
    message = EmailMessage()
    message["From"] = _require_ascii(params.mail_from, field="mail_from")
    message["To"] = _require_ascii(params.mail_to, field="mail_to")
    subject = params.subject or f"EDIS {ahl}"
    message["Subject"] = _require_ascii(subject, field="subject")
    message.set_content(bulletin, subtype="plain", charset="us-ascii")

    try:
        await smtp.connect()
        try:
            if params.username is not None and params.password is not None:
                await smtp.login(params.username, params.password)
            await smtp.send_message(message)
        finally:
            await smtp.quit()
    except EgressDenied:
        raise
    except Exception as exc:
        raise ValueError(_redact_exc(exc, params)) from exc

    return EdisSubmitResult(ok=True, ahl=ahl, detail=None)


__all__ = [
    "EdisParams",
    "EdisSubmitResult",
    "SmtpClient",
    "build_edis_message",
    "edis_preflight",
    "edis_submit",
    "format_wmo_ahl",
]
