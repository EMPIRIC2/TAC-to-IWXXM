# Ops note — Legacy `tac_work_sessions` archive (F21 / E17-5)

**Session**: S023 / EV-017  
**Decision**: E17-5 — no public API to old rows; archive/delete after **~30 days**  
**ADR**: [ADR-031](../adr/ADR-031-public-app-indexeddb-history.md)

## Policy

After the public-app cutover (operator Auth + work-sessions HTTP removed):

1. **No public API** — `/api/v1/work-sessions*` returns 404; browser history is IndexedDB only.
2. **Hold window** — retain legacy Supabase `tac_work_sessions` (and any remaining
   `metar_work_sessions`) rows for approximately **30 days** after production cutover for
   incident recovery / one-time ops export if needed.
3. **Then delete** — drop or truncate the legacy tables (or delete rows) once the hold
   window ends. Do not re-expose them via the product API.

## Operator checklist

| Step | Action |
|------|--------|
| 1 | Confirm cutover deploy: Auth routes + work-sessions HTTP 404; convert public |
| 2 | Record cutover UTC date in the deploy report / this note’s “Cutover” line below |
| 3 | Optional: one-time service-role export of `tac_work_sessions` to cold storage if prod data exists |
| 4 | Calendar reminder: cutover + ~30 days → delete/archive rows |
| 5 | After delete: verify table empty or dropped; no product code path reads it |

## Cutover

| Field | Value |
|-------|-------|
| Cutover date (UTC) | _TBD at deploy (T7.x / 13-deploy-smoke)_ |
| Archive due (UTC) | _cutover + ~30 days_ |
| Export location | _optional — fill if export taken_ |
| Delete confirmed | _pending_ |

## Related

- Env: [env-contract.md](../env-contract.md) — no browser Auth / `E2E_USER_*` for public convert
- Secrets matrix: [staging-secrets-matrix.md](staging-secrets-matrix.md) — F8 service-role only
- Package: `packages/auth` deleted (E17-22); F8 continues on service-role env without it
