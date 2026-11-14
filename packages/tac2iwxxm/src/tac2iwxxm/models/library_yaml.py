"""Library YAML diagnostic models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

LibraryLifecycle = Literal["draft", "activated"]
RegexSeverity = Literal["ok", "warn", "fail"]
# Mirror library_assets.LibraryKind without importing it (avoids import cycles).
LibraryKindName = Literal[
    "conversion",
    "tac_validation",
    "iwxxm_validation",
    "dissemination",
    "decoding",
]


@dataclass(frozen=True, slots=True)
class CaptureSummary:
    """One named or positional capture from a compiled pattern."""

    index: int
    name: str


@dataclass(frozen=True, slots=True)
class RegexDiagnostic:
    """Compile result for one pattern in a library YAML document."""

    path: str
    pattern: str
    severity: RegexSeverity
    message: str
    captures: tuple[CaptureSummary, ...] = ()
    sample_matched: bool | None = None


@dataclass(frozen=True, slots=True)
class LibraryYamlReport:
    """Strict YAML parse + regex diagnostics for one library asset."""

    valid_yaml: bool
    yaml_error: str | None
    kind: LibraryKindName | str | None
    name: str | None
    lifecycle: LibraryLifecycle
    diagnostics: tuple[RegexDiagnostic, ...]
    fail_count: int
    warn_count: int
    can_activate: bool
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON / API responses."""
        return {
            "valid_yaml": self.valid_yaml,
            "yaml_error": self.yaml_error,
            "kind": self.kind,
            "name": self.name,
            "lifecycle": self.lifecycle,
            "fail_count": self.fail_count,
            "warn_count": self.warn_count,
            "can_activate": self.can_activate,
            "data": dict(self.data),
            "diagnostics": [
                {
                    "path": item.path,
                    "pattern": item.pattern,
                    "severity": item.severity,
                    "message": item.message,
                    "captures": [{"index": c.index, "name": c.name} for c in item.captures],
                    "sample_matched": item.sample_matched,
                }
                for item in self.diagnostics
            ],
        }


__all__ = [
    "CaptureSummary",
    "LibraryKindName",
    "LibraryLifecycle",
    "LibraryYamlReport",
    "RegexDiagnostic",
    "RegexSeverity",
]
