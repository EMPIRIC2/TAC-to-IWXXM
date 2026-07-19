"""E10-35 / F11 hard-gate helpers — soft in build (T3.5), hard at publish (T6.6)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASELINES = (
    REPO_ROOT
    / "docs"
    / "sessions"
    / "S014-package-publish-validation"
    / "reports"
    / "perf-baselines.yaml"
)

# Env flip for publish/cutover hard-fail (T6.6). Soft benches ignore this.
HARD_PERF_ENV = "IWXXM_VALIDATE_HARD_PERF"


@dataclass(frozen=True, slots=True)
class PerfBaselines:
    """Absolute p95 baselines and gate ratios from T1.3 / E10-35."""

    lib_path_ratio: float
    http_msgspec_ratio: float
    lib_path_lxml_p95_s: float
    lib_path_hard_ceiling_p95_s: float
    http_pydantic_map_p95_s: float
    http_msgspec_hard_ceiling_p95_s: float
    raw: dict[str, Any]


def load_baselines(path: Path | None = None) -> PerfBaselines:
    """
    Load committed ``perf-baselines.yaml``.

    Parameters
    ----------
    path :
        Override YAML path (tests / alternate runners).

    Returns
    -------
    PerfBaselines
        Gate ratios and absolute ceilings.
    """
    target = path or DEFAULT_BASELINES
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    gates = data["gates"]
    baselines = data["baselines_p95_s"]
    ceilings = data["ceilings_p95_s"]
    return PerfBaselines(
        lib_path_ratio=float(gates["lib_path_ratio"]),
        http_msgspec_ratio=float(gates["http_msgspec_ratio"]),
        lib_path_lxml_p95_s=float(baselines["lib_path_lxml"]),
        lib_path_hard_ceiling_p95_s=float(ceilings["lib_path_hard"]),
        http_pydantic_map_p95_s=float(baselines["http_pydantic_map"]),
        http_msgspec_hard_ceiling_p95_s=float(ceilings["http_msgspec_hard"]),
        raw=data,
    )


def hard_perf_enabled() -> bool:
    """Return True when publish hard-fail mode is on (``IWXXM_VALIDATE_HARD_PERF=1``)."""
    return os.environ.get(HARD_PERF_ENV, "").strip() in {
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
    }


@dataclass(frozen=True, slots=True)
class RatioCheck:
    """Result of comparing a candidate p95 against a baseline x ratio ceiling."""

    ok: bool
    candidate_p95_s: float
    baseline_p95_s: float
    ratio: float
    ceiling_p95_s: float
    observed_ratio: float
    label: str

    @property
    def message(self) -> str:
        """Human-readable soft/hard gate message."""
        return (
            f"{self.label}: candidate p95={self.candidate_p95_s:.6g}s "
            f"vs ceiling {self.ceiling_p95_s:.6g}s "
            f"({self.ratio:.2f}x baseline {self.baseline_p95_s:.6g}s); "
            f"observed ratio={self.observed_ratio:.3f}"
        )


def check_ratio(
    candidate_p95_s: float,
    baseline_p95_s: float,
    *,
    ratio: float,
    label: str,
) -> RatioCheck:
    """
    Compare candidate p95 to ``ratio x baseline``.

    Parameters
    ----------
    candidate_p95_s :
        Measured candidate (e.g. native ``validate_iwxxm``) p95 seconds.
    baseline_p95_s :
        Baseline (e.g. lxml) p95 seconds.
    ratio :
        Gate multiplier (0.85 for lib path).
    label :
        Name for messages.

    Returns
    -------
    RatioCheck
        ``ok`` is True when ``candidate <= ratio * baseline``.
    """
    if baseline_p95_s <= 0.0:
        msg = f"baseline must be positive, got {baseline_p95_s}"
        raise ValueError(msg)
    ceiling = ratio * baseline_p95_s
    observed = candidate_p95_s / baseline_p95_s
    return RatioCheck(
        ok=candidate_p95_s <= ceiling,
        candidate_p95_s=candidate_p95_s,
        baseline_p95_s=baseline_p95_s,
        ratio=ratio,
        ceiling_p95_s=ceiling,
        observed_ratio=observed,
        label=label,
    )


def apply_gate(check: RatioCheck, *, hard: bool | None = None) -> None:
    """
    Soft-warn or hard-fail a ratio check.

    Soft (default / build): emit ``UserWarning`` when over ceiling.
    Hard (``IWXXM_VALIDATE_HARD_PERF=1`` or ``hard=True``): ``AssertionError``.
    """
    mode_hard = hard_perf_enabled() if hard is None else hard
    if check.ok:
        return
    if mode_hard:
        raise AssertionError(f"HARD PERF: {check.message}")
    import warnings

    warnings.warn(
        f"SOFT PERF: {check.message}; hard-fail deferred to publish (E10-35/T6.6)",
        stacklevel=2,
    )
