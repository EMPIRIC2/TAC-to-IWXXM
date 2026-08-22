"""CA_ECCC profile XML writer — Canadian METAR/SPECI/TAF (IWXXM 3.0.0 + iwxxm-ca).

Encodes MANOBS surface observations and MANAIR TAF extensions on the MSC operational
line: statute-mile visibility, inch-of-mercury altimeter (via QNH), AUTO observing
systems, Canadian REMARKS in ``iwxxm-ca:Addendum``, and non-convective low-level wind
shear (NCLWS) in TAF base forecasts.

[Corpus: product §F36] [Corpus: domain-profiles §CA_ECCC] [Corpus: adr/ADR-036]
"""

from __future__ import annotations

import re
from typing import Any, cast
from xml.sax.saxutils import escape

from tac2iwxxm.profiles.annex3 import NS, aerodrome_block, build_observation_and_trends, obs_timestamp
from tac2iwxxm.profiles.annex3_products import emit_airmet_annex3, emit_taf_annex3

CA_IWXXM_VERSION = "3.0.0"
CA_NS = "https://dd.meteo.gc.ca/today/aviation/iwxxm/"
_CODE_CA_BASE = "https://dd.weather.gc.ca/today/aviation/iwxxm/code-ca"
CA_OBS_AWOS = f"{_CODE_CA_BASE}/ObservingSystemType/AWOS"
CA_PRES_FALLING = f"{_CODE_CA_BASE}/PressureChangingRapidly/FALLING"
CA_PRES_RISING = f"{_CODE_CA_BASE}/PressureChangingRapidly/RISING"
CA_AIRMET_PHENOM_BASE = f"{_CODE_CA_BASE}/airmet_weather_phenomena"


def _ca_gml_id(ir: dict[str, Any], product: str) -> str:
    """Stable gml:id for CA_ECCC golden fixtures."""
    root = product.lower()
    station = str(ir["station"]).lower()
    if ir.get("auto"):
        return f"{root}.ca.auto.{station}"
    if ir.get("visibility_sm") is not None:
        return f"{root}.ca.vis.sm.{station}"
    if ir.get("altimeter_inhg") is not None:
        return f"{root}.ca.alt.a.{station}"
    if ir.get("pressure_change_href"):
        return f"{root}.ca.pres.{station}"
    return f"{root}.ca.basic.{station}"


def _prepare_ca_ir(ir: dict[str, Any]) -> dict[str, Any]:
    """Apply MANOBS display hints (SM visibility) without mutating the caller IR."""
    out = dict(ir)
    if out.get("cavok") or out.get("visibility_not_observable"):
        return out
    vis_sm = out.get("visibility_sm")
    if vis_sm is not None:
        out["visibility_display_uom"] = "[mi_i]"
        out["visibility_display_value"] = vis_sm
    return out


def _ca_pressure_change_href(ir: dict[str, Any]) -> str | None:
    """Map parsed PRESFR/PRESRR to MSC code-ca vocabulary."""
    href = ir.get("pressure_change_href")
    if not isinstance(href, str):
        return None
    if "FALLING" in href or "PRESFR" in href:
        return CA_PRES_FALLING
    if "RISING" in href or "PRESRR" in href:
        return CA_PRES_RISING
    return None


def _ca_observing_system_href(ir: dict[str, Any]) -> str | None:
    """Resolve Canadian observing-system vocabulary for AUTO / remarks."""
    if ir.get("auto"):
        return CA_OBS_AWOS
    return None


def _addendum_extension(ir: dict[str, Any]) -> str:
    """Serialize observation-level ``iwxxm-ca:Addendum`` for MANOBS REMARKS."""
    free_text = str(ir.get("remarks_free_text") or "").strip()
    obs_href = _ca_observing_system_href(ir)
    pres_href = _ca_pressure_change_href(ir)
    has_slp = ir.get("sea_level_pressure_hpa") is not None
    if not obs_href and not pres_href and not has_slp and not free_text:
        return ""

    parts: list[str] = [
        "      <iwxxm:extension>",
        "        <iwxxm-ca:Addendum>",
    ]
    if obs_href:
        parts.append(f'          <iwxxm-ca:observingSystemType xlink:href="{escape(obs_href)}"/>')
    if free_text:
        parts.append(f"          <iwxxm-ca:humanReadableText>{escape(free_text)}</iwxxm-ca:humanReadableText>")
    if has_slp:
        parts.append(
            f'          <iwxxm-ca:seaLevelPressure uom="hPa">{ir["sea_level_pressure_hpa"]}</iwxxm-ca:seaLevelPressure>'
        )
    if pres_href:
        parts.append(f'          <iwxxm-ca:pressureChangeIndicator xlink:href="{escape(pres_href)}"/>')
    parts.extend(
        [
            "        </iwxxm-ca:Addendum>",
            "      </iwxxm:extension>",
        ]
    )
    return "\n".join(parts) + "\n"


def _ca_taf_gml_id(ir: dict[str, Any]) -> str:
    """Stable gml:id for CA_ECCC TAF golden fixtures."""
    station = str(ir["station"]).lower()
    if ir.get("nclws"):
        return f"taf.ca.nclws.{station}"
    return f"taf.ca.basic.{station}"


def _prepare_ca_taf_ir(ir: dict[str, Any]) -> dict[str, Any]:
    """Apply MANAIR display hints (SM visibility) without mutating the caller IR."""
    out = dict(ir)
    if out.get("cavok") or out.get("visibility_not_observable"):
        return out
    vis_sm = out.get("visibility_sm")
    if vis_sm is not None:
        out["visibility_display_uom"] = "[mi_i]"
        out["visibility_display_value"] = vis_sm
    return out


def _nclws_extension(ir: dict[str, Any]) -> str:
    """Serialize ``iwxxm-ca:NonConvectiveLowLevelWindShear`` for MANAIR TAF."""
    nclws = ir.get("nclws")
    if not isinstance(nclws, dict):
        return ""
    nclws_data = cast(dict[str, Any], nclws)
    station = str(ir["station"]).lower()
    top_ft = int(nclws_data["layer_top_ft"])
    wind_dir = int(nclws_data["wind_dir_deg"])
    wind_kt = int(nclws_data["wind_speed_kt"])
    return "\n".join(
        [
            "      <iwxxm:extension>",
            f'        <iwxxm-ca:NonConvectiveLowLevelWindShear gml:id="nclws.{station}">',
            f'          <iwxxm-ca:windDirection uom="deg">{wind_dir}</iwxxm-ca:windDirection>',
            f'          <iwxxm-ca:windSpeed uom="[kn_i]">{wind_kt}</iwxxm-ca:windSpeed>',
            "          <iwxxm-ca:layerAboveAerodrome>",
            '            <iwxxm-ca:lowerLimit uom="[ft_i]">0</iwxxm-ca:lowerLimit>',
            f'            <iwxxm-ca:upperLimit uom="[ft_i]">{top_ft}</iwxxm-ca:upperLimit>',
            "          </iwxxm-ca:layerAboveAerodrome>",
            "        </iwxxm-ca:NonConvectiveLowLevelWindShear>",
            "      </iwxxm:extension>",
            "",
        ]
    )


def _inject_ca_taf_namespace(xml: str, *, iwxxm_version: str) -> str:
    """Add ``iwxxm-ca`` namespace declaration on the TAF root element."""
    needle = f'<iwxxm:TAF xmlns:iwxxm="{NS[iwxxm_version]}"'
    if needle not in xml:
        return xml
    return xml.replace(
        needle,
        f'{needle}\n    xmlns:iwxxm-ca="{CA_NS}"',
        1,
    )


def _inject_ca_taf_gml_id(xml: str, *, gml_id: str) -> str:
    """Replace annex3 default TAF gml:id with CA fixture id."""
    return re.sub(r'gml:id="taf\.[^"]+"', f'gml:id="{gml_id}"', xml, count=1)


def _ca_airmet_gml_id(ir: dict[str, Any]) -> str:
    """Stable gml:id for CA_ECCC AIRMET golden fixtures."""
    fir = str(ir["fir"]).lower()
    if ir.get("ca_gfa_phenomenon"):
        return f"airmet.ca.gfa.{fir}"
    return f"airmet.ca.basic.{fir}"


def _ca_airmet_phenomenon_href(ir: dict[str, Any]) -> str | None:
    """Map MANAIR GFA compound phenomenon to MSC code-ca vocabulary."""
    code = ir.get("ca_gfa_phenomenon")
    if not isinstance(code, str):
        return None
    return f"{CA_AIRMET_PHENOM_BASE}/{code}"


def _inject_ca_airmet_namespace(xml: str, *, iwxxm_version: str) -> str:
    """Add ``iwxxm-ca`` namespace declaration on the AIRMET root element."""
    needle = f'<iwxxm:AIRMET xmlns:iwxxm="{NS[iwxxm_version]}"'
    if needle not in xml:
        return xml
    return xml.replace(
        needle,
        f'{needle}\n    xmlns:iwxxm-ca="{CA_NS}"',
        1,
    )


def _inject_ca_airmet_gml_id(xml: str, *, gml_id: str) -> str:
    """Replace annex3 default AIRMET gml:id with CA fixture id."""
    return re.sub(r'gml:id="airmet\.[^"]+"', f'gml:id="{gml_id}"', xml, count=1)


def emit_airmet_ca_eccc(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit AIRMET IWXXM for profile ``CA_ECCC``.

    Parameters
    ----------
    ir :
        Parsed intermediate representation from ``parse_airmet``.
    iwxxm_version :
        Must be ``3.0.0`` (MSC operational line).

    Returns
    -------
    str
        IWXXM 3.0.0 XML with code-ca GFA phenomenon href when present.

    Raises
    ------
    ValueError
        When ``iwxxm_version`` is not ``3.0.0``.
    """
    if iwxxm_version != CA_IWXXM_VERSION:
        raise ValueError(f"profile ca_eccc requires iwxxm_version {CA_IWXXM_VERSION!r}, got {iwxxm_version!r}")

    xml = emit_airmet_annex3(
        ir,
        iwxxm_version=iwxxm_version,
        phenomenon_href=_ca_airmet_phenomenon_href(ir),
    )
    xml = _inject_ca_airmet_namespace(xml, iwxxm_version=iwxxm_version)
    return _inject_ca_airmet_gml_id(xml, gml_id=_ca_airmet_gml_id(ir))


def emit_taf_ca_eccc(ir: dict[str, Any], *, iwxxm_version: str) -> str:
    """
    Emit TAF IWXXM for profile ``CA_ECCC``.

    Parameters
    ----------
    ir :
        Parsed intermediate representation from ``parse_taf``.
    iwxxm_version :
        Must be ``3.0.0`` (MSC operational line).

    Returns
    -------
    str
        IWXXM 3.0.0 XML with ``iwxxm-ca`` NCLWS extension when present.

    Raises
    ------
    ValueError
        When ``iwxxm_version`` is not ``3.0.0``.
    """
    if iwxxm_version != CA_IWXXM_VERSION:
        raise ValueError(f"profile ca_eccc requires iwxxm_version {CA_IWXXM_VERSION!r}, got {iwxxm_version!r}")

    ca_ir = _prepare_ca_taf_ir(ir)
    extension = _nclws_extension(ca_ir)
    xml = emit_taf_annex3(ca_ir, iwxxm_version=iwxxm_version, forecast_extension=extension)
    xml = _inject_ca_taf_namespace(xml, iwxxm_version=iwxxm_version)
    return _inject_ca_taf_gml_id(xml, gml_id=_ca_taf_gml_id(ca_ir))


def emit_metar_speci_ca_eccc(
    ir: dict[str, Any],
    *,
    product: str,
    iwxxm_version: str,
) -> str:
    """
    Emit METAR/SPECI IWXXM for profile ``CA_ECCC``.

    Parameters
    ----------
    ir :
        Parsed intermediate representation from ``parse_metar_speci``.
    product :
        ``METAR`` or ``SPECI``.
    iwxxm_version :
        Must be ``3.0.0`` (MSC operational line).

    Returns
    -------
    str
        IWXXM 3.0.0 XML with ``iwxxm-ca`` extensions where MANOBS rules apply.

    Raises
    ------
    ValueError
        When ``iwxxm_version`` is not ``3.0.0``.
    """
    if iwxxm_version != CA_IWXXM_VERSION:
        raise ValueError(f"profile ca_eccc requires iwxxm_version {CA_IWXXM_VERSION!r}, got {iwxxm_version!r}")

    ns = NS[iwxxm_version]
    ca_ir = _prepare_ca_ir(ir)
    station = str(ca_ir["station"])
    stamp = obs_timestamp(ca_ir)
    root = product.upper()
    gml_id = _ca_gml_id(ca_ir, root)
    override = ca_ir.get("report_status")
    if override in {"NORMAL", "AMENDMENT", "CORRECTION"}:
        report_status = str(override)
    else:
        report_status = "CORRECTION" if ca_ir.get("correction") else "NORMAL"
    automated = "true" if ca_ir.get("auto") else "false"

    addendum = _addendum_extension(ca_ir)
    observation, trends = build_observation_and_trends(ca_ir, addendum_extension=addendum)
    aerodrome = aerodrome_block(station)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<iwxxm:{root} xmlns:iwxxm="{ns}"
    xmlns:iwxxm-ca="{CA_NS}"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:gml="http://www.opengis.net/gml/3.2"
    xmlns:aixm="http://www.aixm.aero/schema/5.1.1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    gml:id="{gml_id}"
    reportStatus="{report_status}"
    permissibleUsage="OPERATIONAL"
    automatedStation="{automated}">
  <iwxxm:issueTime>
    <gml:TimeInstant gml:id="t.issue">
      <gml:timePosition>{stamp}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:issueTime>
{aerodrome}  <iwxxm:observationTime>
    <gml:TimeInstant gml:id="t.obs">
      <gml:timePosition>{stamp}</gml:timePosition>
    </gml:TimeInstant>
  </iwxxm:observationTime>
{observation}{trends}</iwxxm:{root}>
"""


__all__ = [
    "CA_IWXXM_VERSION",
    "CA_NS",
    "CA_OBS_AWOS",
    "CA_PRES_FALLING",
    "CA_PRES_RISING",
    "emit_airmet_ca_eccc",
    "emit_metar_speci_ca_eccc",
    "emit_taf_ca_eccc",
]
