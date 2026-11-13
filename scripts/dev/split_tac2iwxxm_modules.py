#!/usr/bin/env python3
"""Split oversized tac2iwxxm modules into packages with contiguous AST chunks.

Behavior-preserving mechanical split:
- module-level imports/assignments → ``_shared.py``
- top-level functions/classes → ``_partNN.py`` bodies (no cross-imports)
- ``__init__.py`` loads ``_shared`` then ``exec``s part bodies into the package
  namespace so private helpers resolve across parts at call time.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

# Body budget so part file (header ~4 lines + units) stays ≤ 500.
MAX_BODY_LINES = 490
PKG = Path("packages/tac2iwxxm/src/tac2iwxxm")

TARGETS: list[str] = [
    "convert.py",
    "bulletin.py",
    "emit_map.py",
    "exchange_output.py",
    "library_yaml.py",
    "conversion_templates.py",
    "slot_builders/metar_speci.py",
    "slot_builders/sigmet_airmet.py",
    "slot_builders/taf.py",
    "slot_builders/vaa_tca.py",
    "profiles/annex3.py",
    "profiles/ca_eccc.py",
    "profiles/iwxxm_us.py",
    "profiles/annex3_emit/sigmet.py",
]


def _source_segment(src: str, node: ast.AST) -> str:
    seg = ast.get_source_segment(src, node)
    if seg is None:
        raise RuntimeError(f"missing source segment for {type(node).__name__}")
    return seg


def _public_names(tree: ast.Module) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "__all__":
                    return list(ast.literal_eval(node.value))
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "__all__" and node.value is not None:
                return list(ast.literal_eval(node.value))
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                names.append(node.name)
    return names


def _pkg_import_path(rel: str) -> str:
    return rel[: -len(".py")].replace("/", ".")


def split_module(rel: str, *, max_body: int = MAX_BODY_LINES) -> None:
    path = PKG / rel
    if not path.is_file():
        print(f"skip missing {rel}", file=sys.stderr)
        return
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    public = _public_names(tree)

    preamble: list[ast.AST] = []
    units: list[ast.AST] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            units.append(node)
            continue
        if isinstance(node, ast.Assign):
            targets = node.targets
            if len(targets) == 1 and isinstance(targets[0], ast.Name) and targets[0].id == "__all__":
                continue
            preamble.append(node)
            continue
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "__all__":
                continue
            preamble.append(node)
            continue
        preamble.append(node)

    shared_body = "\n\n".join(_source_segment(src, n) for n in preamble).rstrip() + "\n"

    pkg_dir = path.with_suffix("")
    if pkg_dir.exists() and pkg_dir.is_dir():
        for child in pkg_dir.iterdir():
            if child.name == "__pycache__":
                continue
            if child.is_file():
                child.unlink()
    else:
        pkg_dir.mkdir(parents=True, exist_ok=True)

    (pkg_dir / "_shared.py").write_text(shared_body, encoding="utf-8")

    parts: list[list[ast.AST]] = []
    current: list[ast.AST] = []
    current_lines = 0
    for unit in units:
        seg = _source_segment(src, unit)
        nlines = seg.count("\n") + 1
        if current and current_lines + nlines + 1 > max_body:
            parts.append(current)
            current = []
            current_lines = 0
        if not current and nlines > max_body:
            parts.append([unit])
            continue
        current.append(unit)
        current_lines += nlines + 1
    if current:
        parts.append(current)

    for idx, group in enumerate(parts, start=1):
        lines = [
            '"""Split part body (exec\'d into package namespace)."""',
            "from __future__ import annotations",
            "",
        ]
        for unit in group:
            lines.append(_source_segment(src, unit))
            lines.append("")
        text = "\n".join(lines).rstrip() + "\n"
        if text.count("\n") > 500:
            print(f"WARN {rel} _part{idx:02d} still >500 lines", file=sys.stderr)
        (pkg_dir / f"_part{idx:02d}.py").write_text(text, encoding="utf-8")

    pkg = _pkg_import_path(rel)
    init_lines = [
        f'"""Package split of former ``{rel}`` (stable import path)."""',
        "from __future__ import annotations",
        "",
        "from importlib import import_module as _import_module",
        "from pathlib import Path as _Path",
        "",
    ]
    if public:
        init_lines.append("__all__ = [")
        for p in public:
            init_lines.append(f'    "{p}",')
        init_lines.append("]")
        init_lines.append("")
    init_lines += [
        f'_shared = _import_module("tac2iwxxm.{pkg}._shared")',
        'globals().update({k: v for k, v in _shared.__dict__.items() if not k.startswith("__")})',
        "",
        "_parts_dir = _Path(__file__).resolve().parent",
        'for _part in sorted(_parts_dir.glob("_part*.py")):',
        '    _src = _part.read_text(encoding="utf-8")',
        '    exec(compile(_src, str(_part), "exec"), globals())',
        "",
        "del _import_module, _Path, _shared, _parts_dir, _part, _src",
        "",
    ]
    (pkg_dir / "__init__.py").write_text("\n".join(init_lines), encoding="utf-8")

    path.unlink()
    print(f"split {rel} -> {pkg_dir.relative_to(PKG)}/ ({len(parts)} parts, shared)")


def main() -> int:
    for rel in TARGETS:
        split_module(rel)
    overs: list[tuple[int, str]] = []
    for path in PKG.rglob("*.py"):
        n = sum(1 for _ in open(path, encoding="utf-8"))
        if n > 500:
            overs.append((n, str(path)))
    if overs:
        print("OVER 500:", file=sys.stderr)
        for n, p in sorted(overs, reverse=True):
            print(f"  {n} {p}", file=sys.stderr)
        return 1
    print("ALL src files <= 500")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
