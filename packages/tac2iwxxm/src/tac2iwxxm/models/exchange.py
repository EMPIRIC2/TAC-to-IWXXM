"""Exchange-output models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProfileOutputSpec:
    """
    Operator-visible exchange output fields for CA_ECCC convert.

    Attributes
    ----------
    semantic_profile : str
        Semantic profile.
    file_naming_pattern : str
        File naming pattern.
    wmo_header_designator : str
        Wmo header designator.
    distribution_path_template : str
        Distribution path template.
    iwxxm_version_pin : str
        IWXXM version pin.
    suggested_filename : str | None
        Suggested filename. Default ``None``.
    wmo_ahl_header : str | None
        Wmo AHL header. Default ``None``.
    distribution_path : str | None
        Distribution path. Default ``None``.
    translation_centre_designator : str | None
        Translation centre designator. Default ``None``.
    translation_centre_name : str | None
        Translation centre name. Default ``None``.
    """

    semantic_profile: str
    file_naming_pattern: str
    wmo_header_designator: str
    distribution_path_template: str
    iwxxm_version_pin: str
    suggested_filename: str | None = None
    wmo_ahl_header: str | None = None
    distribution_path: str | None = None
    translation_centre_designator: str | None = None
    translation_centre_name: str | None = None


@dataclass(frozen=True, slots=True)
class MscFilenameParts:
    """
    Parsed MSC datamart filename parts (owned nested-dict replacement).

    Attributes
    ----------
    tt : str
        T1T2 designator.
    aa : str
        Geographical designator.
    ii : str
        Bulletin number.
    cccc : str
        Originating centre.
    yygggg : str
        Day-hour-minute group.
    bbb : str | None
        Optional BBB.
    issuer : str
        Issuer CCCC in ``_C_`` segment.
    issued_at : str
        ``YYYYMMddhhmmss`` stamp.
    """

    tt: str
    aa: str
    ii: str
    cccc: str
    yygggg: str
    issuer: str
    issued_at: str
    bbb: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Wire-stable dict (same keys as the former nested parse result)."""
        return {
            "tt": self.tt,
            "aa": self.aa,
            "ii": self.ii,
            "cccc": self.cccc,
            "yygggg": self.yygggg,
            "bbb": self.bbb,
            "issuer": self.issuer,
            "issued_at": self.issued_at,
        }


__all__ = ["MscFilenameParts", "ProfileOutputSpec"]
