# T3.4 — PyPI clean-venv install smoke (EV-028 / TC-EV028-003)

**Date**: 2026-08-01  
**Decision**: `D-S035-14d` — skip cosmetic `0.1.3`; smoke against published pins  
**Host**: macOS arm64 · Python 3.12.13 (packages require `>=3.12`)

## Pins

| Package | Pin | Result |
|---------|-----|--------|
| `tac-validate` | `==0.1.1` | installed |
| `iwxxm-validate` | `==0.1.2` | installed (native macOS wheel) |
| `tac2iwxxm` | `==0.1.1` | installed |

## Procedure

```bash
python3.12 -m venv "$SMOKE_DIR/venv"
source "$SMOKE_DIR/venv/bin/activate"
pip install -U pip
pip install 'tac-validate==0.1.1' 'iwxxm-validate==0.1.2' 'tac2iwxxm==0.1.1'
# lint → convert → validate_iwxxm(xsd)
```

Fixture TAC: `packages/tac-validate/tests/fixtures/accept/metar_basic.tac`

## Results

| Check | Result |
|-------|--------|
| `pip` metadata versions | `0.1.1` / `0.1.2` / `0.1.1` |
| `iwxxm_validate.__version__` | `"0.1.1"` (known leftover; next wheel) |
| `rust_available` | `True` |
| `tac_validate.lint` METAR | `ok=True` |
| `tac2iwxxm.convert` | XML len 2614 · IWXXM `2025-2` |
| `validate_iwxxm(..., levels=("xsd",))` | `ok=True` |

**Verdict: PASS** — UJ-023 / TC-EV028-003 install smoke green at published pins.

## Notes

- System `python3` (3.9) cannot install these wheels (`Requires-Python >=3.12`); use 3.12+.
- Cosmetic `__version__` string mismatch deferred per `D-S035-14d`.
