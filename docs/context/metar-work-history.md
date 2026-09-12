# Context — User METAR Work History (F5)

> **Mode**: scoped | **Slug**: metar-work-history | **Generated**: 2026-06-23  
> **Feature / workflow**: Per-user Supabase-backed workflow log (Draft → WIP → Finished + Failed) | **Status**: active  
> **Session**: S004 / EV-004 (merged with #555 UX + S003 Supabase)

## Executive Summary

Users need a **persisted history log** of METAR work linked to their Supabase auth account — not just ephemeral in-browser results. Each **work session** tracks the full converter batch (manual textarea + queued files), progresses through **Draft → WIP → Finished** (plus **Failed** for convert errors), stores TAC + IWXXM + errors + params, and is resumable on login. **F5** is a new product feature with **Postgres tables**, **backend REST API**, RLS (own data only), compact converter panel + full My METARs page, 30-day TTL on Draft-only rows, soft-delete trash with 30-day restore, and admin read-only browse.

## Resolution Log

| ID | Category | Decision |
|----|----------|----------|
| R1 | Decision | **Status lifecycle**: Draft → WIP → Finished; **Failed** for convert/partial failures |
| R2 | Decision | **Persist trigger**: Auto-save drafts (~3s debounce) + update on Convert / Convert&Send |
| R3 | Decision | **Granularity**: One row per **user session** = manual textarea + pending file queue as a single batch |
| R4 | Decision | **Payload**: Full — TAC, IWXXM (when available), error/warning log, conversion params |
| R5 | Decision | **UI**: Compact history panel on converter **and** separate My METARs page (status + date filters) |
| R6 | Decision | **API**: Backend REST on `apps/backend` (JWT via packages/auth) — not direct Supabase client from browser |
| R7 | Decision | **Admin access**: Existing admin role — **read-only** browse of all users' sessions in v1 |
| R8 | Scope | **Merged into S004 / EV-004** with #555 UX + S003 Supabase (2026-06-23) |
| R9 | Decision | **Session boundary**: Resume most recent non-Finished, non-deleted session on login |
| R10 | Decision | **Multi-METAR**: Multiple lines in one textarea = **one session** (batch convert) |
| R11 | Decision | **Multi-open**: Multiple **Draft** / **Failed** OK; at most **one WIP**; new Draft allowed while WIP open |
| R12 | Decision | **Retention**: Auto-delete **Draft** after **30 days** (Supabase pg_cron); WIP/Finished/Failed until user soft-deletes |
| R13 | Decision | **Schema**: New `metar_work_sessions` table + RLS — not KV upload path |
| R14 | Decision | **Failed behavior**: Stays Failed until user **edits input** and re-converts |
| R15 | Decision | **Session title**: Auto from first METAR ICAO + timestamp; user can rename |
| R16 | Decision | **File storage**: Inline JSONB (name + TAC content) |
| R17 | Decision | **Delete**: Soft-delete; user trash with **30-day restore**, then hard-delete |
| R18 | Decision | **Finished**: Only after successful operational DB send; convert-only stays **WIP** |
| R19 | Decision | **KV linkage**: Finished session stores **`kv_upload_key`** reference from send |
| R20 | Decision | **Auth**: Login required for persistence (RLS per user) |
| R21 | Decision | **Auth**: Login required for persistence (RLS per user); guests may convert without save |
| R22 | Decision | **History model**: Current state on session row — no append-only audit trail in v1 |
| R23 | Decision | **Send failure**: Stay WIP; user retries send |
| R24 | Decision | **Finished reopen**: Read-only view in v1 |
| R25 | Decision | **New session**: Explicit **New METAR** button |
| R26 | Decision | **Sidebar switch**: Load into converter; WIP unchanged in DB |
| R27 | Decision | **Multi-device**: Last-write-wins on auto-save |
| R28 | Decision | **Error log**: In-app panel (#555) + persist on session row |
| R29 | Decision | **Admin UI**: Separate admin page (read-only) |
| R30 | Decision | **Storage**: No explicit size cap in v1 |

## Scope & Constraints

**In scope (F5 / S005)**

- Supabase migration: `metar_work_sessions` with columns per spec.md §F5.
- RLS: `auth.uid() = user_id`; admin SELECT via `is_admin()`; service_role for Draft purge job.
- Backend API: CRUD + upsert + restore; admin read-only list.
- Frontend: debounced draft sync, resume-on-login, sidebar + My METARs page.
- pg_cron: purge Draft rows where `updated_at < now() - 30 days`.
- E2E: login → type → draft → convert → WIP → send → Finished (UJ-004).

**Out of scope (v1)**

- Admin mutate/delete other users' sessions.
- Backfill F5 from existing KV uploads.
- Wiring legacy `conversion_uploads` empty shell tables.

**Linked features**

- **F5** — User METAR work history.
- **F1** — Converter UI integration.
- **M4** — Auth on backend API.

**Relationship to S004 (#555)**

- S004: in-memory UX — replace Results panel, in-app error log panel.
- S005/F5: **durable** history; error log persisted on session row.

## Proposed Status Transitions

```
Login ──► resume most recent non-Finished OR start new Draft
     │
     ▼
Draft ◄── auto-save (3s debounce)
Failed ◄── convert failure (same multi-session rules as Draft)
     │
     │ Convert success (no send)
     ▼
WIP   ◄── at most one per user; IWXXM + errors/issues stored
     │
     │ Send success (Convert&Send or Upload to Database)
     ▼
Finished ◄── kv_upload_key set
```

- Failed → re-convert after user edits input (not while unchanged).
- User may start new Draft while a WIP remains open.

## Unresolved Gaps (for 04-tech-plan / 07-build)

- Exact pg_cron migration SQL and schedule expression.
- Shared TypeScript types location (`packages/shared` vs backend-only schemas).
- Sidebar item count: **5** recent sessions (confirmed EV-004 R11).

## Sources

- Requirements interview — 2026-06-23 (01-requirements F5 delta)
- [Context: issue-555-feedback](issue-555-feedback.md)
- [Docs: feature-list.md §F5](../feature-list.md)
- [Docs: user-journeys.md §UJ-004](../user-journeys.md)
- [Docs: api-contract.md §Work sessions](../api-contract.md)
