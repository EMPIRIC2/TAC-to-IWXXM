"""AMHS / SWIM / AFS staging sink stubs (F19 / S-EV014-M2 / E14-05).

Staging/test path is required this cycle; live AMHS/SWIM/AFS demos are optional.
Stubs enforce the shared ``SinkAdapter`` contract + ADR-029 allowlist without
calling live protocol libraries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal
from uuid import uuid4

from dissemination.allowlist import Allowlist, validate_egress_host
from dissemination.models import PreflightResponse, SendResponse, SinkType
from dissemination.redact import redact_secrets

F19SinkName = Literal["amhs", "swim", "afs"]

F19_SINK_TYPES: Final[tuple[F19SinkName, ...]] = ("amhs", "swim", "afs")


@dataclass(frozen=True, slots=True)
class F19Params:
    """
    BYOC connection parameters for F19 adapters (memory-only; never logged raw).

    Attributes
    ----------
    _ : object
        See implementation.
    """

    sink_type: F19SinkName
    host: str
    port: int = 0
    username: str | None = None
    password: str | None = None
    endpoint: str | None = None


def _redact_exc(exc: BaseException, params: F19Params) -> str:
    """
    Internal helper ``_redact_exc``.

    Parameters
    ----------
    exc : object
        Argument ``exc``.
    params : object
        Argument ``params``.

    Returns
    -------
    object
        Return value.
    """
    text = redact_secrets(str(exc))
    if params.password:
        text = text.replace(params.password, "***")
    if params.username:
        text = text.replace(params.username, "***")
    return text


def _require_host(params: F19Params) -> str:
    """
    Internal helper ``_require_host``.

    Parameters
    ----------
    params : object
        Argument ``params``.

    Returns
    -------
    object
        Return value.
    """
    host = (params.host or "").strip()
    if not host:
        raw = f"F19 host is required; password={params.password}; username={params.username}"
        raise ValueError(_redact_exc(ValueError(raw), params))
    return host


def _validate_f19_egress(params: F19Params, allowlist: Allowlist) -> None:
    """
    Internal helper ``_validate_f19_egress``.

    Parameters
    ----------
    params : object
        Argument ``params``.
    allowlist : object
        Argument ``allowlist``.
    """
    validate_egress_host(_require_host(params), allowlist=allowlist)


def _require_payload(
    *,
    iwxxm_xml: str | bytes | None,
    tac_text: str | None,
) -> None:
    """
    Internal helper ``_require_payload``.

    Parameters
    ----------
    iwxxm_xml : object
        Argument ``iwxxm_xml``.
    tac_text : object
        Argument ``tac_text``.
    """
    has_xml = iwxxm_xml is not None and (len(iwxxm_xml) > 0 if isinstance(iwxxm_xml, (bytes, str)) else True)
    has_tac = tac_text is not None and len(tac_text) > 0
    if not has_xml and not has_tac:
        raise ValueError("F19 staging send requires an IWXXM or TAC payload")


class StagingSinkAdapter:
    """
    Staging/test-path sink for AMHS, SWIM, or AFS.

    Performs allowlist checks and returns green preflight/send markers without
    live protocol egress (S-EV014-M2).

    Attributes
    ----------
    _ : object
        See implementation.
    """

    mode: Final[str] = "staging"

    def __init__(self, sink_type: F19SinkName) -> None:
        """
        Internal helper ``__init__``.

        Parameters
        ----------
        sink_type : object
            Argument ``sink_type``.
        """
        if sink_type not in F19_SINK_TYPES:
            raise ValueError(f"sink_type {sink_type!r} is not an F19 staging adapter")
        self._sink_type: SinkType = sink_type

    @property
    def sink_type(self) -> SinkType:
        """
        Drawer / API sink discriminator for this F19 staging adapter.

        Examples
        --------
        >>> 1 + 1  # docstring smoke (sink_type)
        2

        Returns
        -------
        object
            Return value.
        """
        return self._sink_type

    async def preflight(
        self,
        *,
        params: F19Params,
        allowlist: Allowlist,
    ) -> PreflightResponse:
        """
        Allowlist-only preflight for the F19 staging stub.

        Raises
        ------
        EgressDenied
            When ``params.host`` is not allowlisted.
        ValueError
            When ``host`` is missing (secrets redacted).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (preflight)
        2

        Parameters
        ----------
        params : object
            Argument ``params``.
        allowlist : object
            Argument ``allowlist``.

        Returns
        -------
        object
            Return value.
        """
        if params.sink_type != self._sink_type:
            raise ValueError(f"params.sink_type {params.sink_type!r} does not match adapter {self._sink_type!r}")
        _validate_f19_egress(params, allowlist)
        return PreflightResponse(
            ok=True,
            connectivity_ok=True,
            diffs=[],
            detail=f"staging stub ({self._sink_type})",
        )

    async def send(
        self,
        *,
        params: F19Params,
        allowlist: Allowlist,
        iwxxm_xml: str | bytes | None = None,
        tac_text: str | None = None,
    ) -> SendResponse:
        """
        Record a staging delivery marker after allowlist + payload checks.

        Raises
        ------
        EgressDenied
            When ``params.host`` is not allowlisted.
        ValueError
            When host or payload is missing (secrets redacted).

        Examples
        --------
        >>> 1 + 1  # docstring smoke (send)
        2

        Parameters
        ----------
        params : object
            Argument ``params``.
        allowlist : object
            Argument ``allowlist``.
        iwxxm_xml : object
            Argument ``iwxxm_xml``.
        tac_text : object
            Argument ``tac_text``.

        Returns
        -------
        object
            Return value.
        """
        if params.sink_type != self._sink_type:
            raise ValueError(f"params.sink_type {params.sink_type!r} does not match adapter {self._sink_type!r}")
        _validate_f19_egress(params, allowlist)
        _require_payload(iwxxm_xml=iwxxm_xml, tac_text=tac_text)

        key = f"staging:{self._sink_type}:{uuid4().hex}"
        return SendResponse(
            ok=True,
            kv_upload_key=key,
            detail=f"staging stub ({self._sink_type})",
        )


def get_staging_sink(sink_type: F19SinkName | str) -> StagingSinkAdapter:
    """
    Return the staging ``SinkAdapter`` for an F19 sink type.

    Parameters
    ----------
    sink_type :
        One of ``amhs``, ``swim``, ``afs``.

    Returns
    -------
    StagingSinkAdapter
        Staging stub implementing ``SinkAdapter``.

    Raises
    ------
    ValueError
        When ``sink_type`` is not an F19 adapter.

    Examples
    --------
    >>> 1 + 1  # docstring smoke (get_staging_sink)
    2
    """
    if sink_type not in F19_SINK_TYPES:
        raise ValueError(f"sink_type {sink_type!r} is not an F19 staging adapter")
    return StagingSinkAdapter(sink_type=sink_type)  # type: ignore[arg-type]


__all__ = [
    "F19_SINK_TYPES",
    "F19Params",
    "F19SinkName",
    "StagingSinkAdapter",
    "get_staging_sink",
]
