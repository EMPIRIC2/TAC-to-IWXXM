"""TAF AerodromeCloudForecast / nil cloud emit helpers."""

from __future__ import annotations

from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3_emit._common import _CLOUD_HREF, _CLOUD_TYPE_HREF

_NIL_NSC = "http://codes.wmo.int/common/nil/nothingOfOperationalSignificance"
_NIL_NCD = "http://codes.wmo.int/common/nil/notDetectedByAutoSystem"
_NIL_NOT_OBS = "http://codes.wmo.int/common/nil/notObservable"
_NIL_INAPPLICABLE = "http://codes.wmo.int/common/nil/inapplicable"


def _nil_or_vv_cloud(fcst: dict[str, Any], *, gml_id: str) -> str | None:
    """
    Return NSC/NCD/VV cloud XML, or None when layered clouds apply.

    Parameters
    ----------
    fcst : dict[str, Any]
        Forecast IR fragment (base or change).
    gml_id : str
        ``gml:id`` for AerodromeCloudForecast when VV is emitted.

    Returns
    -------
    str | None
        Cloud XML, or ``None`` to fall through to layered emit.
    """
    if fcst.get("nsc"):
        return f'      <iwxxm:cloud nilReason="{_NIL_NSC}"/>\n'
    if fcst.get("ncd"):
        return f'      <iwxxm:cloud nilReason="{_NIL_NCD}"/>\n'
    if fcst.get("vertical_visibility_not_observable"):
        return f"""      <iwxxm:cloud>
        <iwxxm:AerodromeCloudForecast gml:id="{gml_id}">
          <iwxxm:verticalVisibility uom="N/A" xsi:nil="true" nilReason="{_NIL_NOT_OBS}"/>
        </iwxxm:AerodromeCloudForecast>
      </iwxxm:cloud>
"""
    vv_ft = fcst.get("vertical_visibility_ft")
    if vv_ft is not None:
        return f"""      <iwxxm:cloud>
        <iwxxm:AerodromeCloudForecast gml:id="{gml_id}">
          <iwxxm:verticalVisibility uom="[ft_i]">{vv_ft}</iwxxm:verticalVisibility>
        </iwxxm:AerodromeCloudForecast>
      </iwxxm:cloud>
"""
    return None


def _cloud_layers(fcst: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Collect CloudLayer dicts from forecast IR.

    Parameters
    ----------
    fcst : dict[str, Any]
        Forecast IR fragment.

    Returns
    -------
    list[dict[str, Any]]
        Layer dicts (may be empty).
    """
    clouds_raw = fcst.get("clouds")
    if isinstance(clouds_raw, list) and clouds_raw:
        return [cast(dict[str, Any], item) for item in cast(list[Any], clouds_raw) if isinstance(item, dict)]
    if fcst.get("cloud_amount") and fcst.get("cloud_base_ft") is not None:
        return [{"amount": fcst["cloud_amount"], "base_ft": fcst["cloud_base_ft"]}]
    return []


def _layer_base_xml(layer: dict[str, Any]) -> str:
    """
    Serialize CloudLayer base height (or nil).

    Parameters
    ----------
    layer : dict[str, Any]
        Single cloud layer IR.

    Returns
    -------
    str
        ``iwxxm:base`` element XML.
    """
    if layer.get("base_not_observable"):
        return f'<iwxxm:base uom="N/A" xsi:nil="true" nilReason="{_NIL_NOT_OBS}"/>'
    if layer.get("base_inapplicable") or layer.get("amount") == "SKC":
        return f'<iwxxm:base uom="N/A" xsi:nil="true" nilReason="{_NIL_INAPPLICABLE}"/>'
    return f'<iwxxm:base uom="[ft_i]">{layer["base_ft"]}</iwxxm:base>'


def _layer_xml(layer: dict[str, Any]) -> str:
    """
    Serialize one CloudLayer property.

    Parameters
    ----------
    layer : dict[str, Any]
        Single cloud layer IR.

    Returns
    -------
    str
        ``iwxxm:layer`` wrapper XML.
    """
    href = _CLOUD_HREF.format(amt=layer["amount"])
    ctype_xml = ""
    if layer.get("cloud_type"):
        thref = escape(_CLOUD_TYPE_HREF.format(ctype=str(layer["cloud_type"])))
        ctype_xml = f'\n              <iwxxm:cloudType xlink:href="{thref}"/>'
    base_xml = _layer_base_xml(layer)
    return f"""          <iwxxm:layer>
            <iwxxm:CloudLayer>
              <iwxxm:amount xlink:href="{escape(href)}"/>
              {base_xml}{ctype_xml}
            </iwxxm:CloudLayer>
          </iwxxm:layer>"""


def taf_cloud_block(fcst: dict[str, Any], *, gml_id: str) -> str:
    """
    Emit ``iwxxm:cloud`` for a TAF base/change forecast.

    NSC/NCD → element nil; VV → verticalVisibility; SKC/CLR → clear layer with
    inapplicable base; else layered FEW/SCT/BKN/OVC. Empty when none apply
    (CAVOK callers omit this block).

    Parameters
    ----------
    fcst : dict[str, Any]
        Forecast IR fragment (base or change).
    gml_id : str
        ``gml:id`` for ``AerodromeCloudForecast``.

    Returns
    -------
    str
        Cloud XML fragment, or empty string when no cloud state is present.

    Examples
    --------
    >>> "nilReason" in taf_cloud_block({"nsc": True}, gml_id="cloud.x")
    True
    """
    special = _nil_or_vv_cloud(fcst, gml_id=gml_id)
    if special is not None:
        return special
    layers = _cloud_layers(fcst)
    if not layers:
        return ""
    joined = "\n".join(_layer_xml(layer) for layer in layers)
    return f"""      <iwxxm:cloud>
        <iwxxm:AerodromeCloudForecast gml:id="{gml_id}">
{joined}
        </iwxxm:AerodromeCloudForecast>
      </iwxxm:cloud>
"""
