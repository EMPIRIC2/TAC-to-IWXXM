"""Split part body (exec'd into package namespace)."""

from __future__ import annotations


def _second_location_addendum_inner(ir: dict[str, Any]) -> str:
    """
    Internal helper ``_second_location_addendum_inner``.

    Parameters
    ----------
    ir : dict[str, Any]
        Argument ``ir``.

    Returns
    -------
    str
        Return value.
    """
    second_raw = ir.get("observed_at_second_location")
    if not isinstance(second_raw, dict):
        return ""
    second = cast(dict[str, Any], second_raw)
    attrs = ""
    if second.get("visibility_below_sensor_minimum"):
        attrs = ' visibilityBelowSensorMinimum="true"'
    parts: list[str] = [
        "          <iwxxm-us:observedAtSecondLocation>",
        f"            <iwxxm-us:ObservedAtSecondLocation{attrs}>",
    ]
    if second.get("ceiling_height_ft") is not None:
        parts.append(
            f'              <iwxxm-us:ceilingHeight uom="[ft_i]">{int(str(second["ceiling_height_ft"]))}</iwxxm-us:ceilingHeight>'
        )
    if second.get("visibility_ft") is not None:
        parts.append(
            f'              <iwxxm-us:visibility uom="[ft_i]">{int(str(second["visibility_ft"]))}</iwxxm-us:visibility>'
        )
    desc = second.get("location_description")
    if desc:
        parts.append("              <iwxxm-us:location>")
        parts.append("                <iwxxm-us:SensorLocation>")
        parts.append(f"                  <iwxxm-us:description>{escape(str(desc))}</iwxxm-us:description>")
        parts.append("                </iwxxm-us:SensorLocation>")
        parts.append("              </iwxxm-us:location>")
    parts.extend(
        [
            "            </iwxxm-us:ObservedAtSecondLocation>",
            "          </iwxxm-us:observedAtSecondLocation>",
        ]
    )
    return "\n".join(parts) + "\n"
