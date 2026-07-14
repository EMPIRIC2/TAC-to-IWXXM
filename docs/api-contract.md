# API Contract

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-07-13 (S011 / EV-008 — F7 decode/spans/preview/unified sessions)
> **Delta**: Monorepo M4 auth; F6 tac2iwxxm; F7 operator API (decode, spans, soft-preview, BYO)

## Base URLs

| Environment | Frontend | API (includes auth) |
|-------------|----------|---------------------|
| Local dev | `http://localhost:18000` | `http://localhost:18001` |
| Render | `https://<frontend-host>` | `https://<api-host>` |

**Post-migration change**: Auth endpoints move from separate `:8003` service to same host as backend.
Frontend uses single API base for `/api/v1/*` and `/auth/*`. **`/admin/*` removed** (S011 / #697).

## Services

| Service | Pre-migration | Post-migration |
|---------|---------------|----------------|
| Conversion API | backend:8001 | apps/backend |
| Auth | auth:8003 | apps/backend (packages/auth) |
| Frontend | frontend:5173/8000 | apps/frontend |

## Endpoints

### Health

```
GET /health
```

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "tac2iwxxm_available": true
}
```

**Breaking (F6 cutover)**: `gifts_available` removed; clients must use `tac2iwxxm_available`.
### Authentication (packages/auth — same host post-migration)

```
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
GET  /auth/health
```

**Auth**: Supabase JWT; Bearer token on protected routes.

**Migration note**: Paths preserved for frontend compatibility; proxy config simplified.

### Admin — Removed (S011 / #697)

```
GET  /admin/settings
POST /admin/settings
GET  /admin/all-users
GET  /admin/stats
POST /admin/toggle-admin
GET  /admin/work-sessions
```

**Status**: **Removed** from product surface. Prefer **HTTP 404** (or equivalent not-found) for these
paths. No `is_admin()` caller requirement for routine product APIs. `SUPABASE_SECRET_KEY` remains
Auth Admin / bootstrap scripts only (ADR-010). Operator credentials are **BYO** via deploy env.

---

### Conversion

```
POST /api/v1/convert
```

**Auth**: Required unless `DISABLE_AUTH=true` (dev/CI — G1). Guests may convert when that policy
applies; work-session persistence still requires JWT.

**Request** (multipart/form-data **only** for product/profile — not read from JSON body):

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `files` | no* | — | TAC files |
| `manual_text` | no* | — | TAC string |
| `product` | **yes** | — | `airmet` \| `metar` \| `sigmet` \| `speci` \| `taf` \| `vaa` \| `tca` |
| `profile` | no | `annex3` | `annex3` \| `iwxxm_us` |
| `iwxxm_version` | no | app default | Vendored pin (e.g. `2025-2`) |
| `lint` | no | `true` | Run `tac-validate` before convert (Q14=C) |
| `preview` | no | `false` | Soft-preview mode (S011) — see below |

\* At least one of `files` or `manual_text` required (unchanged).

**Notes**:
- Auto-detect is **UI-side only**; API rejects missing `product` with **400**.
- Sessions may **store** `product`/`profile` in `conversion_params` for UI restore; on submit the UI
  **copies** them into multipart fields.
- No `engine` field; converter is always `tac2iwxxm` after cutover.

**Soft-preview (`preview=true`)** — S011 / #666:

- HTTP **200** allowed when parse/convert is partial; response may include best-effort IWXXM,
  `ok: false`, and `failed_spans: [{ start, end, code?, message? }]`.
- Does **not** imply Schematron-passed publish; hard convert (default) keeps existing failure
  HTTP semantics.
- Prefer this flag over a separate `/preview-convert` route (D-S011-01-api-A).

**S011 spans on convert issues/errors** (when present): optional integer `start` / `end` alongside
existing string fields.
- No metrics object on the response (library/CI only).
- **Single-report only**: WMO AHL **bulletins** use `POST /api/v1/convert-bulletin` (below).

**Response**: `ConversionResponse` — see docs/guides/API.md (shape unchanged).

Each `ConversionResult` includes optional `tac_input` (original TAC echo) for input traceability ([#594](https://github.com/joseph-c-mcguire/metar-to-IWXXM/issues/594)).

**Errors** (F6): Prefer existing `errors` / `issues` arrays; include machine-readable `code` when applicable:

| code | HTTP | When |
|------|------|------|
| `unknown_product` | 400 | Invalid product enum / unsupported |
| `invalid_profile` | 400 | Profile not in enum |
| `missing_iwxxm_us` | 400 | `profile=iwxxm_us` but vendor pin/catalog missing |
| `parse_failed` | 422 | TAC fails product parse |
| `tac_lint_failed` | 422 | Optional when convert path invokes lint (prefer `/lint-tac`) |

Unexpected converter crashes remain **5xx**.

### Bulletin conversion (S008 amend)

```
POST /api/v1/convert-bulletin
```

**Purpose**: Accept a **WMO abbreviated-header (AHL) bulletin** that may contain **multiple**
TAC reports; split; convert each via `tac2iwxxm`. Single-report TAC stays on `/api/v1/convert`.

**Auth**: Same as `/api/v1/convert`.

**Request** (multipart/form-data):

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `files` | no* | — | Bulletin file(s) |
| `manual_text` | no* | — | Bulletin string |
| `product` | **yes** | — | Same enum as convert |
| `profile` | no | `annex3` | `annex3` \| `iwxxm_us` |
| `iwxxm_version` | no | app default | Vendored pin |
| `lint` | no | `true` | When true, run `tac-validate` before each report convert |

* At least one of `files` or `manual_text` required.

**Response** (S008 04 — Q6=A, Q7=C):

```json
{
  "bulletin_meta": {
    "ahl": "SAUS31 KZNY 121200",
    "report_count": 2,
    "tt": "SA",
    "aa": "US",
    "cccc": "KZNY",
    "yygggg": "121200"
  },
  "results": [
    {
      "report_index": 0,
      "ok": true,
      "tac_input": "METAR ...",
      "xml": "<iwxxm:...>",
      "issues": [],
      "fixes": []
    },
    {
      "report_index": 1,
      "ok": false,
      "tac_input": "METAR ...",
      "xml": null,
      "issues": [
        {"severity": "error", "code": "parse_failed", "message": "...", "location": null}
      ],
      "fixes": [
        {"code": "suggest_icao", "message": "Replace XXXX with valid ICAO", "replacement": null}
      ]
    }
  ]
}
```

- **Partial success allowed**: HTTP **200** when split succeeds even if some reports fail;
  callers inspect per-report `ok` / `issues` / `fixes`.
- Must support H7 (TC-LIVE-F6-030).

**Errors** (whole-request): Same codes as convert, plus:

| code | HTTP | When |
|------|------|------|
| `bulletin_split_failed` | 422 | Cannot parse AHL / split reports |
| `empty_bulletin` | 400 | No reports after split |

### TAC lint (S008 amend)

```
POST /api/v1/lint-tac
```

**Purpose**: Thin wrapper over `packages/tac-validate` (parse gate + shared rule pack).
**Not** Schematron.

**Auth**: Same as convert (unless `DISABLE_AUTH=true`).

**Request** (**multipart/form-data only** — Q8=A):

| Field | Required | Description |
|-------|----------|-------------|
| `manual_text` or `files` | yes | TAC text |
| `product` | no | Hint when known; improves rule selection |

**Response** (HTTP pydantic map of msgspec package issues — Q9=C):

```json
{
  "ok": false,
  "issues": [
    {
      "severity": "error",
      "code": "rule_x",
      "message": "...",
      "location": "wind",
      "start": 12,
      "end": 18
    }
  ],
  "fixes": [
    {"code": "normalize_wind", "message": "...", "replacement": "12010KT"}
  ]
}
```

`start` / `end` are optional integer character offsets (S011 / #694/#702). `location` string retained
for back-compat.

Must support TC-F6-031 and TC-F7-004 span highlight.

### Decode TAC (S011 / #702)

```
POST /api/v1/decode-tac
```

**Purpose**: Ordered TAC decode/annotate segments for the Code \| Explanation panel.

**Auth**: Same as convert (unless `DISABLE_AUTH=true`).

**Request** (multipart/form-data; JSON body alternative deferred to 04 if needed):

| Field | Required | Description |
|-------|----------|-------------|
| `manual_text` or `files` | yes | TAC text |
| `product` | yes* | Same enum as convert (*API may accept omit only if 04 specifies auto — default: required) |

**Response**:

```json
{
  "product": "metar",
  "segments": [
    {"start": 0, "end": 5, "code": "METAR", "explanation": "Report type"}
  ],
  "residuals": [
    {"start": 80, "end": 95, "text": "..."}
  ]
}
```

VAA/TCA may be residual-heavy (G4). Must support TC-F7-002.

### Validation

```
POST /api/v1/validate
```

**Implementation**: Thin wrapper over **`packages/iwxxm-validate`** (XSD + Schematron).

**Request**: Existing body/content-type **plus** optional `profile` (`annex3` default |
`iwxxm_us`). When US, validation uses combined WMO + iwxxm-us catalogs.

**Response**: Pass/fail + messages; each issue may include optional integer `start` / `end`
(S011) when the validator can map to TAC or XML offsets — otherwise omit.

### Work sessions (F5+F7 — unified `tac_work_sessions`, ADR-020)

All routes require Bearer JWT unless noted. User routes enforce RLS via caller JWT
(`auth.uid() = user_id`). Storage: **`tac_work_sessions`** after F7.e migration.

```
GET    /api/v1/work-sessions
POST   /api/v1/work-sessions
GET    /api/v1/work-sessions/{id}
PATCH  /api/v1/work-sessions/{id}
DELETE /api/v1/work-sessions/{id}
POST   /api/v1/work-sessions/{id}/restore
```

**Query params** (`GET` list): `status`, `product`, `from`, `to`, `include_deleted` (trash view),
`page`, `limit`. My METARs UI passes `product=metar,speci` (or equivalent filter).

**Request body** (`POST` / `PATCH`):

```json
{
  "title": "optional — default auto ICAO + timestamp",
  "product": "metar",
  "manual_tac": "string",
  "pending_files": [{ "name": "file.tac", "content": "METAR ..." }],
  "converted_results": [],
  "errors": [],
  "issues": [],
  "conversion_params": { "iwxxm_version": "2025-2", "product": "metar", "profile": "annex3" },
  "status": "draft | wip | finished | failed",
  "kv_upload_key": "optional — set on successful send"
}
```

`product` is **required** on create (and when changing product). Prefer top-level `product`
matching `conversion_params.product`.

**Response** (`WorkSession`):

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "product": "metar",
  "status": "draft",
  "title": "KJFK 2026-06-23",
  "manual_tac": "...",
  "pending_files": [],
  "converted_results": [],
  "errors": [],
  "issues": [],
  "conversion_params": {},
  "kv_upload_key": null,
  "deleted_at": null,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

**Status transitions** (server-enforced):

| From | Event | To |
|------|-------|-----|
| — | Auto-save / create | draft |
| draft / failed | Convert success (no send) | wip (**reject if another wip exists — one WIP per user total**) |
| draft / failed | Convert failure | failed |
| wip | Send success | finished (+ kv_upload_key) |
| wip | Send failure | wip (unchanged — user may retry) |
| any | User soft-delete | deleted_at set |
| deleted | Restore within 30 days | deleted_at cleared |

**Admin work-sessions list**: **Removed** (`GET /admin/work-sessions` — see Admin section).

**Guest users**: Work-session routes require JWT. Unauthenticated users may call `/api/v1/convert`
but receive no session persistence until login. On first authenticated request after login, if the
frontend holds unsaved converter state, it **POST**s a new **draft** session from that state before
resume logic runs.

## CORS

| Header | Value |
|--------|-------|
| `Access-Control-Allow-Origin` | Origins from `config.*.api.corsOrigins` |
| `Access-Control-Allow-Methods` | GET, POST, OPTIONS |
| `Access-Control-Allow-Headers` | Authorization, Content-Type |

Preflight: `OPTIONS` on `/api/v1/*` and `/auth/*` (admin paths no longer product surface).

F6/F7 fields do **not** change CORS headers. Frontend and API remain different origins on Render;
configure `config.*.api.corsOrigins` accordingly. Live workbench increases request volume
(debounce/Abort on client — H4–H5 still required).

## Error Format

```json
{
  "detail": "Human-readable message"
}
```

Convert responses may also carry `errors` / `issues` / `failed_spans` with optional `code` /
`start` / `end` (see Conversion). HTTP status codes: 400 / 422 / 5xx as documented for F6; soft-preview
uses **200** with structured partial failure when `preview=true`.

## Frontend Integration

Runtime config via `GET /config.json` (copied from `config/prod.json` at deploy; publishable
key injected from `SUPABASE_PUBLISHABLE_KEY`).

| Config field | Purpose |
|--------------|---------|
| `api.baseUrl` | API + auth base (`/api/v1`, `/auth`) — **no** `/admin` |
| `supabase.url` | Supabase project URL (operator BYO) |
| `supabase.publishableKey` | Client-side Supabase auth (injected at deploy) |

**Deprecated**: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`,
`VITE_APP_URL` — one-release shim during S003 migration.

**Breaking changes (F6 cutover)**:
- Health: `gifts_available` → `tac2iwxxm_available`
- Convert: `product` required; `profile` optional (default `annex3`); multipart-only for those fields
- No gifts dual-run / no `engine` parameter

**Breaking / additive (F7 / S011)**:
- `/admin/*` removed
- `POST /api/v1/decode-tac` added
- `preview` on `/convert`; optional `start`/`end` on lint/validate issues
- Work sessions: top-level `product`; storage `tac_work_sessions`; no admin list

OpenAPI / shared TS codegen remains planned (P1); this contract is the requirements SoT until then.

## References

- docs/guides/API.md (detailed examples — update paths during implementation)
- docs/deploy.md §Integration
- ADR-014; [ADR-015](adr/ADR-015-validate-packages-bulletin-api-f7-f8.md); [ADR-020](adr/ADR-020-unified-tac-work-sessions.md)

### Session changelog

- S008 (2026-07-12): product required; profile; tac2iwxxm_available; validate profile; error codes
- S008 amend (2026-07-12): validate → iwxxm-validate; `POST /api/v1/lint-tac`;
  `POST /api/v1/convert-bulletin` (multi-result TBD 04); `/convert` single-report only
- S008 04 (2026-07-12): bulletin multi-result schema; lint-tac multipart-only; lint default on;
  ADR-016–018
- S011 / EV-008 (2026-07-13): admin removed; decode-tac; spans; convert `preview`; unified
  work-sessions `product` (ADR-020)
