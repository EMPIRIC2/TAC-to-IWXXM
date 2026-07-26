# API Contract

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-07-22 (S020 / EV-015 — F20 TAF+SPECI quality; full endpoint review)
> **Delta**: Monorepo M4 auth; F6 tac2iwxxm; F7 operator API; F11 msgspec HTTP (ADR-026);
> F15 registry codes (ADR-028); F20 TAF/SPECI quality (wire shape unchanged)

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

### Serialization boundary (S014 / ADR-026)

| Surface | Runtime | OpenAPI |
|---------|---------|---------|
| High-churn **responses** (`/convert`, `/convert-zip`, `/convert-bulletin`, `/validate`, `/lint-tac`, `/decode-tac`, `/lint-issue-catalog`) | **msgspec** encode (+ optional Struct validate after assemble) | Thin **pydantic** aliases / JSON Schema export — **no** dual runtime validation |
| High-churn **requests** (same routes) | **multipart/form-data** via FastAPI `Form`/`File` (unchanged intake) | Form fields documented as today |
| `/auth/*`, work-sessions, airports, ICAO OPMET stats | **pydantic** | pydantic (unchanged) |

Breaking JSON **response** field changes on high-churn routes are allowed in EV-010; frontend
types update in the same cycle. Prefer additive changes when possible. msgspec does **not**
JSON-decode the raw multipart body (02 S2.M1).

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
| `validate_output` | no | `false` | Run post-convert IWXXM validation when true |
| `validation_level` | no | `basic` | `basic` \| `schema` \| `schematron` \| `icao_opmet` \| `comprehensive` |
| `stop_on_error` | no | `false` | Stop processing remaining inputs after first error |
| `bulletin_id` | no | `""` | Optional bulletin identifier (translation metadata) |
| `issuing_center` | no | `""` | Optional issuing centre ICAO (4-letter) |
| `include_nil_reasons` | no | `true` | Prefer emitting nilReason attributes (engine may still emit NIL shells) |
| `log_level` | no | `INFO` | Minimum severity for process issues echoed to clients |

\* At least one of `files` or `manual_text` required (unchanged).

**Notes**:
- Auto-detect is **UI-side only**; API rejects missing `product` with **400**.
- Sessions may **store** `product`/`profile` in `conversion_params` for UI restore; on submit the UI
  **copies** them into multipart fields.
- No `engine` field; converter is always `tac2iwxxm` after cutover.
- **F7 / ADR-023**: Hard Convert from FileConverter sends `bulletin_id`, `issuing_center`,
  `stop_on_error`, `validate_output`, and `validation_level` from Conversion Parameters.
  Soft-preview forces `validate_output=false`. Operator **Log Level** filters conversion /
  validation / lint process messages (Conversion log + console) and is sent as `log_level`.
  **Include Nil Reasons** maps to `include_nil_reasons` (engine honor TBD).
- **F7 / ADR-024**: AHL bulletin UI uses `/convert-bulletin`. COLLECT / `.gz` uses
  `/ingest-collect` (**501** placeholder). Uploads may be gzip-compressed.

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

Each `ConversionResult` includes optional `tac_input` (original TAC echo) for input traceability ([#594](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/594)).

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

### COLLECT ingest (placeholder — ADR-024)

```
POST /api/v1/ingest-collect
```

**Purpose**: Accept IWXXM COLLECT XML (or gzipped COLLECT). **Currently returns HTTP 501** with
`code=not_implemented` until member extraction + validate ships. Exists so the operator UI can
exercise the path.

**Auth**: Same as `/api/v1/convert`.

**Request** (multipart/form-data): `files` and/or `manual_text`; optional `profile`,
`iwxxm_version`.

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

**Severity values** (S013 / EV-009): `error` | `warning` | `info`. `ok` is computed from
`error`-severity issues only. `MISSING_TERMINATOR` is **`info`** (advisory hint for single
pasted reports; copy: "Reports in bulletins end with '=' — add it before publishing").
The paired fix entry (`code: add_terminator`, `replacement` = text with `=` appended)
powers the UI one-click "Add `=`" quick fix (TC-F10-002).

Must support TC-F6-031 and TC-F7-004 span highlight.

**S015 / EV-011 (F15 / ADR-028)**: HTTP **wire shape unchanged** — clients still receive
`ok`, `issues[]` (`severity`, `code`, `message`, `location`, optional `start`/`end`), and
optional `fixes[]`. New/migrated METAR/SPECI lint `code` values come from the
`tac-validate` issue registry; no new response fields on this route.

### Lint issue catalog (S015 / EV-011 / E11-31)

```
GET /api/v1/lint-issue-catalog
```

**Purpose**: Export the `tac-validate` issue registry for operator UI tooltips and a
lightweight catalog panel (F15). Does **not** change `POST /lint-tac` response shape.

**Auth**: Same as convert / lint-tac (unless `DISABLE_AUTH=true`).

**Query** (optional):

| Param | Required | Description |
|-------|----------|-------------|
| `product` | no | If set, filter rows tagged for that product (e.g. `metar`, `speci`); omit = all |

**Response** (msgspec encode; pydantic OpenAPI alias):

```json
{
  "issues": [
    {
      "code": "MISSING_TERMINATOR",
      "severity": "info",
      "message_template": "Reports in bulletins end with '=' — add it before publishing",
      "product": null,
      "tags": ["terminator", "metar", "speci"]
    }
  ]
}
```

`code` / default `severity` / `message_template` match the registry module. FE uses this for
code tooltips; live lint findings still come from `POST /lint-tac`.

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
  "summary": "Routine METAR for KJFK observed on day 12 at 12:51 UTC. Wind from 180° at 4 kt. Visibility 10 statute miles. Temperature 24 °C, dewpoint 18 °C. Altimeter 30.11 inHg.",
  "segments": [
    {"start": 0, "end": 5, "code": "METAR", "explanation": "Report type (routine meteorological aerodrome report)"},
    {"start": 30, "end": 35, "code": "24/18", "explanation": "Temperature 24 °C, dewpoint 18 °C"}
  ],
  "residuals": [
    {"start": 80, "end": 95, "text": "..."}
  ]
}
```

**S013 / EV-009 (F9)**: `segments[].explanation` is **value-aware** (parsed values, not only
group labels) and `summary` is an additive **deterministic plain-language paragraph** built
from decoded values — present for all seven products (best-effort / "partial decode" wording
for sparse products); when residuals exist the summary ends with a "Not decoded: …" clause.
No offset or field removals — response stays backward-compatible (TC-F9-001/002).

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

## Dissemination (F16–F19) — Planned (S019 / EV-014)

> **Status**: Planned — shapes locked at architecture level (ADR-030 / E14-03=A).
> Exact JSON field names and error codes finalize **before 07-build** (04 batches complete).

Auth: Bearer JWT (same as other `/api/v1/*`). Destination credentials are **memory-only**
(never persisted; never returned in responses). Egress subject to ADR-029 allowlist.

### `POST /api/v1/dissemination/preflight`

| Field | Notes |
|-------|-------|
| Request | JSON: `sink_type` (`postgres` \| `mysql` \| `sqlserver` \| `sqlite` \| `wis2` \| `edis` \| `amhs` \| `swim` \| `afs`) + sink-specific connection params (DB URI or WIS2/EDIS/AMHS fields) + optional `payload` metadata (product, schema version) + `ddl` flag for create-if-missing |
| Success | Structured preflight result: connectivity OK, schema/writer-contract diff (empty when green), optional short-lived opaque `handle` |
| Failure | 400/422 structured errors (allowlist/SSRF, auth to dest, schema mismatch, missing columns); secrets redacted |

### `POST /api/v1/dissemination/send`

| Field | Notes |
|-------|-------|
| Request | JSON: either `handle` from green preflight **or** full sink params again + IWXXM/TAC body (or reference to in-session convert result / drag-drop content) |
| Success | Sink ack + optional `kv_upload_key` metadata for F5 Finished (no dest secrets stored) |
| Failure | Same structured/redacted errors as preflight; block if preflight would not be green |

Encoding: **msgspec** request Struct validation + response encode; thin pydantic OpenAPI
aliases only (E14-07=A / ADR-026). CORS: no new origins; reuse existing
`METAR_CORS_ORIGINS` / `corsOrigins` (H4–H5 when FE drawer ships — E14-10=A).

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
- S013 / EV-009 (2026-07-16): decode-tac additive `summary` + value-aware explanations (F9);
  lint-tac `info` severity + MISSING_TERMINATOR advisory (F10); ADR-025
- S014 / EV-010 (2026-07-18): high-churn routes msgspec runtime (ADR-026); pydantic OpenAPI
  aliases; PyPI packages `tac-validate` / `iwxxm-validate` / `tac2iwxxm` `0.1.0` (F12–F14)
- S015 / EV-011 (2026-07-19): F15 registry — lint-tac **wire shape unchanged**; codes from
  `tac-validate` registry (ADR-028); METAR+SPECI adjacency in UJ-024 / TC-F15;
  **additive** `GET /api/v1/lint-issue-catalog` (E11-31) for FE tooltips/catalog panel
- S019 / EV-014 (2026-07-21): Planned `POST /api/v1/dissemination/preflight` + `/send`
  (ADR-030); F16–F19 sinks; Batch 1 architecture locked (Q32=A)
- S020 / EV-015 (2026-07-22): F20 TAF+SPECI quality — **full endpoint review**; no new routes;
  wire shapes unchanged. `product` enum already includes `taf` \| `speci` on convert /
  convert-bulletin / lint-tac / decode-tac. Registry codes for TAF (+ SPECI deepen) flow through
  existing `lint-tac` + `GET /lint-issue-catalog`. Convert roots `iwxxm:TAF` / `iwxxm:SPECI`
  asserted in goldens (UJ-031 / TC-F20-*). Dissemination routes unchanged (OOS).

## S020 / EV-015 — Endpoint review (F20)

| Endpoint | Change for F20? | Notes |
|----------|-----------------|-------|
| `POST /api/v1/convert` | **None (wire)** | `product=taf` \| `speci` already required enum; quality deepen is package-side |
| `POST /api/v1/convert-bulletin` | **None (wire)** | Per-report product identity for SPECI/TAF in bulletins; TC-F20-006 |
| `POST /api/v1/lint-tac` | **None (wire)** | New TAF (+ SPECI) registry codes in issue payloads; catalog stays source of truth |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | New codes appear in catalog export; response schema unchanged |
| `POST /api/v1/decode-tac` | **None (wire)** | TAF change-group / SPECI value-aware decode already F9 scope; fixtures may expand |
| `POST /api/v1/validate` | **None (wire)** | Round-trip goldens use existing validate levels |
| `POST /api/v1/dissemination/*` | **OOS** | No F16–F19 changes this cycle (E15-6) |
| `/auth/*`, work-sessions | **None** | Unchanged |

**Breaking changes**: None expected. Frontend OpenAPI types update only if catalog/issue
content requires new documented code enums (prefer additive).
