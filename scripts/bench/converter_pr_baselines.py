"""EV-047 / #834 — converter PR hard-gate baseline load + measure helpers."""

from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASELINES = REPO_ROOT / "tests" / "perf" / "baselines" / "converter_pr.yaml"


@dataclass(frozen=True, slots=True)
class ProductBaseline:
    key: str
    product: str
    tac: str
    baseline_p50_s: float
    baseline_p95_s: float
    ceiling_p95_s: float


@dataclass(frozen=True, slots=True)
class ConverterPrBaselines:
    version: int
    status: str
    ratio_limit: float
    absolute_floor_s: float
    iwxxm_version: str
    profile: str
    warmup: int
    iterations: int
    products: dict[str, ProductBaseline]
    raw: dict[str, Any]


def ceiling_p95_s(baseline_p95: float, ratio_limit: float, absolute_floor_s: float) -> float:
    """Return hard-fail ceiling: max(baseline * ratio, baseline + floor)."""
    return max(baseline_p95 * ratio_limit, baseline_p95 + absolute_floor_s)


def _p95(samples: list[float]) -> float:
    xs = sorted(samples)
    if not xs:
        msg = "no samples for p95"
        raise ValueError(msg)
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * 0.95
    f = int(k)
    c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)


def _resolve_tac(entry: dict[str, Any], repo_root: Path) -> str:
    if tac := entry.get("tac"):
        return str(tac).strip()
    fixture = entry.get("fixture")
    if not fixture:
        msg = "product entry needs tac or fixture"
        raise ValueError(msg)
    path = repo_root / str(fixture)
    return path.read_text(encoding="utf-8").strip()


def load_converter_pr_baselines(path: Path | None = None) -> ConverterPrBaselines:
    """Load committed converter PR baselines YAML."""
    target = path or DEFAULT_BASELINES
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    ratio = float(data["ratio_limit"])
    floor = float(data["absolute_floor_s"])
    products: dict[str, ProductBaseline] = {}
    for key, entry in data["products"].items():
        p95 = float(entry["baseline_p95_s"])
        products[key] = ProductBaseline(
            key=key,
            product=str(entry["product"]),
            tac=_resolve_tac(entry, REPO_ROOT),
            baseline_p50_s=float(entry["baseline_p50_s"]),
            baseline_p95_s=p95,
            ceiling_p95_s=ceiling_p95_s(p95, ratio, floor),
        )
    return ConverterPrBaselines(
        version=int(data["version"]),
        status=str(data.get("status", "unknown")),
        ratio_limit=ratio,
        absolute_floor_s=floor,
        iwxxm_version=str(data["iwxxm_version"]),
        profile=str(data["profile"]),
        warmup=int(data["warmup"]),
        iterations=int(data["iterations"]),
        products=products,
        raw=data,
    )


def measure_convert_p95(
    tac: str,
    *,
    product: str,
    profile: str,
    iwxxm_version: str,
    warmup: int,
    iterations: int,
    convert_fn: Any | None = None,
) -> tuple[float, float]:
    """Return (p50, p95) wall times for convert-only calls."""
    from tac2iwxxm import convert as default_convert

    convert = convert_fn or default_convert
    for _ in range(warmup):
        result = convert(
            tac, product=product, profile=profile, iwxxm_version=iwxxm_version
        )
        if not getattr(result, "ok", False):
            msg = f"warmup convert failed for {product}"
            raise RuntimeError(msg)
    samples: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        result = convert(
            tac, product=product, profile=profile, iwxxm_version=iwxxm_version
        )
        elapsed = time.perf_counter() - t0
        if not getattr(result, "ok", False):
            msg = f"convert failed for {product}"
            raise RuntimeError(msg)
        samples.append(elapsed)
    return statistics.median(samples), _p95(samples)


def record_baselines_dict(
    baselines: ConverterPrBaselines,
    *,
    status: str,
    recorded_host: str,
    convert_fn: Any | None = None,
) -> dict[str, Any]:
    """Re-measure all products and return updated YAML-serializable dict."""
    data = dict(baselines.raw)
    data["status"] = status
    data["recorded_host"] = recorded_host
    products_out = dict(data["products"])
    for key, pb in baselines.products.items():
        p50, p95 = measure_convert_p95(
            pb.tac,
            product=pb.product,
            profile=baselines.profile,
            iwxxm_version=baselines.iwxxm_version,
            warmup=baselines.warmup,
            iterations=baselines.iterations,
            convert_fn=convert_fn,
        )
        entry = dict(products_out[key])
        entry["baseline_p50_s"] = float(p50)
        entry["baseline_p95_s"] = float(p95)
        products_out[key] = entry
    data["products"] = products_out
    return data
