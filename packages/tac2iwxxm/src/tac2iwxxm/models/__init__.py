"""Data models for tac2iwxxm (msgspec / dataclass / TypedDict)."""

from __future__ import annotations

from tac2iwxxm.models.bulletin import AhlParts, BulletinMeta, BulletinSplit
from tac2iwxxm.models.conversion_template import (
    BridgeCapture,
    BridgePreview,
    BridgeSkipped,
    ConversionTemplate,
    Slot,
    SlotMode,
    SlotType,
)
from tac2iwxxm.models.convert_result import ConvertIssue, ConvertResult
from tac2iwxxm.models.emit_map import EmitMap, EmitMapError
from tac2iwxxm.models.exchange import MscFilenameParts, ProfileOutputSpec
from tac2iwxxm.models.ir import (
    ConvertIr,
    HailstoneSize,
    LatLonPoint,
    LightningSector,
    ObservedLightning,
    PolygonGeometry,
    PropagateResidualsConfig,
    SkyLevel,
    TrendGroup,
    VaLocation,
)
from tac2iwxxm.models.library_yaml import (
    CaptureSummary,
    LibraryKindName,
    LibraryLifecycle,
    LibraryYamlReport,
    RegexDiagnostic,
    RegexSeverity,
)

__all__ = [
    "AhlParts",
    "BridgeCapture",
    "BridgePreview",
    "BridgeSkipped",
    "BulletinMeta",
    "BulletinSplit",
    "CaptureSummary",
    "ConversionTemplate",
    "ConvertIr",
    "ConvertIssue",
    "ConvertResult",
    "EmitMap",
    "EmitMapError",
    "HailstoneSize",
    "LatLonPoint",
    "LibraryKindName",
    "LibraryLifecycle",
    "LibraryYamlReport",
    "LightningSector",
    "MscFilenameParts",
    "ObservedLightning",
    "PolygonGeometry",
    "ProfileOutputSpec",
    "PropagateResidualsConfig",
    "RegexDiagnostic",
    "RegexSeverity",
    "SkyLevel",
    "Slot",
    "SlotMode",
    "SlotType",
    "TrendGroup",
    "VaLocation",
]
