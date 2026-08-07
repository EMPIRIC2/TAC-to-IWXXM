# Build Plan Card — S050 / EV-042

> Updated: 2026-08-07

## Goal

Hide all operator dissemination destinations; add auth-gated mass file/folder ingest;
speed convert/validate churn via queue/keyboard/batch.

## Out of scope

#898 restore; #896 connector; deleting dissemination adapters; DatabaseUploadDialog;
raising global `MAX_REQUEST_BODY_BYTES` to 50 MiB; F8 auto-push.

## Milestones (ordered)

1. **M1** — Hide destinations UI (T1.1–T1.3)
2. **M2** — F33 mass ingest API + FE (T2.1–T2.4)
3. **M3** — Queue/keyboard/batch churn (T3.1–T3.3)
4. **M4** — H4–H5 + verify/deploy stages

## First build batch

After 05 Gate B: start **M1** (T1.1) on `evolve/EV-042-remove-db-tools-operator-throughput`.

**Progress**: M1 complete; M2 (T2.1–T2.4) complete — next **M3** T3.1.

## Risks

- Middleware body limit must exempt/raise only mass route (D-S050-C1)
- Zip-bomb defenses must be tested before enabling large uploads in prod
- Convert&Send removal may break e2e that open dissemination drawer — update/skip operator paths; keep harness
