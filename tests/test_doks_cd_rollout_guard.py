"""TC-F30-007 — CD wires DOKS rollout; Render hooks must not hard-fail Deploy."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci-cd.yml"
SCRIPT = ROOT / "scripts" / "deploy" / "doks_rollout_images.sh"


def test_doks_rollout_script_exists_and_targets_three_deploys() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "deploy/metar-api" in text
    assert "deploy/metar-frontend" in text
    assert "deploy/metar-worker" in text
    assert "rollout status" in text


def test_ci_cd_deploy_rolls_doks_with_kube_config() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "doks_rollout_images.sh" in text
    assert "KUBE_CONFIG" in text
    assert "Roll out DOKS images" in text
    # Fail-closed on missing kubeconfig
    assert "Missing required secret KUBE_CONFIG" in text
    # Reject doctl exec plugins (GHA runners lack doctl)
    assert "doctl exec auth" in text


def test_ci_cd_render_hooks_are_optional_non_blocking() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "Optional Render hooks (non-blocking)" in text
    assert "continue-on-error: true" in text
    assert "Enforce backend deploy hook presence" not in text
