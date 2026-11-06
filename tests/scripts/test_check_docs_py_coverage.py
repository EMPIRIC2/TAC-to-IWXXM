"""Coverage for scripts/docs/check_docs_py.py ADR-048 branches (scripts cov gate)."""

from __future__ import annotations

from pathlib import Path

import scripts.docs.check_docs_py as check_docs_py
from scripts.docs.check_docs_py import (
    _doc_ok_private,
    _doc_ok_public_class,
    _doc_ok_public_fn,
    _has_args,
    _is_typing_stub_class,
    _returns_annotation,
    _should_skip,
    check_file,
    iter_in_scope,
    main,
)

ROOT = Path(__file__).resolve().parents[2]


def test_should_skip_tests_and_vendor_dirs() -> None:
    # Avoid pytest tmp paths containing "test_" (matches SKIP_PATH_PARTS).
    base = Path("/tmp/evdoc-cov-skip")
    assert _should_skip(base / "packages" / "x" / "tests" / "a.py")
    assert _should_skip(base / "vendor" / "schemas" / "a.py")
    assert not _should_skip(base / "packages" / "x" / "src" / "a.py")


def test_typing_stub_and_args_and_returns_helpers() -> None:
    import ast

    stub = ast.parse("class P(Protocol):\n    pass\n").body[0]
    assert isinstance(stub, ast.ClassDef)
    # Protocol not imported — Name base
    stub.bases = [ast.Name(id="Protocol", ctx=ast.Load())]
    assert _is_typing_stub_class(stub)
    stub.bases = [
        ast.Attribute(
            value=ast.Name(id="t", ctx=ast.Load()), attr="TypedDict", ctx=ast.Load()
        )
    ]
    assert _is_typing_stub_class(stub)
    stub.bases = [
        ast.Attribute(
            value=ast.Name(id="t", ctx=ast.Load()), attr="NotAStub", ctx=ast.Load()
        )
    ]
    assert not _is_typing_stub_class(stub)
    # neither Name nor Attribute → fall through with empty name
    stub.bases = [ast.Constant(value="Protocol")]
    assert not _is_typing_stub_class(stub)
    stub.bases = [ast.Name(id="object", ctx=ast.Load())]
    assert not _is_typing_stub_class(stub)

    fn = ast.parse("def f(self, x):\n    pass\n").body[0]
    assert isinstance(fn, ast.FunctionDef)
    assert _has_args(fn)
    bare = ast.parse("def g(self):\n    pass\n").body[0]
    assert isinstance(bare, ast.FunctionDef)
    assert not _has_args(bare)

    none_ret = ast.parse("def h() -> None:\n    pass\n").body[0]
    assert isinstance(none_ret, ast.FunctionDef)
    assert not _returns_annotation(none_ret)
    int_ret = ast.parse("def i() -> int:\n    return 1\n").body[0]
    assert isinstance(int_ret, ast.FunctionDef)
    assert _returns_annotation(int_ret)
    no_ann = ast.parse("def j():\n    pass\n").body[0]
    assert isinstance(no_ann, ast.FunctionDef)
    assert not _returns_annotation(no_ann)


def test_doc_ok_helpers() -> None:
    assert not _doc_ok_private(None)
    assert _doc_ok_private("x")
    assert _doc_ok_public_fn(None, has_args=False, has_return=False) == [
        "missing docstring"
    ]
    issues = _doc_ok_public_fn("summary\n", has_args=True, has_return=True)
    assert "missing Examples section" in issues
    assert "missing Parameters section" in issues
    assert "missing Returns section" in issues
    good = (
        "summary\n\nParameters\n----------\nx : int\n\n"
        "Returns\n-------\nint\n\nExamples\n--------\n>>> 1\n1\n"
    )
    assert _doc_ok_public_fn(good, has_args=True, has_return=True) == []
    assert _doc_ok_public_class(None) == ["missing docstring"]
    assert _doc_ok_public_class("only title") == [
        "missing Attributes or Parameters section"
    ]
    assert _doc_ok_public_class("Attributes\n----------\nx : int\n") == []


def test_check_file_parse_error_and_shapes(tmp_path: Path) -> None:
    bad = tmp_path / "bad.py"
    bad.write_text("def (\n", encoding="utf-8")
    assert any("parse-error" in item for item in check_file(bad))

    sample = tmp_path / "sample.py"
    sample.write_text(
        '''"""Mod."""

class _Priv:
    """ok private."""

class Public:
    """Public class.

    Attributes
    ----------
    x : int
        x
    """

    def __getattr__(self, name: str) -> int:
        return 0

    async def work(self, n: int) -> int:
        """Do work.

        Parameters
        ----------
        n : int
            n

        Returns
        -------
        int
            n

        Examples
        --------
        >>> 1
        1
        """
        return n

    def _hidden(self) -> None:
        pass

from enum import Enum
from typing import Protocol

class Kind(Enum):
    """Kind enum."""

    A = 1

class Hook(Protocol):
    """Hook protocol."""

    def run(self) -> None:
        ...
''',
        encoding="utf-8",
    )
    issues = check_file(sample)
    # private _hidden missing docstring should appear; Protocol method exempt
    assert any("_hidden" in item for item in issues)
    assert not any("function run" in item for item in issues)


def test_iter_in_scope_and_main_paths() -> None:
    base = Path("/tmp/evdoc-cov-scope")
    if base.exists():
        import shutil

        shutil.rmtree(base)
    pkg = base / "packages" / "demo" / "src"
    pkg.mkdir(parents=True)
    (pkg / "mod.py").write_text('"""m."""\n', encoding="utf-8")
    (base / "packages" / "demo" / "tests").mkdir()
    (base / "packages" / "demo" / "tests" / "t.py").write_text(
        "x=1\n", encoding="utf-8"
    )
    files = iter_in_scope(base)
    assert any(p.name == "mod.py" for p in files)
    assert not any("tests" in str(p) for p in files)

    # relative --paths dir walk
    assert main([str(base), "--paths", "packages/demo/src"]) == 0
    empty = base / "empty.py"
    empty.write_text("def f(x: int) -> int:\n    return x\n", encoding="utf-8")
    assert main([str(base), "--paths", str(empty)]) == 1


def test_remaining_branch_coverage() -> None:
    import ast
    import shutil

    base = Path("/tmp/evdoc-cov-branches")
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)

    # SKIP_DIR_NAMES via path.parts (line 58)
    assert _should_skip(base / "node_modules" / "pkg" / "a.py")

    # returns annotation Name None (line 123)
    none_name = ast.parse("def k() -> None:\n    pass\n").body[0]
    # Force Name node rather than Constant for older/alternate parse
    assert isinstance(none_name, ast.FunctionDef)
    none_name.returns = ast.Name(id="None", ctx=ast.Load())
    assert not _returns_annotation(none_name)

    # stub class missing docstring (line 158) — Enum by name short-circuit
    stub = base / "stub.py"
    stub.write_text(
        '"""m."""\nclass Enum:\n    pass\n',
        encoding="utf-8",
    )
    issues = check_file(stub)
    assert any("class Enum" in i and "missing docstring" in i for i in issues)

    # Protocol stub missing docstring
    stub2 = base / "stub2.py"
    stub2.write_text(
        '"""m."""\nfrom typing import Protocol\nclass Hook(Protocol):\n    pass\n',
        encoding="utf-8",
    )
    assert any("Hook" in i and "missing docstring" in i for i in check_file(stub2))

    # nested class inside Protocol exercises stub_depth>0 ClassDef path
    nest = base / "nest.py"
    nest.write_text(
        '"""m."""\nfrom typing import Protocol\n'
        'class Hook(Protocol):\n    """Hook."""\n    class Nested:\n        """Nested."""\n',
        encoding="utf-8",
    )
    assert check_file(nest) == []  # Nested skipped under stub_depth

    # module missing docstring (line 198)
    nodoc = base / "nodoc.py"
    nodoc.write_text("x = 1\n", encoding="utf-8")
    assert any("module: missing docstring" in i for i in check_file(nodoc))

    # iter_in_scope: missing glob base (210), file glob hit (212-213), skip in rglob (216)
    # Manufacture a tiny fake tree matching IN_SCOPE_GLOBS by temporarily patching
    orig = list(check_docs_py.IN_SCOPE_GLOBS)
    try:
        check_docs_py.IN_SCOPE_GLOBS = (
            "missing-glob-dir",
            "single.py",
            "pkg",
        )
        (base / "single.py").write_text('"""s."""\n', encoding="utf-8")
        pkg = base / "pkg"
        pkg.mkdir()
        (pkg / "ok.py").write_text('"""o."""\n', encoding="utf-8")
        (pkg / "tests").mkdir()
        (pkg / "tests" / "skip.py").write_text("x=1\n", encoding="utf-8")
        found = {p.name for p in iter_in_scope(base)}
        assert "single.py" in found
        assert "ok.py" in found
        assert "skip.py" not in found
    finally:
        check_docs_py.IN_SCOPE_GLOBS = tuple(orig)

    # relative --paths file (241) and directory (245)
    rel_root = base / "relroot"
    rel_root.mkdir()
    sub = rel_root / "sub"
    sub.mkdir()
    (sub / "a.py").write_text('"""a."""\n', encoding="utf-8")
    assert main([str(rel_root), "--paths", "sub/a.py"]) == 0
    assert main([str(rel_root), "--paths", "sub"]) == 0

    # public class missing Attributes/Parameters (line 172)
    pub = base / "pub.py"
    pub.write_text(
        '"""m."""\nclass PublicBad:\n    """title only"""\n', encoding="utf-8"
    )
    assert any("PublicBad" in i for i in check_file(pub))

    # main() default globs path (line 249) — empty tree still exits 0
    empty_root = base / "emptyroot"
    empty_root.mkdir()
    assert main([str(empty_root)]) == 0

    # >80 violations truncation (259)
    flood = base / "flood"
    flood.mkdir()
    lines = ['"""m."""\n']
    lines.extend(f"def f{i}(x: int) -> int:\n    return x\n" for i in range(90))
    (flood / "many.py").write_text("".join(lines), encoding="utf-8")
    assert main([str(base), "--paths", str(flood / "many.py")]) == 1
