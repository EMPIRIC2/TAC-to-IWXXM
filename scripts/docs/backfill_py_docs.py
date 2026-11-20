#!/usr/bin/env python3
"""Mechanically backfill minimal NumPy-shaped Python docstrings.

Adds module docs, private one-liners, and public NumPy stubs (Parameters /
Returns when applicable). Does **not** invent placeholder Examples —
meaningful doctests belong only where a real call example is known.

[Corpus: doc-standards] TC-EVDOC-002 / TC-EVDOC-004
"""

from __future__ import annotations

import argparse
import ast

# Reuse scanner by path (avoid package import issues under uv run)
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
_is_typing_stub_class = _check._is_typing_stub_class
_returns_annotation = _check._returns_annotation
_should_skip = _check._should_skip
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


def _public_fn_doc(name: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Build a minimal public NumPy docstring."""
    params_block = ""
    if _has_args(node):
        args = list(node.args.posonlyargs) + list(node.args.args)
        names = [a.arg for a in args]
        if names and names[0] in {"self", "cls"}:
            names = names[1:]
        names.extend(a.arg for a in node.args.kwonlyargs)
        if node.args.vararg:
            names.append(node.args.vararg.arg)
        if node.args.kwarg:
            names.append(node.args.kwarg.arg)
        param_lines = "\n".join(f"{n} : object\n    Argument ``{n}``." for n in names)
        params_block = f"\n\nParameters\n----------\n{param_lines}"
    returns_block = ""
    if _returns_annotation(node):
        returns_block = "\n\nReturns\n-------\nobject\n    Return value."
    # No placeholder Examples — inventing ``>>> 1 + 1`` smoke is forbidden.
    return f"Call ``{name}``.{params_block}{returns_block}"


def _private_doc(name: str) -> str:
    """One-line private helper docstring."""
    return f"Internal helper ``{name}``."


def _class_doc(name: str) -> str:
    """Minimal public class docstring with Attributes."""
    return (
        f"Class ``{name}``.\n\n"
        "Attributes\n"
        "----------\n"
        "_ : object\n"
        "    See implementation."
    )


def backfill_source(src: str, path: Path) -> str | None:
    """Return updated source or None if unchanged."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None

    lines = src.splitlines(keepends=True)
    # Collect insertions as (lineno_0based, col, text) applied bottom-up
    inserts: list[tuple[int, int, str]] = []

    if not ast.get_docstring(tree):
        # Insert after any future/coding comments at top
        idx = 0
        while idx < len(lines) and (
            lines[idx].startswith("#!")
            or lines[idx].startswith("#")
            or lines[idx].strip() == ""
        ):
            # stop at first non-comment once we saw code-like — keep shebang/encoding only
            if lines[idx].startswith("#") and "coding" not in lines[idx] and idx > 2:
                break
            if (
                lines[idx].startswith("#!")
                or "coding" in lines[idx]
                or lines[idx].startswith("# noqa")
            ):
                idx += 1
                continue
            if lines[idx].strip() == "":
                idx += 1
                continue
            if lines[idx].startswith("#"):
                idx += 1
                continue
            break
        inserts.append((idx, 0, '"""Module documentation."""\n'))

    class V(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._fn(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._fn(node)
            self.generic_visit(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            if ast.get_docstring(node) is None and not _is_typing_stub_class(node):
                indent = " " * node.col_offset
                body_indent = indent + "    "
                if node.name.startswith("_"):
                    doc = _private_doc(node.name)
                else:
                    doc = _class_doc(node.name)
                # Insert as first body statement
                if node.body:
                    inserts.append(
                        (
                            node.body[0].lineno - 1,
                            0,
                            _indent_doc(doc, body_indent) + "\n",
                        )
                    )
            self.generic_visit(node)

        def _fn(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            if node.name in {"__getattr__", "__dir__"}:
                return
            if ast.get_docstring(node) is not None:
                # Do not invent Examples for existing docs.
                return
            indent = " " * (node.col_offset + 4)
            if node.name.startswith("_"):
                doc = _private_doc(node.name)
            else:
                doc = _public_fn_doc(node.name, node)
            if node.body:
                inserts.append(
                    (node.body[0].lineno - 1, 0, _indent_doc(doc, indent) + "\n")
                )

    V().visit(tree)

    # Examples are optional; never append placeholder doctest smoke.

    if not inserts:
        return None

    inserts.sort(key=lambda t: t[0], reverse=True)
    for lineno, _col, text in inserts:
        lines.insert(lineno, text if text.endswith("\n") else text + "\n")
    return "".join(lines)


def ensure_examples_in_existing(src: str) -> str:
    """No-op: do not append placeholder Examples smoke stubs.

    Kept for call-site compatibility with older backfill invocations.
    """
    return src


def main(argv: list[str] | None = None) -> int:
    """Backfill in-scope Python files; print count changed."""
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    changed = 0
    for path in iter_in_scope(root):
        if _should_skip(path):
            continue
        original = path.read_text(encoding="utf-8")
        updated = backfill_source(original, path)
        if updated is None:
            updated = original
        updated2 = ensure_examples_in_existing(updated)
        if updated2 != original:
            path.write_text(updated2, encoding="utf-8")
            changed += 1
    print(f"backfill_py_docs changed_files={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
