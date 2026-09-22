"""Coverage for scripts/overlays/preflight.py (EV-YEC / #1224)."""

from __future__ import annotations

from pathlib import Path

import pytest
from scripts.overlays import preflight as mod
from tests.scripts.conftest import REPO_ROOT

_VALID_PACK = (
    REPO_ROOT / "packages" / "tac-decoding" / "examples" / "overlays" / "valid"
)
_INVALID_PACK = (
    REPO_ROOT
    / "packages"
    / "tac-decoding"
    / "examples"
    / "overlays"
    / "invalid-bad-extends"
)


def test_main_all_examples_ok() -> None:
    assert mod.main(["--all-examples"]) == 0


def test_main_kind_dir_ok() -> None:
    assert mod.main(["--kind", "pack", "--dir", str(_VALID_PACK)]) == 0


def test_main_kind_dir_expect_fail() -> None:
    assert (
        mod.main(["--kind", "pack", "--dir", str(_INVALID_PACK), "--expect-fail"]) == 0
    )


def test_main_missing_dir(tmp_path: Path) -> None:
    missing = tmp_path / "nope"
    with pytest.raises(SystemExit) as exc:
        mod.main(["--kind", "pack", "--dir", str(missing)])
    assert exc.value.code == 1


def test_main_requires_args() -> None:
    with pytest.raises(SystemExit) as exc:
        mod.main([])
    assert exc.value.code == 2


def test_run_examples_missing_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        mod,
        "_EXAMPLE_ROOTS",
        (("pack", tmp_path / "missing-root"),),
    )
    with pytest.raises(SystemExit) as exc:
        mod._run_examples()
    assert exc.value.code == 1


def test_expect_fail_when_checker_passes(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setitem(mod._CHECKERS, "pack", lambda _d: None)
    with pytest.raises(SystemExit) as exc:
        mod._expect_fail("pack", tmp_path)
    assert exc.value.code == 1


def test_expect_fail_non_one_systemexit(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def boom(_d: Path) -> None:
        raise SystemExit(3)

    monkeypatch.setitem(mod._CHECKERS, "pack", boom)
    with pytest.raises(SystemExit) as exc:
        mod._expect_fail("pack", tmp_path)
    assert exc.value.code == 3


def test_run_examples_missing_starters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    overlays = tmp_path / "overlays"
    (overlays / "valid").mkdir(parents=True)
    (overlays / "invalid-bad-extends").mkdir()
    monkeypatch.setattr(mod, "_EXAMPLE_ROOTS", (("pack", overlays),))
    with pytest.raises(SystemExit) as exc:
        mod._run_examples()
    assert exc.value.code == 1


def test_check_pack_loader_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "tac_decoding.overlay_check.check_pack_overlay_dir",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    with pytest.raises(SystemExit) as exc:
        mod._check_pack(tmp_path)
    assert exc.value.code == 1


def test_check_tac_policy_policy_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from tac_validate.policy import PolicyError

    monkeypatch.setattr(
        "tac_validate.overlay_check.check_tac_policy_overlay_dir",
        lambda *_a, **_k: (_ for _ in ()).throw(PolicyError("bad")),
    )
    with pytest.raises(SystemExit) as exc:
        mod._check_tac_policy(tmp_path)
    assert exc.value.code == 1


def test_check_tac_policy_generic_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "tac_validate.overlay_check.check_tac_policy_overlay_dir",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("x")),
    )
    with pytest.raises(SystemExit) as exc:
        mod._check_tac_policy(tmp_path)
    assert exc.value.code == 1


def test_check_iwxxm_policy_policy_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from iwxxm_validate.policy import PolicyError

    monkeypatch.setattr(
        "iwxxm_validate.overlay_check.check_iwxxm_policy_overlay_dir",
        lambda *_a, **_k: (_ for _ in ()).throw(PolicyError("bad")),
    )
    with pytest.raises(SystemExit) as exc:
        mod._check_iwxxm_policy(tmp_path)
    assert exc.value.code == 1


def test_check_iwxxm_policy_generic_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "iwxxm_validate.overlay_check.check_iwxxm_policy_overlay_dir",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("x")),
    )
    with pytest.raises(SystemExit) as exc:
        mod._check_iwxxm_policy(tmp_path)
    assert exc.value.code == 1


def test_check_profile_binding_resolve_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from tac2iwxxm.profile_resolve import ProfileResolveError

    monkeypatch.setattr(
        "tac2iwxxm.overlay_check.check_profile_overlay_dir",
        lambda *_a, **_k: (_ for _ in ()).throw(ProfileResolveError("bad")),
    )
    with pytest.raises(SystemExit) as exc:
        mod._check_profile_binding(tmp_path)
    assert exc.value.code == 1


def test_check_profile_binding_generic_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "tac2iwxxm.overlay_check.check_profile_overlay_dir",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("x")),
    )
    with pytest.raises(SystemExit) as exc:
        mod._check_profile_binding(tmp_path)
    assert exc.value.code == 1


def test_kind_dir_other_families() -> None:
    for kind, pkg in (
        ("tac-policy", "tac-validate"),
        ("iwxxm-policy", "iwxxm-validate"),
        ("profile-binding", "tac2iwxxm"),
    ):
        valid = REPO_ROOT / "packages" / pkg / "examples" / "overlays" / "valid"
        assert mod.main(["--kind", kind, "--dir", str(valid)]) == 0
