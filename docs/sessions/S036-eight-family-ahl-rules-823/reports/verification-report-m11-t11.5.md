# Verification — M11 T11.5 (`product=swxa` runtime)

**Cycle**: S036 / EV-029 · **Branch**: `evolve/EV-029-eight-family-ahl-rules`

## Scope

| Change | Result |
|--------|--------|
| `normalize_api_product` | Accepts `swxa`; rejects `swx` / unknown with `unknown_product` **400** |
| Multiline keep-whole | SWXA added (backend + FE) |
| Decode | SWXA in sparse/best-effort set |
| Work sessions | CHECK migration + shared/FE product type |
| Tests | `test_tc_f28_swxa_product_enum.py` + helpers |

## Checks

- `make validate-fast` — pass
- Backend unit (T11.5 + t82 unknown_product) — 13 passed
- Vitest `tacProduct.test.ts` — 13 passed
- Prior tip CI (T11.3/T11.4 @ `19915e2`) — CI/CD Pipeline **success**

## Next

- **T11.6** — `swxa-quality.yml`
- **T11.7** — product-path smoke / Examples unlock when ready
