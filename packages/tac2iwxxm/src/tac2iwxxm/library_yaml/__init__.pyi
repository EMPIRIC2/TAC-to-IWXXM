"""Typing stub for exec-loaded split package (EV-tac2iwxxm-models-split)."""

from tac2iwxxm.library_assets import LibraryKind as LibraryKind
from tac2iwxxm.models import (
    CaptureSummary as CaptureSummary,
)
from tac2iwxxm.models import (
    LibraryLifecycle as LibraryLifecycle,
)
from tac2iwxxm.models import (
    LibraryYamlReport as LibraryYamlReport,
)
from tac2iwxxm.models import (
    RegexDiagnostic as RegexDiagnostic,
)

def diagnose_regex(pattern: str, *, flags: int = 0) -> RegexDiagnostic: ...
def validate_library_yaml(
    yaml_body: str,
    *,
    expected_kind: LibraryKind | None = None,
    lifecycle: LibraryLifecycle = "draft",
) -> LibraryYamlReport: ...

__all__ = [
    "CaptureSummary",
    "LibraryKind",
    "LibraryLifecycle",
    "LibraryYamlReport",
    "RegexDiagnostic",
    "diagnose_regex",
    "validate_library_yaml",
]
