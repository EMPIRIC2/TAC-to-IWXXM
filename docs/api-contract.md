# API Contract

> **Project**: METAR to IWXXM Converter
> **Last updated**: 2026-08-18 (S071 / EV-061 — AHL `INVALID_AHL`; validate decode segments; catalog additive fields)
> **Delta**: Monorepo M4 auth; F6 tac2iwxxm; F7 operator API; F11 msgspec HTTP (ADR-026);
> F15 registry codes (ADR-028); F20 TAF/SPECI quality; **F21 Amended** public convert + optional
> Auth; **F22** privacy; **F30/F31** Auth-only Supabase + DO Postgres work-sessions (ADR-033)

## Base URLs

| Environment | Frontend | API |
|-------------|----------|-----|
| Local dev | `http://localhost:18000` | `http://localhost:18001` |
| DOKS (prod) | `https://app.tac-to-iwxxm.com` | `https://api.tac-to-iwxxm.com` |
| Render (transitional) | `https://<frontend-host>.onrender.com` | `https://<api-host>.onrender.com` |

**EV-031 / F21 Amended**: Frontend uses single API base for `/api/v1/*` **and** `/auth/*`.
Convert/lint/validate/disseminate remain **public** (no JWT). JWT required only for
`/api/v1/work-sessions*`. Guests use IndexedDB; logged-in users use DO Postgres sessions.
`/admin/*` remains **gone** (404).

## Services

| Service | Pre-migration | Post-migration | EV-031 |
|---------|---------------|----------------|--------|
| Conversion API | backend:8001 | apps/backend | Public + abuse controls |
| Auth | auth:8003 | apps/backend (`packages/auth`) | **Restored** (Auth-only Supabase) |
| Frontend | frontend:5173/8000 | apps/frontend | Optional login + guest notice |
| Worker | — | apps/worker | `DATABASE_URL` → DO Postgres |

## Endpoints

### Serialization boundary (S014 / ADR-026)

| Surface | Runtime | OpenAPI |
|---------|---------|---------|
| High-churn **responses** (`/convert`, `/convert-zip`, `/convert-bulletin`, `/validate`, `/lint-tac`, `/decode-tac`, `/lint-issue-catalog`, `/quality-metrics*`) | **msgspec** encode (+ optional Struct validate after assemble) | Thin **pydantic** aliases / JSON Schema export — **no** dual runtime validation |
| High-churn **requests** (same routes) | **multipart/form-data** via FastAPI `Form`/`File` (unchanged intake) | Form fields documented as today |
| `/auth/*`, work-sessions | **pydantic** (restored F31) | pydantic |
| airports, ICAO OPMET stats | **pydantic** | pydantic (unchanged) |

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

### Authentication — Restored (S038 / EV-031 / F31; was Removed F21)

```
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
GET  /auth/health
```

**Status**: **Restored** for optional long-term storage. Supabase Auth issues JWTs; API verifies
via `packages/auth`. Convert/lint/validate/disseminate **do not** require JWT.

**F8**: Worker uses machine/`DATABASE_URL` credentials **off** the operator Auth path (ADR-018
amend / ADR-033).

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

**Auth**: **None** (F21 Amended — public). Abuse controls: per-IP + global rate limits, body/batch
size, timeouts/concurrency (finalize numeric defaults in 04-tech-plan). Guests and operators share
the same public convert path. Work history: guest → IndexedDB; logged-in → separate session APIs.

**Request** (multipart/form-data **only** for product/profile — not read from JSON body):

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `files` | no* | — | TAC files |
| `manual_text` | no* | — | TAC string |
| `product` | **yes** | — | `airmet` \| `metar` \| `sigmet` \| `speci` \| `taf` \| `vaa` \| `tca` \| `swxa` \| `vona` \| `iwxxm` (EV-060 / F7.t — pass-through; no TAC convert) |
| `profile` | no | `annex3` | `annex3` \| `iwxxm_us` |
| `iwxxm_version` | no | SoT default (`2025-2`) | Enum = Python `SUPPORTED_VERSIONS` via generated JSON (`apps/frontend/src/generated/iwxxm_versions.json`; `make export-iwxxm-versions`; #851 / D-S046-sot) |
| `lint` | no | `true` | Run `tac-validate` before convert (Q14=C) |
| `preview` | no | `false` | Soft-preview mode (S011) — see below |
| `validate_output` | no | `false` | Run post-convert IWXXM validation when true |
| `validation_level` | no | `basic` | `basic` \| `schema` \| `schematron` \| `icao_opmet` \| `comprehensive` |
| `stop_on_error` | no | `false` | Stop processing remaining inputs after first error |
| `bulletin_id` | no | `""` | Optional bulletin identifier (translation metadata) |
| `issuing_center` | no | `""` | Optional issuing centre ICAO (4-letter) |
| `include_nil_reasons` | no | `true` | Prefer emitting nilReason attributes (engine may still emit NIL shells) |
| `log_level` | no | `INFO` | Minimum severity for process issues echoed to clients **and** backend/package logger verbosity (EV-060 / #1004). Must not log JWTs, passwords, or Authorization headers at DEBUG. |

\* At least one of `files` or `manual_text` required (unchanged).

**Notes**:
- Auto-detect is **UI-side only**; API rejects missing `product` with **400**.
- Sessions may **store** `product`/`profile` in `conversion_params` for UI restore; on submit the UI
  **copies** them into multipart fields.
- No `engine` field; converter is always `tac2iwxxm` after cutover.
- **Manual entry split**: default is one TAC per non-empty line. For **`product=vaa`**,
  **`tca`**, **`swxa`**, or **`vona`** (F26/F27/F28/F32), `manual_text` is kept as a **single multi-line
  advisory/notice document** (template fields must not be line-split).
- **`product=sigmet`**: package selects `iwxxm:SIGMET` vs `iwxxm:VolcanicAshSIGMET` vs
  `iwxxm:TropicalCycloneSIGMET` from TAC content / designators (WS/WV/WC). **No** separate
  `va_sigmet` / `tc_sigmet` enum values (E19-13=A; EV-029 / #738).
- **`product=swxa`**: Space Weather Advisory → `iwxxm:SpaceWeatherAdvisory` (F28 / #740).
  Canonical wire value is **`swxa`** (not `swx`). Unknown aliases → `unknown_product` **400**.
- **`product=iwxxm` (EV-060 / F7.t / #1003)**: Pass-through. `/convert` and `/convert-bulletin`
  do **not** run TAC→IWXXM; they lint XML (well-formed / COLLECT vs report) and may run F2
  validate. TAC text → structured not-XML error (not METAR lint). `/lint-tac` with
  `product=iwxxm` uses XML lint rules, not TAC product syntax. `/validate` unchanged engine
  (F2); product field documents the pass-through path.
- **`product=vona`**: Volcano Observatory Notice for Aviation →
  `iwxxm:VolcanoObservatoryNoticeForAviation` (F32 / #741). Canonical wire value is **`vona`**.
  Unknown aliases → `unknown_product` **400**.
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
- Does **not** imply Schematron-passed publish; hard convert (default) keeps failure HTTP
  semantics for non-quarantine errors. **EV-023 / TC-EV023-003:** product-shaped unreliable
  TAC emits a successful quarantine document (`@translationFailedTAC`) with HTTP **200**
  (not the soft-preview `ok:false` envelope).
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
| `iwxxm_version` | no | SoT default | Same enum as convert (`iwxxm_versions.json` / #851) |
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
    "yygggg": "121200",
    "bbb": null,
    "report_status": "NORMAL"
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
| `INVALID_AHL` | 400 or 422 | Malformed AHL heading/body (EV-061 / #1012). Prefer this code for operator-facing malformed heading; engine `bulletin_split_failed` / `invalid_bbb` appear as additive `detail.alias` |
| `empty_bulletin` | 400 | No reports after split |

**EV-061 / #1011**: Live/clients must post multipart field **`files`** (not `file`). Contract unchanged; harness fix only.

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

**Auth**: **None** (F21 public) — same as convert.

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

**Auth**: **None** (F21 public) — same as convert / lint-tac.

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
      "tags": ["terminator", "metar", "speci"],
      "source_id": "icao-annex-3",
      "source_url": "https://store.icao.int/",
      "source_attribution": "ICAO Annex 3 (paywall) — citation only; see RULE_SOURCE_URLS / PROVENANCE_MAP"
    }
  ]
}
```

**Additive (S048 / EV-040)**: optional `source_id`, `source_url`, `source_attribution` join
provenance from `PROVENANCE_MAP` so the FE catalog spells out WMO/ICAO/IWXXM sources
(citations/URLs only — no copyrighted Annex prose). Older clients may ignore the fields.

**Additive (S071 / EV-061 / #1014)**: optional fields for operator catalog + IWXXM validation
rows (same route — **no** new endpoint). Older clients ignore extras.

| Field | Required | Notes |
|-------|----------|-------|
| `family` | no | `lint` (TAC registry) or `iwxxm` (F2/Schematron-style checks) |
| `source_type` | no | `tier1` \| `tier2` \| `tier3` (`D-S071-links-resolve`) |
| `status` | no | `verified` \| `legacy_alias` \| `semantic_only` |
| `semantic_identifier` | no | e.g. `codes.wmo.int/49-2/…` when href is a verified landing |
| `last_verified` | no | ISO date of last HTTP check |
| `replacement_url` | no | If `source_url` is alias |

Query: optional `family=lint\|iwxxm` in addition to `product`. Operator-visible `source_url`
must be a verified HTTP landing when `status=verified`; do not put planning ids in
`source_attribution` (EV-048).

`code` / default `severity` / `message_template` match the registry module. FE uses this for
code tooltips; live lint findings still come from `POST /lint-tac`.

**Additive (EV-062 / #1017)**: optional fields for Validation Issues Catalog UX + provenance
quality. Older clients ignore extras. **No** new route.

| Field | Required | Notes |
|-------|----------|-------|
| `issue_type` | no | `presence` \| `structure` \| `content` \| `consistency` \| `iwxxm_schema` \| `other` |
| `source_locator` | no | Section / appendix / table / paragraph / page; omit or null when unavailable |
| `source_access` | no | `public` \| `paywall` \| `login` \| `semantic_only` |

Operator-visible `message_template` / description must explain **what** and **why** at the
stated severity and include a natural-language section reference **or** an explicit
unavailable marker (not thin research-only stubs). Prefer public primary `source_url` when a
lawful free citation exists; paywall rows keep `source_access=paywall` and may expose a
public companion via `replacement_url`. Query params may add `issue_type` and
`source_access` filters (additive).

### Quality metrics corpus (S063 / EV-054 / #836 / F7.q)

Public read API for the operator **Quality metrics** tab. Serves **precomputed** official
WMO corpus quality data (match / residuals / lint / validate) generated at fixture/CI time —
not a live re-download of upstream WMO trees and not a per-request full convert pipeline
for the default view (`D-S063-compute=1` + `D-S063-gateA=2`).

**Auth**: **None** (F21 public) — same as convert / lint-issue-catalog.

```
GET /api/v1/quality-metrics
```

**Purpose**: Product-level summary counts + file inventory for the corpus browser.

**Query** (optional):

| Param | Required | Description |
|-------|----------|-------------|
| `product` | no | Filter inventory to one product (e.g. `metar`, `taf`, `sigmet`) |

**Response** (msgspec encode; pydantic OpenAPI alias) — minimum fields:

```json
{
  "generated_at": "2026-08-10T00:00:00Z",
  "iwxxm_pin": "2025-2",
  "summaries": [
    {
      "product": "metar",
      "match_pass": 12,
      "match_fail": 1,
      "residual_nonempty": 0,
      "lint_fail": 0,
      "validate_fail": 0,
      "deferred_gaps": 1
    }
  ],
  "files": [
    {
      "stem": "metar-A3-1",
      "product": "metar",
      "tier": "wmoPass",
      "match_status": "equal",
      "residual_count": 0,
      "lint_error_count": 0,
      "validate_error_count": 0,
      "deferred": false
    }
  ]
}
```

```
GET /api/v1/quality-metrics/{stem}
```

**Purpose**: Per-file detail for the master–detail pane (TAC, official XML, our XML,
match status, residuals, lint issues, validate issues). Unified XML diff is computed
**client-side** from `official_xml` / `converted_xml` (no server `diff` field in v1;
`D-S063-diff=2` + `D-S063-diff-impl`).

**Match semantics (S064 / EV-055 / #982 — `D-S064-normalize=1` / `D-S064-c14n=1` /
`D-S064-c14n-volatile=1`)**:
`match_status` is equality of **W3C C14N** forms of `official_xml` and `converted_xml`
**after** volatile-attribute strip (ADR-032 local-name / UUID-href / `codes.wmo.int` href
rules), then whitespace-only text strip (both sides; shared helper used by the metrics
generator and the FE unified diff — `D-S064-gateA-M1=1`; [Corpus: adr/ADR-035]). Raw
pretty-print or `gml:id` / UUID churn alone must not yield `match_status` fail. Client
unified diff uses the same C14N peers. Precomputed `corpus_metrics` is regenerated to match
(`D-S064-regen=1`). Detail responses may expose both raw and normalized XML (or the UI
normalizes client-side); operator panes **default to normalized** with an explicit override
to un-normalized (`D-S064-gateA-M2=override`). Operator-facing `detail` / chip copy must stay
free of internal doc refs (EV-048). Cycle hard requirements: Schematron enabled for 2025-2
(`D-S064-sch-hard=1`) and `SCHEMA_IMPORT_WARNING` fixed (`D-S064-xsd-hard=1`).

**Path**: `stem` — catalog / fixture stem (e.g. `metar-A3-1`).

**Response** (msgspec; minimum fields):

```json
{
  "stem": "metar-A3-1",
  "product": "metar",
  "tier": "wmoPass",
  "deferred": false,
  "tac": "METAR …=",
  "official_xml": "<?xml …",
  "converted_xml": "<?xml …",
  "match_status": "equal",
  "residuals": [],
  "lint_issues": [],
  "validate_issues": []
}
```

**Errors**: `404` when stem unknown; `503` when precomputed artifact missing at runtime
(misconfigured deploy) — operator-facing `detail` must stay free of internal doc refs
(EV-048).

**Non-goals**: Live upstream WMO fetch; replacing CI matrix jobs; JWT/Supabase for this route.

### Decode TAC (S011 / #702)

```
POST /api/v1/decode-tac
```

**Purpose**: Ordered TAC decode/annotate segments for the Code \| Explanation panel.

**Auth**: **None** (F21 public) — same as convert.

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

**S026 / EV-020 (F9 deepen / ADR-032)**: `segments[].explanation` strings deepen to
**registry-backed English token meanings** (all seven products) plus optional OpenAIP/F3
**names** when resolvable. Response **shape unchanged** (no new required fields); richer
string content only. Optional additive fields require a follow-on api-contract amend in 04
if proven necessary. Glossary is package data (YAML/JSON); see config-spec for optional
override path.

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

**Additive (S071 / EV-061 / #1010)**: optional `segments` / `summary` using the same F9
shape as `POST /decode-tac` when Validate IWXXM still produces a readable decode. Omitted
when there is no decode. FE shows item-by-item rows (parity with TAC products), not a raw
dump. F7.s validate-only and F7.t pass-through stay. Older clients ignore extras.

### Work sessions (F5+F7+F31 — **restored HTTP**; hybrid storage — S038 / EV-031)

**Status**: Server CRUD on `tac_work_sessions` is **restored** for **logged-in** operators
(JWT required). Storage host = **DigitalOcean Postgres** (`DATABASE_URL`). Guests continue to
use IndexedDB only (no server calls while logged out). On login, client **auto-uploads** eligible
local drafts (`D-S038-guest-merge`=2).

```
GET    /api/v1/work-sessions
POST   /api/v1/work-sessions
GET    /api/v1/work-sessions/{id}
PATCH  /api/v1/work-sessions/{id}
DELETE /api/v1/work-sessions/{id}
POST   /api/v1/work-sessions/{id}/restore
```

**Auth**: Bearer JWT (Supabase Auth). Owner isolation by Auth `user_id`. Exact list/query/body
shapes finalize in 04 (historical ADR-020 shapes are the starting point).

**Admin work-sessions list**: Remains removed (`GET /admin/work-sessions`).

**Guest users**: Convert/validate/lint/decode/preview/dissemination without login; history local
+ persistent loss-of-progress notice (UJ-045).

## CORS

| Header | Value |
|--------|-------|
| `Access-Control-Allow-Origin` | Origins from `config.*.api.corsOrigins` |
| `Access-Control-Allow-Methods` | GET, POST, PATCH, DELETE, OPTIONS |
| `Access-Control-Allow-Headers` | Content-Type, Authorization |

Preflight: `OPTIONS` on `/api/v1/*` and `/auth/*`.

Frontend and API may be different origins on DOKS; configure `corsOrigins` accordingly. H4–H5
**required** this cycle after Auth + URL changes.

## Dissemination (F16–F19) — Done (EV-014); multi-select deepen EV-018

> **Status**: Shipped EV-014 (#771/#772). **EV-018 / #785**: UI multi-file selection — **no**
> new batch endpoint; existing single-payload routes reused via N sequential client calls.

Auth: **None** (F21 public — same as other `/api/v1/*`). Destination credentials are
**memory-only** (never persisted; never returned in responses). Egress subject to ADR-029
allowlist. Abuse controls apply (rate limits / body size).

### `POST /api/v1/dissemination/preflight`

| Field | Notes |
|-------|-------|
| Request | JSON: `sink_type` (`postgres` \| `mysql` \| `sqlserver` \| `sqlite` \| `wis2` \| `edis` \| `amhs` \| `swim` \| `afs`) + sink-specific connection params (DB URI or WIS2/EDIS/AMHS fields) + optional `payload` metadata (product, schema version) + `ddl` flag for create-if-missing + **single** IWXXM/TAC body (or in-session/drop reference) |
| Success | Structured preflight result: connectivity OK, schema/writer-contract diff (empty when green), optional short-lived opaque `handle` |
| Failure | 400/422 structured errors (allowlist/SSRF, auth to dest, schema mismatch, missing columns); secrets redacted |

### `POST /api/v1/dissemination/send`

| Field | Notes |
|-------|-------|
| Request | JSON: either `handle` from green preflight **or** full sink params again + **single** IWXXM/TAC body (or reference to in-session convert result / drag-drop content) |
| Success | Sink ack + optional `kv_upload_key` metadata for local Finished (no dest secrets stored) |
| Failure | Same structured/redacted errors as preflight; block if preflight would not be green |

### Multi-file selection (EV-018 / #785) — client contract

| Rule | Notes |
|------|-------|
| API shape | **Unchanged** single-payload preflight/send (E18-5). No `payloads[]` batch endpoint in v1. |
| Client | For selection size N (1…**20**), **interleaved** per file: preflight → send → next (E18-10); continue after failures; aggregate per-file status in the drawer (E18-11). Primary **Disseminate**; optional **Preflight only** (E18-15). |
| Cap | Selection count **≤20**; existing body/size limits still apply per call (E18-6). |
| Candidates | Current-session conversion outputs + dropped files only (E18-4). Sole candidate auto-selected; panel optional (E18-9). |
| Empty | UI disables Disseminate / Preflight-only when selection is empty. |
| Progress | Per-file UI progress (mail→sink graphic or text-only under reduced-motion) — client-only; no API change (E18-13/14). |

Encoding: **msgspec** request Struct validation + response encode; thin pydantic OpenAPI
aliases only (E14-07=A / ADR-026). CORS: no new origins; reuse existing
`METAR_CORS_ORIGINS` / `corsOrigins` (H4–H5 / H6′ for UJ-027–030).

### S050 / EV-042 — Operator UI destinations hidden

Operator Dissemination drawer / Convert&Send destination path is **UI-hidden** (UJ-053).
These `/dissemination/*` routes remain for **harness/tests** until [#898](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/898) restores destinations. No API deletion this cycle.

## F33 Secure mass ingest (S050 / EV-042 / #897)

### `POST /api/v1/ingest/mass`

| Field | Notes |
|-------|-------|
| Auth | **Required** JWT (Bearer). Unauthenticated → 401/403. |
| Request | `multipart/form-data`: one or more `files`, and/or a single `.zip`; optional folder client expands to files before upload |
| Caps | ≤**200** files; ≤**5 MiB** each; ≤**50 MiB** total unzipped |
| Guards | MIME/extension allowlist (text/TAC); reject binaries/executables; **content sniff**; **zip-bomb** / excessive nesting reject |
| Success | Per-file results: accepted path/name, rejected reason; items queued for convert/validate client-side |
| Failure | 413 over caps; 400 sniff/zip reject; 401/403 auth |

Guest **small** multi-file convert upload (existing convert multipart) is unchanged and remains public if previously public. Mass folder/zip path is auth-only.

CORS: no new origins; H4–H5 for UJ-051.

## Error Format

```json
{
  "detail": "Human-readable message"
}
```

Convert responses may also carry `errors` / `issues` / `failed_spans` with optional `code` /
`start` / `end` (see Conversion). HTTP status codes: 400 / 422 / 5xx as documented for F6; soft-preview
uses **200** with structured partial failure when `preview=true`.

### Operator-facing OpenAPI and error copy (EV-048 / #951)

Public OpenAPI (path/operation summaries, parameter and schema `description` fields that
feed `/docs` / Redoc) and client-facing `detail` / error messages MUST describe controls and
failures in plain operator language. They MUST NOT cite internal engineering documents or
planning IDs — including `[Corpus:…]`, `ADR-NNN`, `EV-NNN`, `S0NN`, `docs/sessions/`,
`docs/feature-list`, or UJ/TC/GitHub issue numbers used as planning vocabulary.

Developer source comments, test names/docstrings, and standing `docs/` remain free to cite
corpus/ADRs. Automated guard: TC-EV048-002/004/005. [Corpus: api] [Corpus: product §F21]

## Frontend Integration

Runtime config via `GET /config.json` (copied from `config/prod.json` at deploy; publishable
Auth key injected from `SUPABASE_PUBLISHABLE_KEY`).

| Config field | Purpose |
|--------------|---------|
| `api.baseUrl` | API base (`/api/v1` **and** `/auth` — **no** `/admin`) |
| `supabase.url` / `publishableKey` | Optional Auth bootstrap for login UX |

**F21 Amended / F31**: FE may show login for long-term storage; convert works without Auth.
Guest history remains IndexedDB; logged-in history uses work-sessions APIs.

**Deprecated**: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`,
`VITE_APP_URL` — prefer runtime `/config.json`.

**Breaking changes (F6 cutover)**:
- Health: `gifts_available` → `tac2iwxxm_available`
- Convert: `product` required; `profile` optional (default `annex3`); multipart-only for those fields
- No gifts dual-run / no `engine` parameter

**Breaking / additive (F7 / S011)**:
- `/admin/*` removed
- `POST /api/v1/decode-tac` added
- `preview` on `/convert`; optional `start`/`end` on lint/validate issues
- Work sessions: top-level `product`; storage shape from ADR-020

**Breaking (F21 / S023 / EV-017)** — historical:
- Operator Auth / `/auth/*` / JWT gates removed; server sessions → IndexedDB

**Breaking / additive (F30/F31 / S038 / EV-031)**:
- `/auth/*` restored (Supabase Auth-only)
- `/api/v1/work-sessions*` restored (JWT; DO Postgres)
- Convert remains public; TC-F21-auth-gone amended
- Product data plane leaves Supabase DB (ADR-033)

OpenAPI / shared TS codegen remains planned (P1); this contract is the requirements SoT until then.

## References

- docs/guides/API.md (detailed examples — update paths during implementation)
- docs/deploy.md §Integration
- ADR-014; [ADR-015](adr/ADR-015-validate-packages-bulletin-api-f7-f8.md); [ADR-020](adr/ADR-020-unified-tac-work-sessions.md); [ADR-033](adr/ADR-033-platform-independence-auth-do-doks.md)

### Session changelog

- S066 / EV-056 (2026-08-11): F7.q #988 — **no HTTP contract change**. FE shareable route
  `/quality/:stem` + collapsible equal-context hunks consume existing
  `GET /api/v1/quality-metrics` + `/{stem}` (pretty C14N panes from S065).
- S064 / EV-055 (2026-08-11): F7.q #982 — `match_status` = **W3C C14N** equality of official
  vs converted XML; shared generator+FE helper; panes default normalized with override;
  regen corpus metrics; **hard** Schematron enable (#980) + SCHEMA_IMPORT fix (#979).
- S063 / EV-054 (2026-08-10): F7.q #836 — additive public `GET /api/v1/quality-metrics` +
  `GET /api/v1/quality-metrics/{stem}` (precomputed corpus quality; msgspec). Gate A M1
  override (`D-S063-gateA=2`).
- S038 / EV-031 (2026-08-03): F30/F31 — `/auth/*` + work-sessions restored; convert public;
  DO Postgres; ADR-033; amend TC-F21-auth-gone semantics
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
- S024 / EV-018 (2026-07-28): F16 multi-file selection deepen (#785) — **no new routes**;
  document client N-sequential preflight/send + ≤20 selection cap; single-payload request
  shape unchanged (E18-5/E18-6).
- S025 / EV-019 (2026-07-29): F23 SIGMET + VA SIGMET quality — **full endpoint review**; no
  new routes; wire shapes unchanged. `product=sigmet` selects root `iwxxm:SIGMET` vs
  `iwxxm:VolcanicAshSIGMET` from TAC content (E19-13=A). Registry codes flow through existing
  `lint-tac` + `GET /lint-issue-catalog`. Dissemination routes unchanged (OOS).
- S030 / EV-023 (2026-07-30): #800 APAC/codes encode deepen — **no new routes**;
  package-side NSC/nils/`translationFailedTAC`/dual-register/informative translation suite.
  Convert multipart Form (E23-T2): `emit_translation_centre` (bool, default false) + optional
  `translation_centre_designator` / `translation_centre_name` when emit true. Dissemination
  COLLECT multi-version remains F16–F19. Informative suite: soft/xfail in main CI (E23-T4).

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

## S025 / EV-019 — Endpoint review (F23)

| Endpoint | Change for F23? | Notes |
|----------|-----------------|-------|
| `POST /api/v1/convert` | **None (wire)** | `product=sigmet` already required enum; package selects `iwxxm:SIGMET` vs `iwxxm:VolcanicAshSIGMET` from TAC (VA / WV); **no** `va_sigmet` enum (E19-13=A) |
| `POST /api/v1/convert-bulletin` | **None (wire)** | Per-report root identity for general vs VA SIGMET in bulletins; TC-F23-006 |
| `POST /api/v1/lint-tac` | **None (wire)** | New SIGMET (+ VA) registry codes in issue payloads; catalog stays source of truth |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | New codes appear in catalog export; response schema unchanged; **FE catalog panel** adds SIGMET/VA tag filters/copy (E19-17=B amends E19-14) |
| `POST /api/v1/decode-tac` | **None (wire)** | SIGMET/VA best-effort decode already F9 sparse-product scope; fixtures may expand |
| `POST /api/v1/validate` | **None (wire)** | Round-trip goldens use existing validate levels |
| `POST /api/v1/dissemination/*` | **OOS** | No F16–F19 changes this cycle (E19-6) |
| `/auth/*`, work-sessions | **None** | Historical (F21 public era — pre–EV-031); restored F31 |

**Breaking changes**: None expected. Root selection is package-side behavior under existing
`product=sigmet`; FE OpenAPI types update only if catalog/issue content requires new
documented code enums (prefer additive).

## S026 / EV-020 — Endpoint review (F24 / F25 / F9 deepen)

| Endpoint | Change for EV-020? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **None (wire)** | Package-side WMO default golden fidelity (AIRMET + METAR/SPECI/TAF); no new params |
| `POST /api/v1/lint-tac` | **None (wire)** | New AIRMET registry codes in payloads |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | AIRMET codes; schema unchanged |
| `POST /api/v1/decode-tac` | **None (wire)** | Richer explanation strings via glossary; **no new required fields** (ADR-032) |
| `POST /api/v1/validate` | **None (wire)** | Existing levels |
| Airport / OpenAIP (F3) | **Reuse** | Optional name enrichment for decode; miss → designator only |
| `POST /api/v1/dissemination/*` | **OOS** | — |

**Breaking changes**: None. FE Examples catalog is static (no new API).

- S026 / EV-020 (2026-07-29): F24/F25 WMO default goldens + F9 glossary deepen — wire shapes
  unchanged; ADR-032.

## S027 / EV-021 — Endpoint review (F26 / F27)

| Endpoint | Change for EV-021? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **Behavior clarify** | `product=vaa` \| `tca`: `manual_text` kept as one multi-line advisory (not line-split); wire schema unchanged |
| `POST /api/v1/convert-bulletin` | **None (wire)** | Per-report product identity for VAA/TCA in bulletins; TC-F26-006 / TC-F27-006 |
| `POST /api/v1/lint-tac` | **None (wire)** | New VAA/TCA registry codes in issue payloads; catalog stays source of truth |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | New VAA/TCA codes appear in catalog export; response schema unchanged |
| `POST /api/v1/decode-tac` | **None (wire)** | VAA/TCA best-effort decode already F9 sparse-product scope (G4); fixtures may expand |
| `POST /api/v1/validate` | **None (wire)** | Round-trip goldens use existing validate levels |
| `POST /api/v1/dissemination/*` | **OOS** | No F16–F19 changes this cycle |
| `/auth/*`, work-sessions | **None** | Historical (F21 public era — pre–EV-031); restored F31 |

**Breaking changes**: None expected. FE Examples catalog is static (no new API). FE OpenAPI
types update only if catalog/issue content requires new documented code enums (prefer additive).

- S027 / EV-021 (2026-07-30): T6.1 — VAA/TCA `manual_text` multi-line keep-whole for convert
  (TC-F26-005 / TC-F27-005); FE `splitManualEntries` aligned.
- S027 / EV-021 (2026-07-29): F26/F27 VAA+TCA quality — **full endpoint review**; no new
  routes; wire shapes unchanged. ADR-028 deepen (codes only); ADR-032 golden bar.

## S036 / EV-029 — Endpoint review (F28 + eight-family / #823)

| Endpoint | Change for EV-029? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **Additive enum** | Add `product=swxa` → `iwxxm:SpaceWeatherAdvisory`; keep-whole `manual_text` like VAA/TCA. `product=sigmet` also selects **TC SIGMET** root from TAC (#738) |
| `POST /api/v1/convert-bulletin` | **Additive enum** | Same `product` enum; AHL/`T1T2` deepen package-side (FN→LN for SWXA); splitter rules #823 B2 |
| `POST /api/v1/lint-tac` | **Additive enum + codes** | `product=swxa` accepted; new SWXA (+ COM/AHL) registry codes in payloads |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | SWXA/COM codes; response schema unchanged |
| `POST /api/v1/decode-tac` | **Additive enum** | `product=swxa` best-effort decode (F9 G4); TC SIGMET under `sigmet` |
| `POST /api/v1/validate` | **None (wire)** | Existing levels; SWXA/TC SIGMET goldens use same validate path |
| `POST /api/v1/dissemination/*` | **Consume AHL helpers** | No new routes; shared AHL/`T1T2`/filename model for sinks (drawer UI OOS) |
| `/auth/*`, work-sessions | **None** | Historical (F21 public era — pre–EV-031); restored F31 |

**Breaking changes**: None — additive `swxa` only. FE OpenAPI / product pickers must add
`swxa` when F28 unlocks Examples. Runtime enum enforcement lands in 07-build (backend +
packages); until then docs lead.

- S036 / EV-029 (2026-08-01): F28 SWXA `product=swxa` + TC SIGMET under `sigmet`; eight-family
  AHL/COM deepen — **endpoint review**; additive enum; no new routes (`D-S036-E29-M` Q1=2).

## S037 / EV-030 — Endpoint review (F29 + #829/#820 residuals)

| Endpoint | Change for EV-030? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **None (wire)** | No new `product` enum. TC SIGMET remains under `product=sigmet` (EV-029). F29 is CI harness only. |
| `POST /api/v1/convert-bulletin` | **None (wire)** | Unchanged |
| `POST /api/v1/lint-tac` | **Additive content** | New TC SIGMET registry codes (#829) appear in issue payloads when pack lands; schema unchanged |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | TC SIGMET codes; response schema unchanged |
| `POST /api/v1/decode-tac` | **Behavior deepen** | #820 VAA/TCA structured field/forecast decode; response shape unchanged (residuals shrink) |
| `POST /api/v1/validate` | **None (wire)** | Same validate path; matrix harness exercises offline |
| FE Examples / sample menu | **Catalog tier** | #829 may unlock `sigmet-A6-2-TC` (`wmoPass` / `wmoReference` per ADR-032) — **static FE catalog**, no new API route. H4–H5 if FE ships. |
| Dissemination / auth / sessions | **None** | Unchanged |

**Breaking changes**: None. No new product enum. Catalog/menu unlock is FE static data + ADR-032
tier decision (TC-EV030-005); document deferral if unlock does not ship this cycle.

- S037 / EV-030 (2026-08-02): F29 matrices + #829 TC deepen + #820 decode — **endpoint review**;
  lean + API/catalog note (`D-S037-E30-M` Q1=2).

## S040 / EV-032 — Endpoint review (F32 VONA + #835/#808/corpus)

| Endpoint | Change for EV-032? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **Additive enum** | Add `product=vona` → `iwxxm:VolcanoObservatoryNoticeForAviation`; keep-whole `manual_text` like VAA/TCA/SWXA. #835 remains under `product=sigmet` (TC path) |
| `POST /api/v1/convert-bulletin` | **Additive enum** | Same `product` enum; AHL/`T1T2` for VONA when known |
| `POST /api/v1/lint-tac` | **Additive enum + codes** | `product=vona` accepted; new VONA registry codes in payloads |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | VONA codes; response schema unchanged |
| `POST /api/v1/decode-tac` | **Additive enum** | `product=vona` best-effort decode (F9 G4) |
| `POST /api/v1/validate` | **None (wire)** | Existing levels; VONA / A6-2-TC goldens use same validate path |
| FE product picker / Examples | **Full F7 surface** | Add **VONA** to picker; unlock Examples when F32 golden greens (`D-S040-E32-M` Q2=3). #835 may promote A6-2-TC → `wmoPass` (static catalog). H4–H5 when FE ships |
| Dissemination / auth / sessions | **None** | Unchanged |

**Breaking changes**: None — additive `vona` only. FE OpenAPI / product pickers must add
`vona` when F32 ships. Runtime enum enforcement lands in 07-build (backend + packages);
until then docs lead. #808 is docs/checklist only (no wire change).

- S040 / EV-032 (2026-08-04): F32 VONA `product=vona` + full F7 surface; #835 catalog tier;
  #808 docs — **endpoint review**; full pack (`D-S040-E32-M` Q1=2).

## S071 / EV-061 — Endpoint review (pre-promote UX + catalog + AHL)

| Endpoint | Change for EV-061? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **None (wire)** | Unchanged |
| `POST /api/v1/convert-bulletin` | **Additive codes** | `INVALID_AHL` for malformed heading (`detail.alias` = `bulletin_split_failed`); `files` field already required (#1011 harness). Decode/convert e2e is #1012 |
| `POST /api/v1/lint-tac` | **None (wire)** | Unchanged |
| `GET /api/v1/lint-issue-catalog` | **Additive fields + content** | IWXXM validation rows (`family=iwxxm`); `source_type` / `status` / `semantic_identifier` / `last_verified` / `replacement_url`. No new route. #1014 |
| `POST /api/v1/decode-tac` | **None (wire)** | AHL bulletins reuse this route: bulletin framing + per-report segments (#1012) |
| `POST /api/v1/validate` | **Additive optional** | `segments` / `summary` (F9 shape) when Validate IWXXM still produces decode (#1010) |
| FE catalog tab | **New page** | Top-level nav; consumes catalog GET; H4–H5 when FE ships |
| FE Product/Profile bars | **None (HTTP)** | Layout only (#1013) |
| Dissemination / auth / sessions | **None** | Unchanged |
| CI promote | **N/A HTTP** | #1015 required checks — not an API change |

**Breaking changes**: None required. Additive fields only (`D-S071-api`). `INVALID_AHL` is the operator-facing convert-bulletin code for malformed heading; `bulletin_split_failed` is retained as `detail.alias` (`D-S071-ahl-code`).

- S071 / EV-061 (2026-08-18): #1010–#1015 endpoint review (`D-S071-api`).

## EV-062 — Endpoint review (Validation Issues Catalog / #1017)

| Endpoint | Change for EV-062? | Notes |
|----------|--------------------|-------|
| `GET /api/v1/lint-issue-catalog` | **Additive fields + content** | `issue_type`, `source_locator`, `source_access`; richer `message_template`s; optional query `issue_type` / `source_access`. No new route |
| `POST /api/v1/lint-tac` | **None (wire)** | Codes/severity unchanged; message text may deepen via registry |
| FE Validation Issues Catalog | **UX deepen** | Rename; type + multi-filter/sort; locator + access display |
| Dissemination / auth / sessions / convert / validate | **None** | Unchanged |

**Breaking changes**: None. Additive only (`D-EV062-api`).

- EV-062 (2026-08-20): #1017 Validation Issues Catalog deepen.
