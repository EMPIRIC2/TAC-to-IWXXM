#!/usr/bin/env python3
"""IWXXM XSD → pydantic codegen via xsdata (ADR-027 / E10-40 / T3.6).

Reads pinned ``vendor/schemas/iwxxm/{version}/IWXXM/*.xsd`` and writes pydantic
models under ``packages/shared/src/metar_shared/iwxxm_xsd/``. Validate hot path
stays Rust (ADR-027) — these models are for typed bind / convert follow-on (T3.7).

Usage
-----
::

    make codegen-iwxxm-xsd
    # or:
    uv run python scripts/codegen/iwxxm_xsd.py --version 2025-2
    uv run python scripts/codegen/iwxxm_xsd.py --check   # config / pins only
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR_IWXXM = REPO_ROOT / "vendor" / "schemas" / "iwxxm"
MANIFEST = REPO_ROOT / "vendor" / "manifest.json"
OUT_ROOT = REPO_ROOT / "packages" / "shared" / "src" / "metar_shared" / "iwxxm_xsd"
DEFAULT_ENTRY = "iwxxm.xsd"

# Known xsdata-pydantic + GML quirk: field(..., default=X, default=X) breaks parse.
# Match both field( and Field(; allow newlines between duplicate defaults.
_DUP_DEFAULT = re.compile(
    r"(default\s*=\s*[^\n,]+)(\s*,\s*\n?\s*default\s*=\s*[^\n,]+)+"
)


def fix_duplicate_field_defaults(tree_root: Path) -> int:
    """
    Remove duplicate ``default=`` kwargs in generated modules.

    Returns
    -------
    int
        Number of files modified.
    """
    changed = 0
    for path in tree_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        fixed = _DUP_DEFAULT.sub(r"\1", text)
        if fixed != text:
            path.write_text(fixed, encoding="utf-8")
            changed += 1
    return changed


def _version_package(version: str) -> str:
    """Return Python package segment for an IWXXM release line (``2025-2`` → ``v2025_2``)."""
    return "v" + version.replace("-", "_").replace(".", "_")


def load_manifest_versions() -> list[str]:
    """Return IWXXM version directory names present under the vendor pin."""
    if not VENDOR_IWXXM.is_dir():
        raise FileNotFoundError(f"vendor iwxxm missing: {VENDOR_IWXXM}")
    found = sorted(
        p.name
        for p in VENDOR_IWXXM.iterdir()
        if p.is_dir() and (p / "IWXXM" / "iwxxm.xsd").is_file()
    )
    if not found:
        raise FileNotFoundError(f"no IWXXM version trees under {VENDOR_IWXXM}")
    return found


def resolve_versions(requested: list[str] | None) -> list[str]:
    """Intersect requested versions with vendor pins (default: all pinned trees)."""
    available = load_manifest_versions()
    if not requested:
        return available
    missing = [v for v in requested if v not in available]
    if missing:
        raise FileNotFoundError(
            f"IWXXM versions not in vendor pin: {missing}; have {available}"
        )
    return requested


def _patch_xsdata_generators() -> None:
    """Register pydantic output and soften ruff / circular-import hard fails."""
    import xsdata_pydantic.hooks.cli  # noqa: F401
    from xsdata.formats.dataclass.generator import DataclassGenerator

    orig_ruff = DataclassGenerator.ruff_code
    orig_validate = DataclassGenerator.validate_imports

    def ruff_code(self: Any, file_paths: list[str]) -> None:
        for root in file_paths:
            fix_duplicate_field_defaults(Path(root))
        try:
            orig_ruff(self, file_paths)
        except Exception as exc:
            print(f"codegen: ruff soft-fail (models kept): {exc}", file=sys.stderr)
            for root in file_paths:
                fix_duplicate_field_defaults(Path(root))

    def validate_imports(self: Any) -> None:
        try:
            orig_validate(self)
        except Exception as exc:
            print(
                f"codegen: import-validation soft-fail "
                f"(GML circular imports known): {exc}",
                file=sys.stderr,
            )

    DataclassGenerator.ruff_code = ruff_code  # type: ignore[method-assign]
    DataclassGenerator.validate_imports = validate_imports  # type: ignore[method-assign]


def generate_version(
    version: str,
    *,
    entry: str = DEFAULT_ENTRY,
    out_root: Path | None = None,
) -> dict[str, Any]:
    """
    Run xsdata pydantic codegen for one IWXXM release line.

    Parameters
    ----------
    version :
        Release line such as ``2025-2``.
    entry :
        Entry XSD filename under ``IWXXM/`` (default ``iwxxm.xsd``).
    out_root :
        Package root for generated ``v*`` trees (default: repo ``iwxxm_xsd``).
        Must be ``…/metar_shared/iwxxm_xsd`` so xsdata package paths resolve.
        Tests pass a temp root so smoke regen does not clobber committed models.

    Returns
    -------
    dict
        Summary with output path and file counts.
    """
    from xsdata.codegen.transformer import ResourceTransformer
    from xsdata.models.config import (
        DocstringStyle,
        GeneratorConfig,
        OutputFormat,
        StructureStyle,
    )

    _patch_xsdata_generators()

    xsd = VENDOR_IWXXM / version / "IWXXM" / entry
    if not xsd.is_file():
        raise FileNotFoundError(f"entry XSD missing: {xsd}")

    root = out_root if out_root is not None else OUT_ROOT
    root.mkdir(parents=True, exist_ok=True)
    # …/src/metar_shared/iwxxm_xsd → shared_src is …/src
    shared_src = root.parent.parent
    if root.name != "iwxxm_xsd" or root.parent.name != "metar_shared":
        raise ValueError(f"out_root must end with metar_shared/iwxxm_xsd, got {root}")

    pkg = f"metar_shared.iwxxm_xsd.{_version_package(version)}"
    out_dir = root / _version_package(version)
    if out_dir.exists():
        shutil.rmtree(out_dir)

    # xsdata writes packages relative to CWD (= shared src root).
    prev = Path.cwd()
    os.chdir(shared_src)
    try:
        cfg = GeneratorConfig.create()
        cfg.output.package = pkg
        cfg.output.format = OutputFormat(value="pydantic")
        cfg.output.structure_style = StructureStyle.FILENAMES
        cfg.output.docstring_style = DocstringStyle.NUMPY
        cfg.output.max_line_length = 120
        cfg.output.relative_imports = True
        cfg.output.include_header = True

        transformer = ResourceTransformer(config=cfg)
        transformer.process([xsd.resolve().as_uri()])
    finally:
        os.chdir(prev)

    if out_dir.is_dir():
        n_fixed = fix_duplicate_field_defaults(out_dir)
        if n_fixed:
            print(
                f"codegen: fixed duplicate default= in {n_fixed} files", file=sys.stderr
            )

    py_files = list(out_dir.rglob("*.py")) if out_dir.is_dir() else []
    try:
        output_rel: str | None = str(out_dir.relative_to(REPO_ROOT))
    except ValueError:
        output_rel = str(out_dir)
    return {
        "version": version,
        "entry": entry,
        "package": pkg,
        "output": output_rel if out_dir.exists() else None,
        "py_files": len(py_files),
        "bytes": sum(p.stat().st_size for p in py_files),
    }


def write_package_init(versions: list[str]) -> None:
    """Ensure ``iwxxm_xsd`` package markers and a STATUS stamp exist."""
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    init = OUT_ROOT / "__init__.py"
    if not init.is_file():
        init.write_text(
            '"""Generated IWXXM pydantic models (xsdata / ADR-027). '
            'Run make codegen-iwxxm-xsd."""\n',
            encoding="utf-8",
        )
    readme = OUT_ROOT / "README.md"
    if not readme.is_file():
        readme.write_text(
            "# iwxxm_xsd (generated)\n\n"
            "Pydantic models from pinned `vendor/schemas/iwxxm` via "
            "`scripts/codegen/iwxxm_xsd.py` (ADR-027).\n\n"
            "Regenerate: `make codegen-iwxxm-xsd`\n\n"
            "Do not hand-edit generated modules — re-run codegen on vendor pin bumps.\n",
            encoding="utf-8",
        )
    status: dict[str, Any] = {
        "generator": "xsdata+xsdata-pydantic",
        "adr": "ADR-027",
        "versions": versions,
        "manifest_pin": None,
    }
    if MANIFEST.is_file():
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        status["manifest_pin"] = data.get("bundles", {}).get("iwxxm", {})
    (OUT_ROOT / "STATUS.json").write_text(
        json.dumps(status, indent=2) + "\n", encoding="utf-8"
    )


def check_only() -> int:
    """Validate vendor pins and output layout without generating."""
    versions = load_manifest_versions()
    print(f"codegen check: vendor versions={versions}")
    print(f"codegen check: output root={OUT_ROOT.relative_to(REPO_ROOT)}")
    if not MANIFEST.is_file():
        print("error: vendor/manifest.json missing", file=sys.stderr)
        return 1
    print("codegen check: ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry for Makefile ``codegen-iwxxm-xsd``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--version",
        action="append",
        dest="versions",
        help="IWXXM version to generate (repeatable). Default: all vendor pins.",
    )
    parser.add_argument(
        "--entry",
        default=DEFAULT_ENTRY,
        help=f"Entry XSD under IWXXM/ (default: {DEFAULT_ENTRY})",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate pins/layout only; do not generate",
    )
    args = parser.parse_args(argv)

    if args.check:
        return check_only()

    try:
        versions = resolve_versions(args.versions)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    write_package_init(versions)
    summaries: list[dict[str, Any]] = []
    for version in versions:
        print(f"codegen: generating {version} ({args.entry})…")
        try:
            summary = generate_version(version, entry=args.entry)
        except Exception as exc:
            print(f"error: codegen failed for {version}: {exc}", file=sys.stderr)
            return 1
        summaries.append(summary)
        print(
            f"codegen: {version} → {summary['py_files']} files "
            f"({summary['bytes'] / 1024:.0f} KiB) package={summary['package']}"
        )

    stamp = OUT_ROOT / "LAST_RUN.json"
    stamp.write_text(json.dumps({"runs": summaries}, indent=2) + "\n", encoding="utf-8")
    write_package_init(versions)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
