"""Library YAML schema + regex diagnostics (EVPYL Phase C).

Fail = does not compile, or required sample has no match.
Warn = compiles but looks risky (nested quantifiers, unused groups).
Activate requires zero Fail; Draft may include Fail.
"""

from __future__ import annotations

# Imports/constants consumed by exec'd part bodies.

import re

from typing import Any, cast

from tac2iwxxm.models import (
    CaptureSummary,
    LibraryLifecycle,
    LibraryYamlReport,
    RegexDiagnostic,
    RegexSeverity,
)

import yaml

from tac2iwxxm.library_assets import LIBRARY_KINDS, LibraryKind

from tac2iwxxm.numeric_checks import evaluate_numeric_check, validate_numeric_check_shape

_NESTED_QUANTIFIER = re.compile(r"[+*][?+]|\{\d+,\}\+|\{0,")

_URI_OR_SECRET = re.compile(
    r"(password|secret|token|credential|api[_-]?key|https?://|sftp://|amqps?://)",
    re.IGNORECASE,
)
