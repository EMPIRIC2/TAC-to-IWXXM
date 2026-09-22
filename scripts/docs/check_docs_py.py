#!/usr/bin/env python3
"""ADR-048 Python docstring presence + Examples + NumPy shape checker.

[Corpus: adr/ADR-048] [Corpus: docstrings]

Scans in-scope product trees. Exit 0 when clean; prints violations otherwise.
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path

SKIP_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "vendor",
    "fixtures",
    ".venv",
    "dist",
    "build",
    "target",
    "iwxxm_xsd",
    "generated",
}

SKIP_PATH_PARTS = (
    "/tests/",
    "/test_",
    "/__tests__/",
    "/_archive/",
    "/iwxxm_xsd/",
    "/generated/",
    "/docker/",
    "/supabase/functions/",
)

IN_SCOPE_GLOBS = (
    "packages/*/src",
    "apps/backend",
    "apps/worker",
)

EXAMPLES_RE = re.compile(r"(?m)^Examples\s*\n-------+")
PARAMS_RE = re.compile(r"(?m)^Parameters\s*\n----------+")
RETURNS_RE = re.compile(r"(?m)^Returns\s*\n-------+")
ATTRIBUTES_RE = re.compile(r"(?m)^Attributes\s*\n----------+")


def _should_skip(path: Path) -> bool:
    """Return True when ``path`` is outside the ADR-048 product scan."""
    parts = path.as_posix()
    if any(part in parts for part in SKIP_PATH_PARTS):
        return True
    return any(name in path.parts for name in SKIP_DIR_NAMES)


def _is_typing_stub_class(node: ast.ClassDef) -> bool:
    """True for Protocol / TypedDict / Enum structural stubs."""
    for base in node.bases:
        name = ""
        if isinstance(base, ast.Name):
            name = base.id
        elif isinstance(base, ast.Attribute):
            name = base.attr
        if name in {"Protocol", "TypedDict", "Enum", "IntEnum", "StrEnum"}:
            return True
    return False


def _has_args(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True when the function has non-self/cls parameters."""
    args = node.args
    positional = list(args.posonlyargs) + list(args.args)
    names = [a.arg for a in positional]
    if names and names[0] in {"self", "cls"}:
        names = names[1:]
    return bool(names or args.kwonlyargs or args.vararg or args.kwarg)


def _doc_ok_private(doc: str | None) -> bool:
    """Private helpers need a non-empty docstring (NumPy sections optional)."""
    return bool(doc and doc.strip())


def _doc_ok_public_fn(
    doc: str | None, *, has_args: bool, has_return: bool
) -> list[str]:
    """Return list of public-function shape violations for ``doc``."""
    issues: list[str] = []
    if not doc or not doc.strip():
        return ["missing docstring"]
    if not EXAMPLES_RE.search(doc):
        issues.append("missing Examples section")
    if has_args and not PARAMS_RE.search(doc):
        issues.append("missing Parameters section")
    if has_return and not RETURNS_RE.search(doc):
        # Allow None returns without Returns when annotated None — still prefer Returns
        issues.append("missing Returns section")
    return issues


def _doc_ok_public_class(doc: str | None) -> list[str]:
    """Return class docstring shape issues (Attributes or Parameters)."""
    if not doc or not doc.strip():
        return ["missing docstring"]
    if ATTRIBUTES_RE.search(doc) or PARAMS_RE.search(doc):
        return []
    # Module-style one-liner classes still need Attributes OR Parameters per ADR-048
    return ["missing Attributes or Parameters section"]


def _returns_annotation(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True when a return annotation other than None/NoneType is present."""
    if node.returns is None:
        return False
    if isinstance(node.returns, ast.Constant) and node.returns.value is None:
        return False
    if isinstance(node.returns, ast.Name) and node.returns.id in {"None"}:
        return False
    return True


def check_file(path: Path) -> list[str]:
    """Return human-readable violation strings for one Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as exc:
        return [f"{path}:0 parse-error {exc}"]

    missing: list[str] = []

    class Visitor(ast.NodeVisitor):
        """Walk AST collecting ADR-048 docstring violations."""

        def __init__(self) -> None:
            self._stub_depth = 0

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Check sync functions/methods."""
            self._check_fn(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            """Check async functions/methods."""
            self._check_fn(node)
            self.generic_visit(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            """Check classes; skip method bodies inside typing stubs."""
            if node.name == "Enum" or _is_typing_stub_class(node):
                # Document the type; methods inside stubs exempt.
                doc = ast.get_docstring(node)
                if not doc or not doc.strip():
                    missing.append(
                        f"{path}:{node.lineno} class {node.name}: missing docstring"
                    )
                self._stub_depth += 1
                self.generic_visit(node)
                self._stub_depth -= 1
                return
            if self._stub_depth == 0:
                doc = ast.get_docstring(node)
                if node.name.startswith("_"):
                    issues = [] if _doc_ok_private(doc) else ["missing docstring"]
                else:
                    issues = _doc_ok_public_class(doc)
                for issue in issues:
                    missing.append(f"{path}:{node.lineno} class {node.name}: {issue}")
            self.generic_visit(node)

        def _check_fn(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
            if self._stub_depth > 0:
                return
            if node.name in {"__getattr__", "__dir__"}:
                return
            doc = ast.get_docstring(node)
            public = not node.name.startswith("_")
            if not public:
                if not _doc_ok_private(doc):
                    missing.append(
                        f"{path}:{node.lineno} function {node.name}: missing docstring"
                    )
                return
            issues = _doc_ok_public_fn(
                doc,
                has_args=_has_args(node),
                has_return=_returns_annotation(node),
            )
            for issue in issues:
                missing.append(f"{path}:{node.lineno} function {node.name}: {issue}")

    # Module docstring
    if not ast.get_docstring(tree):
        missing.append(f"{path}:1 module: missing docstring")

    Visitor().visit(tree)
    return missing


def iter_in_scope(root: Path) -> list[Path]:
    """List in-scope ``.py`` files under ``root``."""
    files: list[Path] = []
    for pattern in IN_SCOPE_GLOBS:
        for base in root.glob(pattern):
            if not base.exists():  # pragma: no cover - Path.glob never yields missing paths
                continue
            if base.is_file() and base.suffix == ".py" and not _should_skip(base):
                files.append(base)
                continue
            for path in base.rglob("*.py"):
                if not _should_skip(path):
                    files.append(path)
    return sorted(set(files))


def main(argv: list[str] | None = None) -> int:
    """CLI entry for ``make check-docs``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Repository root (default: .)",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Optional explicit file/dir paths (overrides default globs)",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    if args.paths:
        targets: list[Path] = []
        for raw in args.paths:
            p = Path(raw)
            if not p.is_absolute():
                p = root / p
            if p.is_file():
                targets.append(p)
            else:
                targets.extend(sorted(p.rglob("*.py")))
        # Explicit paths are trusted (fixture tests); do not apply tree skips.
        files = [p for p in targets if p.suffix == ".py"]
    else:
        files = iter_in_scope(root)

    violations: list[str] = []
    for path in files:
        violations.extend(check_file(path))

    print(f"check-docs scanned_files={len(files)} violations={len(violations)}")
    for item in violations[:80]:
        print(item)
    if len(violations) > 80:
        print(f"... and {len(violations) - 80} more")
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())
