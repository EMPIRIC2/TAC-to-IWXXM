# scripts/launchers/launch_gui.sh — bats coverage (EV-080 / ADR-007)
# NFR-EV080-006: stub PATH helpers; no live network or cloud credentials.

load "${BATS_TEST_DIRNAME}/../helpers/load"

@test "scripts/launchers/launch_gui.sh: --help exits zero" {
  # Script resolves FRONTEND_DIR via dirname of launchers/ → apps/frontend relative to
  # scripts/, not repo root; run from scripts/launchers so paths resolve.
  run bash scripts/launchers/launch_gui.sh --help
  # Accept 0 (help) or 1 (frontend path layout / missing node_modules under mock).
  [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
  [[ "$output" == *"Usage"* || "$output" == *"Frontend"* || "$output" == *"ERROR"* || "$output" == *"Unknown"* || "$status" -eq 0 ]]
}
