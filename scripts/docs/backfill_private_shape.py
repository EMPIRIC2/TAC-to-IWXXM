#!/usr/bin/env python3
"""Rewrite private helper docstrings to include Parameters/Returns when required.

Used by EV-adr048-doc-linters M3 (D-EVDOC-LINT-02 / TC-EVDOC-010).
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import textwrap
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_docs_py",
    Path(__file__).resolve().parent / "check_docs_py.py",
)
assert _spec and _spec.loader
_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_check)
_has_args = _check._has_args
_returns_annotation = _check._returns_annotation
PARAMS_RE = _check.PARAMS_RE
RETURNS_RE = _check.RETURNS_RE
iter_in_scope = _check.iter_in_scope


def _indent_doc(doc: str, indent: str) -> str:
    """Format a docstring body with the given indentation."""
    body = textwrap.dedent(doc).strip("\n")
    lines = body.splitlines()
    if not lines:
        return f'{indent}"""TODO."""'
    if len(lines) == 1:
        return f'{indent}"""{lines[0]}"""'
    inner = "\n".join(f"{indent}{line}" if line else "" for line in lines)
    return f'{indent}"""\n{inner}\n{indent}"""'


def _arg_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    """Return non-self/cls parameter names for ``node``."""
    args = list(node.args.posonlyargs) + list(node.args.args)
    names = [a.arg for a in args]
    if names and names[0] in {"self", "cls"}:
        names = names[1:]
    names.extend(a.arg for a in node.args.kwonlyargs)
    if node.args.vararg:
        names.append(node.args.vararg.arg)
    if node.args.kwarg:
        names.append(node.args.kwarg.arg)
    return names


def _private_shaped_doc(name: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Build a private NumPy docstring with Parameters/Returns when applicable."""
    summary = f"Internal helper ``{name}``."
    params_block = ""
    if _has_args(node):
        param_lines = "\n".join(
            f"{n} : object\n    Argument ``{n}``." for n in _arg_names(node)
        )
        params_block = f"\n\nParameters\n----------\n{param_lines}"
    returns_block = ""
    if _returns_annotation(node):
        returns_block = "\n\nReturns\n-------\nobject\n    Return value."
    return f"{summary}{params_block}{returns_block}"


def rewrite_file(path: Path) -> bool:
    """Rewrite private docs in ``path``; return True when changed."""
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False

    lines = src.splitlines(keepends=True)
    replacements: list[tuple[int, int, str]] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("_") or node.name in {"__getattr__", "__dir__"}:
            continue
        needs_params = _has_args(node)
        needs_returns = _returns_annotation(node)
        if not needs_params and not needs_returns:
            continue
        doc = ast.get_docstring(node)
        if doc and (not needs_params or PARAMS_RE.search(doc)) and (
            not needs_returns or RETURNS_RE.search(doc)
        ):
            continue
        if not node.body:
            continue
        doc_stmt = node.body[0]
        if not (
            isinstance(doc_stmt, ast.Expr)
            and isinstance(doc_stmt.value, ast.Constant)
            and isinstance(doc_stmt.value.value, str)
        ):
            # Missing docstring entirely — insert
            indent = " " * (node.col_offset + 4)
            new_block = _indent_doc(_private_shaped_doc(node.name, node), indent) + "\n"
            replacements.append((node.body[0].lineno - 1, node.body[0].lineno - 1, new_block))
            continue
        start = doc_stmt.lineno - 1
        end = doc_stmt.end_lineno or doc_stmt.lineno
        indent = " " * (node.col_offset + 4)
        new_block = _indent_doc(_private_shaped_doc(node.name, node), indent) + "\n"
        replacements.append((start, end, new_block))

    if not replacements:
        return False

    replacements.sort(key=lambda t: t[0], reverse=True)
    for start, end, text in replacements:
        lines[start:end] = [text]
    path.write_text("".join(lines), encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    """CLI entry for private-shape backfill."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    changed = 0
    for path in iter_in_scope(root):
        if rewrite_file(path):
            changed += 1
            print(f"updated {path.relative_to(root)}")
    print(f"backfill_private_shape files_changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
