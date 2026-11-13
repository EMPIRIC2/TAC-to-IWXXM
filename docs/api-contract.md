# API Contract

> **Project**: TAC to IWXXM
> **Last updated**: 2026-11-10
> **Delta**: Monorepo auth in API auth. general TAC conversion tac2iwxxm. operator workbench operator API. validation performance msgspec HTTP.
> METAR and SPECI quality bar registry codes. TAF and SPECI quality bar TAF/SPECI quality. public operator app Amended public convert + optional
> Auth. privacy preference center privacy. platform independence/hybrid operator sessions Auth-only Supabase + DO Postgres work-sessions

## How to read this document

This file is the **HTTP API** corpus. It records request and
response shapes, auth rules, and known quirks for the backend in `apps/backend`.

| Source | Authority |
|--------|-----------|
| Committed [api/openapi.json](api/openapi.json) / [api/openapi.yaml](api/openapi.yaml) | Machine-readable contract (refresh with `make openapi-refresh`) |
| Live OpenAPI `GET {API}/openapi.json` | Which routes are mounted in that environment |
| This document | Contracts, field tables, and migration notes |
| When they disagree | Prefer OpenAPI, then a decision interview before you patch callers |

**Auth model (public operator app Amended / hybrid operator sessions):** Convert, lint, validate, and disseminate stay
**public** (no JWT). A JWT is required only for `/api/v1/work-sessions*`. Guests
use IndexedDB. Logged-in users use DigitalOcean Postgres sessions. `/admin/*`
remains **gone** (404). The frontend uses one API base for `/api/v1/*`.
Operator login/register uses Supabase Auth in the browser (`@supabase/supabase-js`);
the API verifies JWTs via JWKS in `packages/auth` for work-sessions only.

Sections below start with **Base URLs**, then **Services**, then per-endpoint
tables. Code samples and JSON schemas in those sections are normative. do not
rewrite them casually.

## Base URLs

| Environment | Frontend | API |
|-------------|----------|-----|
| Local dev | `http://localhost:18000` | `http://localhost:18001` |
| DOKS (prod) | `https://app.tac-to-iwxxm.com` | `https://api.tac-to-iwxxm.com` |
| DOKS (staging) | `https://app.staging.tac-to-iwxxm.com` | `https://api.staging.tac-to-iwxxm.com` |

## Services

| Service | Pre-migration | Post-migration | |
|---------|---------------|----------------|--------|
| Conversion API | backend:8001 | apps/backend | Public + abuse controls |
| Auth | auth:8003 | FE `@supabase/supabase-js` + BE JWKS (`packages/auth`) | **Auth-only Supabase** (no `/auth/*` proxy) |
| Frontend | frontend:5173/8000 | apps/frontend | Optional login + guest notice |
| Worker | — | apps/worker | `DATABASE_URL` → DO Postgres |

## Endpoints

### Serialization boundary 

| Surface | Runtime | OpenAPI |
|---------|---------|---------|
| High-churn **responses** (`/convert`, `/convert-zip`, `/convert-bulletin`, `/validate`, `/lint-tac`, `/decode-tac`, `/lint-issue-catalog`, `/quality-metrics*`) | **msgspec** encode (+ optional Struct validate after assemble) | Thin **pydantic** aliases / JSON Schema export , **no** dual runtime validation |
| High-churn **requests** (same routes) | **multipart/form-data** via FastAPI `Form`/`File` (unchanged intake) | Form fields documented as today |
| work-sessions | **pydantic** (hybrid operator sessions; JWT via JWKS) | pydantic |
| airports, ICAO OPMET stats | **pydantic** | pydantic (unchanged) |

Breaking JSON **response** field changes on high-churn routes are allowed in. frontend
types update in the same cycle. Prefer additive changes when possible. msgspec does **not**
JSON-decode the raw multipart body (02 S2.monorepo layout).

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

**Breaking (general TAC conversion cutover)**: `gifts_available` removed; clients must use `tac2iwxxm_available`.

### Authentication (hybrid operator sessions — FE-direct)

Operator login, register, email confirm, logout, and password reset run in the
browser against Supabase Auth (`@supabase/supabase-js`). The API does **not**
mount `/auth/*` proxy routes.

The backend verifies access tokens with JWKS (`packages/auth`) for
`/api/v1/work-sessions*` only. Convert/lint/validate/disseminate stay public
(no JWT). Use **`GET /health`** for liveness.

**ingest worker**: Worker uses machine/`DATABASE_URL` credentials **off** the
operator Auth path.

### Admin , Removed 

```
GET /admin/settings
POST /admin/settings
GET /admin/all-users
GET /admin/stats
POST /admin/toggle-admin
GET /admin/work-sessions
```

**Status**: **Removed** from product surface. Prefer **HTTP 404** (or equivalent not-found) for these
paths. No `is_admin` caller requirement for routine product APIs. `SUPABASE_SECRET_KEY` remains
Auth Admin / bootstrap scripts only. Operator credentials are **BYO** via deploy env.

---

### Conversion

```
POST /api/v1/convert
```

**Auth**: **None** (public operator app Amended. public). Abuse controls: per-IP + global rate limits, body/batch
size, timeouts/concurrency (finalize numeric defaults in ). Guests and operators share
the same public convert path. Work history: guest → IndexedDB. logged-in → separate session APIs.

**Request** (multipart/form-data **only** for product/profile. not read from JSON body):

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `files` | no* | — | TAC files |
| `manual_text` | no* | — | TAC string |
| `product` | **yes** | — | `airmet` \| `metar` \| `sigmet` \| `speci` \| `taf` \| `vaa` \| `tca` \| `swxa` \| `vona` \| `iwxxm` (operator workbench , pass-through; no TAC convert) |
| `profile` | no | `annex3` | `annex3` \| `iwxxm_us` , **legacy**; see [ / semantic and exchange profiles proposed wire](#ev-063--f35-proposed-semantic--exchange-wire-not-implemented-until-build-gate) |
| `iwxxm_version` | no | SoT default (`2025-2`) | Enum = Python `SUPPORTED_VERSIONS` via generated JSON (`apps/frontend/src/generated/iwxxm_versions.json`; `make export-iwxxm-versions`; / D-) |
| `lint` | no | `true` | Run `tac-validate` before convert (Q14=C) |
| `preview` | no | `false` | Soft-preview mode , see below |
| `strict` | no | `false` | Strict raise master. Off: client raises critical and error only. On: full ladder and drives validate when `strict_validate` |
| `strict_lint` | no | `true` | When `strict`, include TAC lint in raised set |
| `strict_convert` | no | `true` | When `strict`, include convert findings in raised set |
| `strict_validate` | no | `true` | When `strict`, include IWXXM validation in raised set and enable post-convert validation |
| `validate_output` | no | `false` | Run post-convert IWXXM validation when true |
| `validation_level` | no | `basic` | `basic` \| `schema` \| `schematron` \| `icao_opmet` \| `comprehensive` |
| `stop_on_error` | no | `false` | Stop processing remaining inputs after first error |
| `bulletin_id` | no | `""` | Optional bulletin identifier (translation metadata) |
| `issuing_center` | no | `""` | Optional issuing centre ICAO (4-letter) |
| `include_nil_reasons` | no | `true` | Prefer emitting nilReason attributes (engine may still emit NIL shells) |
| `log_level` | no | `INFO` | Minimum severity for process issues echoed to clients **and** backend/package logger verbosity. Must not log JWTs, passwords, or Authorization headers at DEBUG. |
| `bulletin_date` | no | current UTC date | `YYYY-MM-DD`. Year and month for TAC day-of-month stamps. A day that cannot fall in that month fails conversion. The message names the day and the month. |
| `propagate_residuals_to_remarks` | no | *(profile default; annex3/ICAO_2025 → `false`)* | : when resolved `true` **and** the semantic profile already emits remarks / `humanReadableText` (`iwxxm_us`, `ca_eccc`, …), append decode residual token text (excluding spans already covered by remarks retain) into that emit path and emit info `ConvertIssueRESIDUALS_PROPAGATED_TO_REMARKS`. On **annex3**, there is no XML remarks/HRT target , do not invent free-text remarks; when flag is on and residuals exist, still emit info `RESIDUALS_PROPAGATED_TO_REMARKS` whose message documents **no XML target** (quality-metrics `residuals_propagated_to_remarks` remains false). When `false` or resolved off, residuals stay diagnostic-only ( unchanged). Omitted → semantic-profile default (wire shipped; only annex3/ICAO_2025 defaults defined this cycle = off). Explicit `true`/`false` overrides profile default. Same field on `/convert-zip`. Operator UI: plain-language toggle (no planning ids). |

\* At least one of `files` or `manual_text` required (unchanged).

**Notes**:
- Auto-detect is **UI-side only**. API rejects missing `product` with **400**.
- Sessions may **store** `product`/`profile` in `conversion_params` for UI restore. on submit the UI
 **copies** them into multipart fields.
- No `engine` field; converter is always `tac2iwxxm` after cutover.
- **Manual entry split**: default is one TAC per non-empty line. For **`product=vaa`**,
 **`tca`**, **`swxa`**, or **`vona`** (VAA quality bar/TCA quality bar/SWXA quality bar/VONA quality bar), `manual_text` is kept as a **single multi-line
 advisory/notice document** (template fields must not be line-split).
- **`product=sigmet`**: package selects `iwxxm:SIGMET` vs `iwxxm:VolcanicAshSIGMET` vs
 `iwxxm:TropicalCycloneSIGMET` from TAC content / designators (WS/WV/WC). **No** separate
 `va_sigmet` / `tc_sigmet` enum values (=A).
- **`product=swxa`**: Space Weather Advisory → `iwxxm:SpaceWeatherAdvisory` (SWXA quality bar).
 Canonical wire value is **`swxa`** (not `swx`). Unknown aliases → `unknown_product` **400**.
- **`product=iwxxm` (operator workbench)**: Pass-through. `/convert` and `/convert-bulletin`
 do **not** run TAC→IWXXM. they lint XML (well-formed / COLLECT vs report) and may run IWXXM validation
 validate. TAC text → structured not-XML error (not METAR lint). `/lint-tac` with
 `product=iwxxm` uses XML lint rules, not TAC product syntax. `/validate` unchanged engine
 (IWXXM validation). product field documents the pass-through path. **:** on `POST /api/v1/convert`,
 when the uploaded IWXXM line differs from the requested `iwxxm_version`, the backend migrates
 only **supported** pairs per
 [CROSS_VERSION_CONVERSION.md](domain/iwxxm/CROSS_VERSION_CONVERSION.md) (currently
 **2023-1 → 2025-2** lossy), rewrites namespace/schema references, and validates the
 migrated output before returning success. Unsupported pairs (e.g. **2025-2 → 2023-1**)
 fail closed with HTTP **400** and issue code `UNSUPPORTED_IWXXM_MIGRATION`.
- **`product=vona`**: Volcano Observatory Notice for Aviation →
 `iwxxm:VolcanoObservatoryNoticeForAviation` (VONA quality bar). Canonical wire value is **`vona`**.
 Unknown aliases → `unknown_product` **400**.
- **operator workbench / **: Hard Convert and live IWXXM preview share one params-bar mapping
 (`convertFieldsFromParamsBar`). Both send `bulletin_id`, `issuing_center`,
 `stop_on_error`, `validate_output`, `validation_level`, `include_nil_reasons`,
 `log_level`, `report_variant`, library ids, and `propagate_residuals_to_remarks`.
 Soft-preview and live preview force `validate_output=false` and `validation_level=basic`.
 Operator **Log Level** also filters conversion / validation / lint process messages
 (Conversion log + console). **Include Nil Reasons** maps to `include_nil_reasons`
 (engine honor TBD).
- **operator workbench / **: AHL bulletin UI uses `/convert-bulletin` and forwards
 `propagate_residuals_to_remarks`, `extensions`, and a bearer token when signed in.
 COLLECT / `.gz` uses `/ingest-collect` (**501** placeholder). Uploads may be gzip-compressed.

**Conversion Parameters bar → request fields** (operator workbench):

| Bar control | `POST /convert` (hard and live) | `POST /convert-bulletin` |
| --- | --- | --- |
| Bulletin ID | `bulletin_id` | , (AHL supplies the header) |
| Issuing Center | `issuing_center` | — |
| IWXXM version | `iwxxm_version` | `iwxxm_version` |
| On Error = Fail | `stop_on_error=true` | — |
| Log Level | `log_level` | — |
| Strict | `strict` + step flags; drives `validate_output`/`validation_level` when validate step on (off when preview) | — |
| Include Nil Reasons | `include_nil_reasons` | — |
| Report variant | `report_variant` | — |
| Library selects | matching `*_library_id` | conversion + dissemination ids |
| Residuals → remarks | `propagate_residuals_to_remarks` | `propagate_residuals_to_remarks` |
| Profile extensions | `extensions` | `extensions` |

**Soft-preview (`preview=true`)** :

- HTTP **200** allowed when parse/convert is partial. response may include best-effort IWXXM,
 `ok: false`, and `failed_spans: [{ start, end, code?, message? }]`.
- Does **not** imply Schematron-passed publish. hard convert (default) keeps failure HTTP
 semantics for non-quarantine errors. **:** product-shaped unreliable
 TAC emits a successful quarantine document (`@translationFailedTAC`) with HTTP **200**
 (not the soft-preview `ok:false` envelope).
- Prefer this flag over a separate `/preview-convert` route.

** spans on convert issues/errors** (when present): optional integer `start` / `end` alongside
existing string fields.
- No metrics object on the response (library/CI only).
- **Single-report only**: WMO AHL **bulletins** use `POST /api/v1/convert-bulletin` (below).

**Response**: `ConversionResponse`; see docs/guides/API.md. Additive optional `raised_severities` lists severities raised for the request; all issues stay in `issues[]`. Convert success with IWXXM validation errors stays HTTP 200 with downloadable XML. Convert path failures promote to severity `critical`. IWXXM validation findings stay at `error`. When decode leaves residual TAC tokens, convert and `POST /lint-tac` emit warning code `PARTIAL_DECODE` (registry default warning; not a pack-engine lint emit).

Each `ConversionResult` includes optional `tac_input` (original TAC echo) for input traceability ([](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/594)).

**Errors** (general TAC conversion): Prefer existing `errors` / `issues` arrays; include machine-readable `code` when applicable:

| code | HTTP | When |
|------|------|------|
| `unknown_product` | 400 | Invalid product enum / unsupported |
| `invalid_profile` | 400 | Profile not in enum (semantic or exchange when applicable) |
| `invalid_semantic_profile` | 400 | **Proposed (semantic and exchange profiles)** , unknown `conversion.semanticProfile` |
| `invalid_exchange_profile` | 400 | **Proposed (semantic and exchange profiles)** , unknown `exchange.profile` |
| `deprecated_profile_alias` | — | **Proposed (semantic and exchange profiles)** , not an error; deprecation signal when alias used |
| `missing_iwxxm_us` | 400 | `profile=iwxxm_us` but vendor pin/catalog missing |
| `parse_failed` | 422 | TAC fails product parse |
| `tac_lint_failed` | 422 | Optional when convert path invokes lint (prefer `/lint-tac`) |

Unexpected converter crashes remain **5xx**.

### / semantic and exchange profiles , semantic + exchange wire (Build)

**Status**: **Implemented** on convert/validate/convert-bulletin routes (GIFTs package wire + auth in API metrics).
Legacy flat `profile=` remains as deprecated alias. Optional `PROFILE_WIRE_V2` env toggles
defaults (see env-contract).

**Intent**: Separate **semantic** (TAC→IWXXM) from **exchange** (packaging). Canonical semantic
ids: `ICAO_2025`, `US_FAA_NWS`, `CA_ECCC`, `AU_BOM`, `NZ_CAA_MET` , thin/compat
`UK_METOFFICE`, `BR_DECEA`, `KR_KMA`, `JP_JMA`, `IN_IMD`, `HK_HKO` ( deepen).
**:** `KR_KMA` / `JP_JMA` convert allowlists gain **SPECI**; `IN_IMD` gains tac-validate lint
profile `in_imd` (alias `IN_IMD`) for TAF TX/TN omission **info** awareness. convert stays core IWXXM.
Legacy aliases during deprecation window (until **2026-10-31**,
[](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1025)):

| Alias | Canonical |
|-------|-----------|
| `annex3` | `ICAO_2025` |
| `iwxxm_us` | `US_FAA_NWS` |

**Target request shape** (multipart field names TBD in. may be JSON body on
package-only routes):

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `semantic_profile` | no | `ICAO_2025` (or alias `annex3` during window) | Semantic profile id. **:** workbench Profile control submits this field with **uppercase** OpenAPI ids for all registered canonicals (`ICAO_2025`, `US_FAA_NWS`, `CA_ECCC`, `AU_BOM`, `NZ_CAA_MET`, thin packs); legacy alias option values `annex3` / `iwxxm_us` remain accepted through the window. Prefer this field over deprecated `profile`. ** (hard cut):** after Libraries cutover, Convert **removes** this field; selection is five library asset ids (Conversion / TAC validation / IWXXM validation / Dissemination / Decoding). See amend |
| `report_variant` | no | omitted / auto-detect when profile defines variants | Optional profile-scoped report variant within the selected `product` family. **:** for profiles such as `CA_ECCC`, this refines the IWXXM root / TAC lead without promoting national variants into the global `product` enum. Valid values come from the semantic profile catalog (`metar_family_variants`); mismatches fail closed (for example `product=SPECI` with `report_variant=LWIS`). When omitted and the profile supports variants, convert may resolve the variant from TAC lead and echo the resolved value in response metadata. |
| `iwxxm_version` | no | SoT default | Unchanged , independent of semantic id |
| `extensions` | no | `[]` | Optional national extension tokens (e.g. `IWXXM_US_3`, `IWXXM_CA`). **:** when `IWXXM_CA` is present with `semantic_profile=CA_ECCC`, triggers the full Canadian validation stack (layers 1–5 in [IWXXM_VALIDATION.md](domain/IWXXM_VALIDATION.md) §CA_ECCC validation stages). When omitted, `CA_ECCC` alone selects profile-pinned 3.0.0 core XSD+SCH scaffold (backward compatible). **:** for `product=SIGMET` or `VAA`, Canadian product XSD is not published , layer `ca_xsd` is skipped as not applicable (not an error); WMO 3.0.0 XSD+Schematron still run. |
| `exchange_profile` | no | `GLOBAL_AFS` | Used when **packaging**disseminate-prep invoked; ignored on convert-only. Known wire ids: `GLOBAL_AFS`, `APAC_ROBEX`, `EUR_RODEX`, `AFI`, `CAR_SAM` ( regional stubs share COLLECT baseline). **:** workbench light Exchange control submits this field on package/bulletin paths. |
| `profile` | no | — | **Deprecated** , maps to `semantic_profile` via alias table |

**Nested logical model** (for library / future JSON routes):

```yaml
conversion:
 semanticProfile: US_FAA_NWS
 product: METAR
 reportVariant: LWIS
 iwxxmVersion: "2025-2"
 extensions: [IWXXM_US_3]
exchange:
 profile: GLOBAL_AFS
```

**Behavior**:

- Unknown semantic or exchange id → **400** (hard).
- Alias use → same semantics as canonical id + deprecation signal (response header and/or
 structured field. finalize in Build).
- `report_variant` is only applicable where the selected semantic profile defines variant rows.
 otherwise omit it and expect no resolved-variant metadata.
- Convert response metadata may include resolved `report_variant` when the profile defines
 variants, even if the client omitted the request field and runtime inferred it from TAC lead.
- Exchange profile selects packaging rules only, **not** dissemination drawer through AMHS SWIM AFS adapters sink credentials.
- Milestone 4 follow-on scope includes supported IWXXM-line conversion framing
 ([](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/908)) and operator-sharing surfaces
 ([](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1051)), but sharing must stay limited
 to non-secret profile assets or destination references. convert/lint/validate remain public,
 while mutate/share/manage profile assets remain JWT-gated.
- For `product=iwxxm`, convert response metadata may include `source_iwxxm_version`,
 `target_iwxxm_version`, and `migrated_iwxxm` to describe the pass-through or migration path.

**Observability** (`GET /metrics`, Prometheus):

| Metric | Labels | When incremented |
|--------|--------|------------------|
| `tac_semantic_profile_requests_total` | `route`, `semantic_profile` | Each resolved profile wire on convert/validate/convert-bulletin (`semantic_profile` = canonical id, uppercase) |
| `tac_exchange_profile_requests_total` | `route`, `exchange_profile` | When client supplies explicit `exchange_profile` |
| `tac_semantic_profile_alias_requests_total` | `route`, `semantic_profile` | When a deprecated alias (`annex3`, `iwxxm_us`) was used |

No PII in profile metric labels. Counters are **not** returned on convert JSON responses.

**Corpus**: semantic and exchange profiles/national semantic profiles.. 

### Bulletin conversion ( amend)

```
POST /api/v1/convert-bulletin
```

**Purpose**: Accept a **WMO abbreviated-header (AHL) bulletin** that may contain **multiple**
TAC reports. split. convert each via `tac2iwxxm`. Single-report TAC stays on `/api/v1/convert`.

**Auth**: Same as `/api/v1/convert`.

**Request** (multipart/form-data):

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `files` | no* | — | Bulletin file(s) |
| `manual_text` | no* | — | Bulletin string |
| `product` | **yes** | — | Same enum as convert |
| `profile` | no | `annex3` | `annex3` \| `iwxxm_us` , **legacy**; see [ / semantic and exchange profiles proposed wire](#ev-063--f35-proposed-semantic--exchange-wire-not-implemented-until-build-gate) |
| `iwxxm_version` | no | SoT default | Same enum as convert (`iwxxm_versions.json`) |
| `lint` | no | `true` | When true, run `tac-validate` before each report convert |
| `bulletin_date` | no | current UTC date | Same calendar-date anchor as `/convert`. An impossible day fails conversion with a message that names the day and the month. |
| `propagate_residuals_to_remarks` | no | *(profile default; annex3/ICAO_2025 → `false`)* | Same semantics as `/convert` |

* At least one of `files` or `manual_text` required.

**Response** ( 04: Q6=A, Q7=C):

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

- **Partial success allowed**: HTTP **200** when split succeeds even if some reports fail.
 callers inspect per-report `ok` / `issues` / `fixes`.
- Must support H7 ( TAC conversion-030).

**Errors** (whole-request): Same codes as convert, plus:

| code | HTTP | When |
|------|------|------|
| `bulletin_split_failed` | 422 | Cannot parse AHL / split reports |
| `INVALID_AHL` | 400 or 422 | Malformed AHL heading/body. Prefer this code for operator-facing malformed heading; engine `bulletin_split_failed` / `invalid_bbb` appear as additive `detail.alias` |
| `empty_bulletin` | 400 | No reports after split |

: Live/clients must post multipart field **`files`** (not `file`). Contract unchanged. test setup fix only.

### COLLECT ingest (placeholder , )

```
POST /api/v1/ingest-collect
```

**Purpose**: Accept IWXXM COLLECT XML (or gzipped COLLECT). **Currently returns HTTP 501** with
`code=not_implemented` until member extraction + validate ships. Exists so the operator UI can
exercise the path.

**Auth**: Same as `/api/v1/convert`.

**Request** (multipart/form-data): `files` and/or `manual_text`; optional `profile`,
`iwxxm_version`.

### TAC lint ( amend)

```
POST /api/v1/lint-tac
```

**Purpose**: Thin wrapper over `packages/tac-validate` (parse gate + shared rule pack).
**Not** Schematron.

**Auth**: **None** (public), same as convert.

**Request** (**multipart/form-data only**. Q8=A):

| Field | Required | Description |
|-------|----------|-------------|
| `manual_text` or `files` | yes | TAC text |
| `product` | no | Hint when known; improves rule selection |
| `semantic_profile` | no | Semantic / lint profile id (default `annex3` / `ICAO_2025`) |
| `icao` | no | Optional station ICAO; TAF auto-detects from TAC when omitted. When the caller profile is default annex3/ICAO and the station maps to a national leaf, that leaf is preferred; an explicit national profile wins. |

**Response** (HTTP pydantic map of msgspec package issues. Q9=C):

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

`start` / `end` are optional integer character offsets. `location` string retained
for back-compat.

**Severity values** : `error` | `warning` | `info`. `ok` is computed from
`error`-severity issues only. `MISSING_TERMINATOR` is **`info`** (advisory hint for single
pasted reports. copy: "Reports in bulletins end with '=' , add it before publishing").
The paired fix entry (`code: add_terminator`, `replacement` = text with `=` appended)
powers the UI one-click "Add `=`" quick fix (TC-workbench preview-002).

Must support TC-general TAC conversion-031 and TC-operator workbench-004 span highlight.

**(METAR and SPECI quality bar)**: HTTP **wire shape unchanged**. clients still receive
`ok`, `issues[]` (`severity`, `code`, `message`, `location`, optional `start`/`end`), and
optional `fixes[]`. New/migrated METAR/SPECI lint `code` values come from the
`tac-validate` issue registry. no new response fields on this route.


### Code name dictionary

```
GET /api/v1/code-name-dictionary
```

**Purpose**: Tagged Decoding glossary export for the operator **Code names** shell tab
(product / country / WMO amendment filters). Source of truth is `packages/tac-decoding`
(glossary + catalog meta). **Read-only**. Deepens live decode / Decoding catalog surfaces;
does not invent a new product capability id.

**Auth**: **None** (public operator app), same as `rule-catalogs`.

**Query**:

| Param | Required | Description |
|-------|----------|-------------|
| `q` | no | Case-insensitive substring on code or meaning |
| `product` | no | Product tag (e.g. `METAR`, `SIGMET`) |
| `country` | no | Country tag (e.g. `INTL`, `CA`) |
| `wmo_amendment` | no | Exact amendment / edition label |

**Response** (msgspec): `{ "items": [ … ], "facets": { "products": [], "countries": [], "wmo_amendments": [] } }`.

Item keys: `id`, `code`, `meaning`, `products` (string[]), `countries` (string[]),
`wmo_amendment` (string \| null). Facets are computed from the full dictionary (not the
filtered subset). Operator-facing strings only — no planning ids.

### Rule catalogs 

```
GET /api/v1/rule-catalogs
```

**Purpose**: Family-aware export of package-owned trust catalogs for the five-tab operator
shell (TAC Validation, IWXXM Validation, Conversion, Dissemination, Decoding). Aggregates
Python catalog APIs from owning packages. **Read-only**. The separate **Code names** shell
tab uses `GET /api/v1/code-name-dictionary` rather than overloading this route.

**Auth**: **None** (public operator app public), same as `lint-issue-catalog`.

**Query**:

| Param | Required | Description |
|-------|----------|-------------|
| `family` | yes | `tac` | `iwxxm` | `conversion` | `dissemination` | `decoding` |
| Product / profile filters | no | Family-specific additive filters (reuse lint-issue-catalog profile filters for `tac` / `iwxxm` where applicable) |

**Response** (msgspec): `{ "family": "...", "items": [ … ] }`. operator strings clean.
Common item keys: `id`, `title`, `summary`, `tags?`. Additive optional keys (null/omit when
unknown. clients **must not invent** defaults):

| Field | Families | Notes |
|-------|----------|--------|
| `severity` | all (optional) | Lint levels: `critical` \| `error` \| `warning` \| `info`. Decoding: typically `info` or null |
| `issue_type` | family-specific enums | **TAC / IWXXM / Decoding:** set `presence` \| `structure` \| `content` \| `consistency` \| `iwxxm_schema` \| `other`. Glossary tokens that explain a TAC group/code prefer `content`. **Conversion:** `profile` \| `policy` \| `other` (semantic profiles ship as `profile`; `policy` reserved). **Dissemination:** `profile` \| `other` (exchange profiles ship as `profile`) |
| `source_url` | optional | Prefer public http(s); verified landings only for clickable UI |
| `source_attribution` | optional | Plain-language attribution (no planning ids) |
| `source_access` | optional | `public` \| `paywall` \| `login` \| `semantic_only` |
| `source_locator` | optional | Section/path hint when useful |
| `conform_note` | optional | Plain-language conform statement when evidence exists |

**Compatibility**: `GET /api/v1/lint-issue-catalog` remains during transition as a thin wrapper
or alias for `family=tac` (+ existing IWXXM merge behavior). Lint-issue-catalog query filters
and TAC/IWXXM behavior are **unchanged** by (additive `rule-catalogs` fields only).

: Decoding + Conversion enrichment is additive on this route. no new query
params required for type/level/source (FE may filter client-side per ). H4–H5 only if
Build introduces a breaking wire change beyond additive fields.

### Selection options (TP-YCL-01)

```
GET /api/v1/selection-options?kind=
```

**Purpose**: Lightweight lists for Convert / Send **dropdowns** (deployed first-party
libraries only). Query `kind` ∈ `conversion` | `tac_validation` | `iwxxm_validation` |
`decoding` | `dissemination`. Each option `id` is a first-party `LIB.{KIND}.{NATIONAL}`
asset id. `label` is the asset display name. Unknown `kind` → 400.

Convert chrome uses the four engine kinds (not `dissemination`). Send drawer uses
`dissemination`. Options are public read of non-secret deployed ids.

**Auth**: None (public).

### Library-assets authoring ( , removed)

Operator-facing `GET/POST/PATCH/DELETE /api/v1/profiles/library-assets*` authoring routes and
YAML validate/preview-for-authoring are **removed** at hard cutover. Runtime uses packaged
registries only. Historical contract text below is **superseded** for operator surfaces.

### Lint issue catalog 

```
GET /api/v1/lint-issue-catalog
```

**Purpose**: Export the `tac-validate` issue registry for operator UI tooltips and a
lightweight catalog panel (METAR and SPECI quality bar). Does **not** change `POST /lint-tac` response shape.

**Auth**: **None** (public operator app public), same as convert / lint-tac.

**Query** (optional):

| Param | Required | Description |
|-------|----------|-------------|
| `product` | no | If set, filter rows tagged for that product (e.g. `metar`, `speci`); omit = all |
| `family` | no | `lint` \| `iwxxm` |
| `issue_type` / `source_access` | no | filters (additive) |
| `semantic_profile` | no | , canonical semantic profile id (uppercase OpenAPI ids; legacy aliases accepted if already on convert wire). Omit = all rows (current behavior). When set: return **shared/global ∪ rows applicable to that profile**; national-only codes for other profiles omitted. Unknown id → **400** (`invalid_semantic_profile` style). |
| `exchange_profile` | no | , packaging-context filter only (not dissemination drawer through AMHS SWIM AFS adapters egress). Omit = ignore exchange tagging. When set: include shared ∪ rows tagged for that exchange profile. Unknown id → **400**. |

**Operator UI :** The Validation Issues Catalog may optionally hide
unrestricted (empty-applicability) rows **client-side** when the operator checks
“Only rules that list this profile” and a profile axis is selected. That checkbox does
**not** change this endpoint’s default shared-union query semantics or add a required
query param.

**Response** (msgspec encode. pydantic OpenAPI alias):

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

**Additive **: optional `source_id`, `source_url`, `source_attribution` join
provenance from `PROVENANCE_MAP` so the FE catalog spells out WMO/ICAO/IWXXM sources
(citations/URLs only, no copyrighted Annex prose). Older clients may ignore the fields.

**Additive **: optional fields for operator catalog + IWXXM validation
rows (same route, **no** new endpoint). Older clients ignore extras.

| Field | Required | Notes |
|-------|----------|-------|
| `family` | no | `lint` (TAC registry) or `iwxxm` (IWXXM validation/Schematron-style checks) |
| `source_type` | no | `tier1` \| `tier2` \| `tier3` |
| `status` | no | `verified` \| `legacy_alias` \| `semantic_only` |
| `semantic_identifier` | no | e.g. `codes.wmo.int/49-2/…` when href is a verified landing |
| `last_verified` | no | ISO date of last HTTP check |
| `replacement_url` | no | If `source_url` is alias |

Query: optional `family=lint\|iwxxm` in addition to `product`. Operator-visible `source_url`
must be a verified HTTP landing when `status=verified`. do not put planning ids in
`source_attribution`.

`code` / default `severity` / `message_template` match the registry module. FE uses this for
code tooltips. live lint findings still come from `POST /lint-tac`.

**Additive **: optional fields for Validation Issues Catalog UX + provenance
quality. Older clients ignore extras. **No** new route.

| Field | Required | Notes |
|-------|----------|-------|
| `issue_type` | no | `presence` \| `structure` \| `content` \| `consistency` \| `iwxxm_schema` \| `other` |
| `source_locator` | no | Section / appendix / table / paragraph / page; omit or null when unavailable |
| `source_access` | no | `public` \| `paywall` \| `login` \| `semantic_only` |

Operator-visible `message_template` / description must explain **what** and **why** at the
stated severity and include a natural-language section reference **or** an explicit
unavailable marker (not thin research-only stubs). Prefer public primary `source_url` when a
lawful free citation exists. paywall rows keep `source_access=paywall` and may expose a
public companion via `replacement_url`. Query params may add `issue_type` and
`source_access` filters (additive).

### Quality metrics corpus (operator workbench)

Public read API for the operator **Quality metrics** tab. Serves **precomputed** official
WMO corpus quality data (match / residuals / lint / validate) generated at fixture/CI time,
not a live re-download of upstream WMO trees and not a per-request full convert pipeline
for the default view.

**Auth**: **None** (public operator app public), same as convert / lint-issue-catalog.

```
GET /api/v1/quality-metrics
```

**Purpose**: Product-level summary counts + file inventory for the corpus browser.

**Query** (optional):

| Param | Required | Description |
|-------|----------|-------------|
| `product` | no | Filter inventory to one product (e.g. `metar`, `taf`, `sigmet`) |

**Response** (msgspec encode. pydantic OpenAPI alias), minimum fields:

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

**Purpose**: Per-file detail for the master-detail pane (TAC, official XML, our XML,
match status, residuals, lint issues, validate issues). Unified XML diff is computed
**client-side** from `official_xml` / `converted_xml`. There is no server `diff` field in v1.

**Match semantics**:
`match_status` is equality of **W3C C14N** forms of `official_xml` and `converted_xml`
**after** volatile-attribute strip (local-name / UUID-href / `codes.wmo.int` href
rules), then whitespace-only text strip on both sides. A shared helper serves the metrics
generator and the frontend unified diff. Raw
pretty-print or `gml:id` / UUID churn alone must not yield `match_status` fail. Client
unified diff uses the same C14N peers. Precomputed `corpus_metrics` is regenerated to match.
Detail responses may expose both raw and normalized XML. The UI may also
normalize client-side. Operator panes **default to normalized** with an explicit override
to un-normalized. Operator-facing `detail` / chip copy must stay
free of internal doc refs. Cycle hard requirements: Schematron enabled for 2025-2
and `SCHEMA_IMPORT_WARNING` fixed.

**Path**: `stem`: catalog / fixture stem (for example `metar-A3-1`).

**Response** (msgspec, minimum fields):

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
  "residuals_propagated_to_remarks": false,
  "lint_issues": [],
  "validate_issues": []
}
```

`residuals_propagated_to_remarks` is additive (boolean). Existing
precomputed fixtures default **`false`** until regenerated under an enabled convert flag.
The operator residuals panel must describe fold status in plain language. Do not use planning ids.
This field does not imply live WMO fetch.

**Errors**: `404` when stem unknown. `503` when the precomputed artifact is missing at runtime
(misconfigured deploy). Operator-facing `detail` must stay free of internal doc refs.

**Non-goals**: Live upstream WMO fetch. Replacing CI matrix jobs. JWT or Supabase for this route.

### Decode TAC 

```
POST /api/v1/decode-tac
```

**Purpose**: Ordered TAC decode/annotate segments for the Code \| Explanation panel.

**Auth**: **None** (public), same as convert.

**Request** (multipart/form-data. JSON body alternative is deferred if needed):

| Field | Required | Description |
|-------|----------|-------------|
| `manual_text` or `files` | yes | TAC text |
| `product` | yes* | Same enum as convert (*API may accept omit only if 04 specifies auto , default: required) |

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

**(live decode)**: `segments[].explanation` is **value-aware** (parsed values, not only
group labels) and `summary` is an additive **deterministic plain-language paragraph** built
from decoded values, present for all seven products (best-effort / "partial decode" wording
for sparse products). when residuals exist the summary ends with a "Not decoded: …" clause.
No offset or field removals. response stays backward-compatible (TC-live decode-001/002).

**(live decode deepen)**: `segments[].explanation` strings deepen to
**registry-backed English token meanings** (all seven products) plus optional OpenAIP/airport data services
**names** when resolvable. Response **shape unchanged** (no new required fields). richer
string content only. Optional additive fields require a follow-on api-contract amend in 04
if proven necessary. Glossary is package data (YAML/JSON). see config-spec for optional
override path.

**/ **: Station ICAO explanations and
`summary` include full aerodrome name when the airport lookup hits. miss soft-fails to
ICAO-only text. **No new response keys**.

VAA/TCA may be residual-heavy (G4). Must support TC-operator workbench-002.

### Validation

```
POST /api/v1/validate
```

**Implementation**: Thin wrapper over **`packages/iwxxm-validate`** (XSD + Schematron).

**Request**: Existing body/content-type **plus** optional `profile` (`annex3` default |
`iwxxm_us`). When US, validation uses combined WMO + iwxxm-us catalogs.

**Response**: Pass/fail + messages. each issue may include optional integer `start` / `end`
 when the validator can map to TAC or XML offsets. otherwise omit.

**Additive **: optional `segments` / `summary` using the same live decode
shape as `POST /decode-tac` when Validate IWXXM still produces a readable decode. Omitted
when there is no decode. FE shows item-by-item rows (parity with TAC products), not a raw
dump. operator workbench validate-only and operator workbench pass-through stay. Older clients ignore extras.

### Staged validation + schema status (OpenAPI , thin pointer)

Live OpenAPI also mounts (see `{API}/openapi.json` for request/response schemas):

```
GET /api/v1/validation/layers
POST /api/v1/validation/validate
POST /api/v1/validation/validate-multi
GET /api/v1/schema-status
GET /api/v1/versions
```

These complement `POST /api/v1/validate`. Prefer OpenAPI for field-level detail.

### Evaluation jobs (OpenAPI , thin pointer)

```
GET,POST /api/v1/eval/jobs
GET /api/v1/eval/jobs/{job_id}
GET /api/v1/eval/jobs/{job_id}/results
```

Corpus / quality evaluation surfaces, not part of the public convert happy path. Prefer OpenAPI.

### Work sessions (work history+operator workbench+hybrid operator sessions , **restored HTTP**. hybrid storage ,)

**Status**: Server CRUD on `tac_work_sessions` is **restored** for **logged-in** operators
(JWT required). Storage host = **DigitalOcean Postgres** (`DATABASE_URL`). Guests continue to
use IndexedDB only (no server calls while logged out). On login, client **auto-uploads** eligible
local drafts (=2).

```
GET /api/v1/work-sessions
POST /api/v1/work-sessions
GET /api/v1/work-sessions/{id}
PATCH /api/v1/work-sessions/{id}
DELETE /api/v1/work-sessions/{id}
POST /api/v1/work-sessions/{id}/restore
```

**Auth**: Bearer JWT (Supabase Auth). Owner isolation by Auth `user_id`. Exact list/query/body
shapes finalize in 04 (historical shapes are the starting point).

**Title**: Plain-text only. Create/update strips HTML markup from `title` on write (defense in
depth. UI still renders titles as text nodes). Operators should not rely on stored HTML.

**Admin work-sessions list**: Remains removed (`GET /admin/work-sessions`).

**Guest users**: Convert/validate/lint/decode/preview/dissemination without login. history local
+ persistent loss-of-progress notice.

## CORS

| Header | Value |
|--------|-------|
| `Access-Control-Allow-Origin` | Origins from `config.*.api.corsOrigins` |
| `Access-Control-Allow-Methods` | GET, POST, PATCH, DELETE, OPTIONS |
| `Access-Control-Allow-Headers` | Content-Type, Authorization |

Preflight: `OPTIONS` on `/api/v1/*` and `/auth/*`.

Frontend and API may be different origins on DOKS. configure `corsOrigins` accordingly. H4–H5
**required** this cycle after Auth + URL changes.

## Dissemination (dissemination drawer through AMHS SWIM AFS adapters) , Done. multi-select deepen 

> **Status**: Shipped. : UI multi-file selection , **no**
> new batch endpoint. existing single-payload routes reused via N sequential client calls.

Auth: **None** (public operator app public, same as other `/api/v1/*`). Destination credentials are
**memory-only** (never persisted. never returned in responses). Egress subject to 
allowlist. Abuse controls apply (rate limits / body size).

### `POST /api/v1/dissemination/preflight`

| Field | Notes |
|-------|-------|
| Request | JSON: `sink_type` (`postgres` \| `mysql` \| `sqlserver` \| `sqlite` \| `wis2` \| `edis` \| `amhs` \| `swim` \| `afs`) + sink-specific connection params (DB URI or WIS2/EDIS/AMHS fields) + optional `payload` metadata (product, schema version) + `ddl` flag for create-if-missing + **single** IWXXM/TAC body (or in-session/drop reference) |
| Success | Structured preflight result: connectivity OK, schema/writer-contract diff (empty when green), optional short-lived opaque `handle` |
| Failure | **422** when `sink_type` is omitted/`null` (client error); **501** when `sink_type` is a known drawer value not yet implemented for this route (e.g. `wis2`); 400/403 structured errors (allowlist/SSRF, auth to dest, schema mismatch, missing columns); secrets redacted |

### `POST /api/v1/dissemination/send`

| Field | Notes |
|-------|-------|
| Request | JSON: either `handle` from green preflight **or** full sink params again + **single** IWXXM/TAC body (or reference to in-session convert result / drag-drop content) |
| Success | Sink ack + optional `kv_upload_key` metadata for local Finished (no dest secrets stored) |
| Failure | Same structured/redacted errors as preflight (**422** missing/`nullsink_type` when no valid handle supplies it; **501** unimplemented sink); block if preflight would not be green |

### Multi-file selection , client contract

| Rule | Notes |
|------|-------|
| API shape | **Unchanged** single-payload preflight/send. No `payloads[]` batch endpoint in v1. |
| Client | For selection size N (1…**20**), **interleaved** per file: preflight → send → next ; continue after failures; aggregate per-file status in the drawer. Primary **Disseminate**; optional **Preflight only**. |
| Cap | Selection count **≤20**; existing body/size limits still apply per call. |
| Candidates | Current-session conversion outputs + dropped files only. Sole candidate auto-selected; panel optional. |
| Empty | UI disables Disseminate / Preflight-only when selection is empty. |
| Progress | Per-file UI progress (mail→sink graphic or text-only under reduced-motion) , client-only; no API change (14). |

Encoding: **msgspec** request Struct validation + response encode. thin pydantic OpenAPI
aliases only (=A). CORS: no new origins. reuse existing
`METAR_CORS_ORIGINS` / `corsOrigins` (H4–H5 / H6′ for –030).

### / , Dissemination ops + Gateway hooks (JWT)

Public `POST /dissemination/preflight` + `/send` **unchanged** (public operator app. memory-only BYOC).
New **authenticated** routes (Bearer JWT, same posture as work-sessions):

| Method | Path | Notes |
|--------|------|-------|
| `GET`/`PUT` | `/api/v1/dissemination/plans/{plan_id}` | DisseminationPlan CRUD (policy, transforms, retry, destination refs , **no secrets**) |
| `POST` | `/api/v1/dissemination/plans/{plan_id}/execute` | Execute/dry-run → `DeliveryReceipt[]`; writes audit |
| `GET` | `/api/v1/dissemination/audit` | List/filter (product, station, profile, status); redacted |
| `GET` | `/api/v1/dissemination/audit/{id}` | Detail; never returns BYOC secrets or connection URIs |
| `GET`/`PUT` | `/api/v1/dissemination/mappings/{id}` | MappingConfig CRUD |
| `GET` | `/api/v1/dissemination/gateways/health` | Per-kind `GatewayHealth` (`ok`, `gateway`, `connectivity_ok`, `detail`) |

**Auth**: JWT required → 401/403 without. **Storage**: audit + saved plans/mappings on product
Postgres (`DATABASE_URL`), not Supabase PostgREST. **Egress**: allowlist still applies
when execute triggers send.

### / , ConversionProfile editor + overlays (JWT)

First-party catalog remains fail-closed. New **authenticated** routes for
operator-scoped overlays and rule packs (Bearer JWT, same posture as work-sessions /
dissemination ops). **Storage**: product Postgres (`DATABASE_URL`) with ownership filters,
not Supabase PostgREST product writes (platform independence). Auth identity from Supabase JWT.

| Method | Path | Notes |
|--------|------|-------|
| `GET` | `/api/v1/profiles/catalog` | Read-only ConversionProfile / catalog projection ( fields; no secrets). **additive:** optional `deltas_vs_icao` (≤3 plain-language bullets vs ICAO baseline), `iwxxm_line` / vendor-pin summary for glanceable summary + side-by-side compare; when JWT present, optional `rule_pack_count` / `overlay_count` for the caller. |
| `GET`/`POST`/`PUT`/`DELETE` | `/api/v1/profiles/rule-packs/{id}` | Rule-pack CRUD; export-friendly body |
| `GET`/`POST`/`PATCH`/`DELETE` | `/api/v1/profiles/overlays[/{id}]` | Server-HMAC signed overlays; reject unsigned/tampered |
| `POST` | `/api/v1/convert` (existing) | Optional multipart `overlay_id` (JWT + ownership when set) |

**Auth**: JWT required for pack/overlay mutate → 401/403. **Trust**: unsigned browser packs
rejected. **Non-goals**: credentials / destination URIs in profile objects (029).

### / , Parameterizable conversion templates (JWT)

Deepens operator workbench composable conversion assembly. **Parameterizable templates** are the default
Conversion rule object ( amend). Phase-1: template CRUD + bridge preview +
convert apply. Slot-builder payloads are structured JSON (not raw regex-first).

| Method | Path | Notes |
|--------|------|-------|
| `GET` | `/api/v1/profiles/conversion-templates` | List first-party catalog templates + caller-visible custom templates (JWT enrich for custom) |
| `GET` | `/api/v1/profiles/conversion-templates/{template_id}` | Read one; unknown → fail-closed |
| `POST`/`PATCH`/`DELETE` | `/api/v1/profiles/conversion-templates[/{template_id}]` | Custom CRUD (JWT owner); reject mutate of first-party builtin ids; fork via POST with `fork_of` |
| `POST` | `/api/v1/profiles/conversion-templates/preview` | Bridge preview: TAC (+ optional focus span) + template id → captures + IWXXM block sketch |
| `POST` | `/api/v1/convert` (existing) | Optional `conversion_template_id` (JWT + ownership when custom); unknown → fail-closed |

**Auth**: JWT required for custom mutate / custom apply. **Trust**: first-party view+fork only
in v1. no destination credentials in template bodies (029). **Non-goals (phase-1):**
TAC-validation / dissem / decoding library APIs. workflow authoring.

### / , Library YAML + export metadata (JWT)

Deepens operator workbench Five Libraries with **YAML-backed custom assets** and optional Convert export
sidecars ( amend EVPYL). Extends existing library-assets routes (do not invent a second
profiles tree).

| Method | Path | Notes |
|--------|------|-------|
| `GET`/`POST`/`PATCH`/`DELETE` | `/api/v1/profiles/library-assets[/{asset_id}]` | Existing library asset CRUD; body includes **YAML document** (strict schema on save). Builtins read-only; customs owner-scoped. Draft vs Activated status (Activate = Phase C). |
| `POST` | `/api/v1/profiles/library-assets/preview-rule` | Existing/extended: sample TAC/IWXXM + rule → match/captures / lint / validate / decode / dissem preview as kind allows |
| `POST` | `/api/v1/profiles/library-assets/validate-yaml` | Validate YAML against strict schema + regex compile diagnostics (Warn/Fail) without persist |
| `POST` | `/api/v1/convert` (existing) | Optional `include_conversion_metadata=true` (multipart). When set, response/download packaging includes sibling `*.meta.json` sidecar (not embedded in IWXXM). Single-file downloads return a **ZIP of two** (`xml` + `meta.json`). Guests may omit operator-identity fields; identity fields require JWT. Checklist fields selectable; default all groups when UI toggle on. Never credentials / destination URIs / auth tokens. |

**Auth**: JWT for Profile Builder mutate (signed-in required). Convert metadata toggle may be
used by guests for non-identity fields. operator identity fields require sign-in. **Trust**:
builtins immutable. Dissemination YAML rejects secret/URI fields. **Non-goals**: metadata on
Disseminate path. workflow definition editing on Profiles page.

### / , Workbench + editable libraries (JWT)

Deepens operator workbench beyond : IDE workbench authoring, **no Conversion DnD**, shared numeric
constraint operators, Overview enablement ( amend EVWB). Extends existing
library-assets / validate-yaml routes (do not invent a second profiles tree).

| Method | Path | Notes |
|--------|------|-------|
| `GET`/`POST`/`PATCH`/`DELETE` | `/api/v1/profiles/library-assets[/{asset_id}]` | YAML body supports renamable Conversion slots (unordered); TAC/IWXXM rule objects with `level`, regex, and numeric ops (`min`/`max`/`eq`/`in`, int|float, optional unit); Decoding maps/units/structured types; Dissemination destination/route profiles without secrets/URIs. |
| `POST` | `/api/v1/profiles/library-assets/validate-yaml` | Extended diagnostics for numeric ops + structured decode types + Overview product/file-type/version enablement document when present |
| `POST` | `/api/v1/profiles/library-assets/preview-rule` | Workbench sample preview for lint/validate/decode/convert as kind allows |
| `GET` | `/api/v1/profiles/library-catalogs/{kind}` (existing or extend) | Grouped searchable Conversion catalog (expanded mined set); other kinds as today |
| `GET`/`PATCH` | existing conversion profile / library-assets (embed) | **Recommended (tech-plan):** store Overview enablement + compare inputs as YAML fields on the parent profile / a dedicated `overview` library-asset kind , **no new `/overview` route tree** in P0–P4 unless Build discovers a hard constraint. Compare is computed client-side from two loaded assets + optional BE helper later. |

**Auth**: JWT for mutate. **Trust**: foundation/builtins read-only. Dissemination rejects
secrets/URIs. **Non-goals**: new sink protocols. Convert chrome rewrite. ingest worker auto-push. PyPI
breaks.

### / , Operator sharing of semantic presets + dissemination templates (JWT)

 deepens the existing authenticated profile and dissemination surfaces rather than
creating a public marketplace or a new secret store. Two saved asset classes are allowed:

1. **Semantic preset**: named operator/org-shareable preset that references an existing
 semantic profile id and supported conversion defaults (`iwxxmVersion`, `extensions[]`,
 optional `reportVariant`, optional overlay/rule-pack references).
2. **Dissemination template**: named operator/org-shareable destination reference that stores
 only non-secret sink metadata and any required runtime-field hints.

| Method | Path | Notes |
|--------|------|-------|
| `GET`/`POST` | `/api/v1/profiles/presets` | List/create semantic presets owned by the caller plus rows visible via share rules |
| `GET`/`PATCH`/`DELETE` | `/api/v1/profiles/presets/{preset_id}` | Read/update/delete one semantic preset; unknown or unauthorized ids fail closed |
| `GET`/`POST` | `/api/v1/profiles/templates` | List/create saved dissemination templates (non-secret only) |
| `GET`/`PATCH`/`DELETE` | `/api/v1/profiles/templates/{template_id}` | Read/update/delete one saved template |
| `POST` | `/api/v1/convert` (existing) | Optional saved `preset_id` may resolve conversion defaults before request execution; explicit request fields still win when both are supplied |
| `POST` | `/api/v1/dissemination/preflight` (existing) | Optional `dissemination_template_id` may resolve non-secret sink metadata, but caller still supplies one-shot live credentials/URI material when required |
| `POST` | `/api/v1/dissemination/send` (existing) | Same template resolution rule as preflight; runtime credentials remain memory-only |

**Auth**: mutate/share/manage preset/template rows requires JWT. Convert/lint/validate stay
public when no saved asset id is supplied. **Visibility**: finalized in Build, but must support
owner-scoped and shared reads without exposing PII in metrics labels. **Secret rules**:
saved dissemination templates must reject URIs, DSNs, passwords, API keys, tokens, and
connection strings. semantic presets may store only non-secret conversion defaults and saved
asset references. Work-session hydration may persist `preset_id` and
`dissemination_template_id` as saved-asset references only. it must not persist live
destination credentials or URIs. **Non-goals**: guest sharing, arbitrary uploaded executable
profiles, saved dissemination credentials, or conflating exchange profile ids with destination
state.

### / , Operator UI destinations hidden

Operator Dissemination drawer / Convert&Send destination path is **restored**.
These `/dissemination/*` routes serve operator UI and tests. Drawer convert-before-send
uses workbench/`exchange_profile` overlay. send body itself remains IWXXM/TAC payload
without a separate exchange field.

## mass file ingest Secure mass ingest 

### `POST /api/v1/ingest/mass`

| Field | Notes |
|-------|-------|
| Auth | **Required** JWT (Bearer). Unauthenticated → 401/403. |
| Request | `multipart/form-data`: one or more `files`, and/or a single `.zip`; optional folder client expands to files before upload |
| Caps | ≤**200** files; ≤**5 MiB** each; ≤**50 MiB** total unzipped |
| Guards | MIME/extension allowlist (text/TAC); reject binaries/executables; **content sniff**; **zip-bomb**excessive nesting reject |
| Success | Per-file results: accepted path/name, rejected reason; items queued for convert/validate client-side |
| Failure | 413 over caps; 400 sniff/zip reject; 401/403 auth |

Guest **small** multi-file convert upload (existing convert multipart) is unchanged and remains public if previously public. Mass folder/zip path is auth-only.

CORS: no new origins. H4–H5 for.

## Error Format

```json
{
 "detail": "Human-readable message"
}
```

Convert responses may also carry `errors` / `issues` / `failed_spans` with optional `code` /
`start` / `end` (see Conversion). HTTP status codes: 400 / 422 / 5xx as documented for general TAC conversion. soft-preview
uses **200** with structured partial failure when `preview=true`.

### Operator-facing OpenAPI and error copy 

Public OpenAPI (path/operation summaries, parameter and schema `description` fields that
feed `/docs` / Redoc) and client-facing `detail` / error messages MUST describe controls and
failures in plain operator language. They MUST NOT cite internal engineering documents or
planning IDs, architecture decision numbers, session numbers, paths under `docs/sessions/`, `docs/product-requirements`, or journey, test-case, or GitHub issue numbers used as planning vocabulary.

Developer source comments, test names/docstrings, and standing `docs/` may still cite
internal design notes. Automated guards in the OpenAPI and frontend copy tests enforce this rule.

## Frontend Integration

Runtime config via `GET /config.json` (copied from `config/deploy/profiles/prod.json` at deploy. publishable
Auth key injected from `SUPABASE_PUBLISHABLE_KEY`).

| Config field | Purpose |
|--------------|---------|
| `api.baseUrl` | API base (`/api/v1` **and** `/auth` , **no** `/admin`) |
| `supabase.url` / `publishableKey` | Optional Auth bootstrap for login UX |

**public operator app Amended / hybrid operator sessions**: FE may show login for long-term storage. convert works without Auth.
Guest history remains IndexedDB. logged-in history uses work-sessions APIs.

**Deprecated**: `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_DEFAULT_KEY`,
`VITE_APP_URL`; prefer runtime `/config.json`.

**Breaking changes (general TAC conversion cutover)**:
- Health: `gifts_available` → `tac2iwxxm_available`
- Convert: `product` required; `profile` optional (default `annex3`); multipart-only for those fields
- No gifts dual-run / no `engine` parameter

**Breaking / additive (operator workbench)**:
- `/admin/*` removed
- `POST /api/v1/decode-tac` added
- `preview` on `/convert`; optional `start`/`end` on lint/validate issues
- Work sessions: top-level `product`. storage shape from 

**Breaking (public operator app)** (historical):
- Operator Auth / `/auth/*` / JWT gates removed. server sessions → IndexedDB

**Breaking / additive (platform independence/hybrid operator sessions)**:
- `/auth/*` restored (Supabase Auth-only)
- `/api/v1/work-sessions*` restored (JWT. DO Postgres)
- Convert remains public. TC-public operator app-auth-gone amended
- Product data plane leaves Supabase DB 

OpenAPI / shared TS codegen remains planned (P1). this contract is the requirements SoT until then.

## References

- docs/guides/API.md (detailed examples. update paths during implementation)
- config/deploy/doks/ §Integration
-. [](adr/-validate-packages-bulletin-api-f7-f8.md). [](adr/-unified-tac-work-sessions.md). [](adr/-platform-independence-auth-do-doks.md)

### Session changelog

- (2026-08-31): : additive convert / convert-bulletin
 `propagate_residuals_to_remarks`. quality-metrics detail
 `residuals_propagated_to_remarks`; info issue `RESIDUALS_PROPAGATED_TO_REMARKS`.
- (2026-09-19): : **no HTTP contract change**
 on `/decode-tac`, `/convert`, or `/convert-bulletin`. See endpoint review at file end.
- / (2026-08-11): operator workbench : **no HTTP contract change**. FE shareable route
 `/quality/:stem` + collapsible equal-context hunks consume existing
 `GET /api/v1/quality-metrics` + `/{stem}` (pretty C14N panes from ).
- / (2026-08-11): operator workbench : `match_status` = **W3C C14N** equality of official
 vs converted XML. shared generator+FE helper. panes default normalized with override.
 regen corpus metrics. **hard** Schematron enable + SCHEMA_IMPORT fix.
- / (2026-08-10): operator workbench : additive public `GET /api/v1/quality-metrics` +
 `GET /api/v1/quality-metrics/{stem}` (precomputed corpus quality. msgspec). Gate A monorepo layout
 override.
- / (2026-08-03): platform independence/hybrid operator sessions: `/auth/*` + work-sessions restored. convert public.
 DO Postgres.. amend TC-public operator app-auth-gone semantics
- (2026-07-12): product required. profile. tac2iwxxm_available. validate profile. error codes
- amend (2026-07-12): validate → iwxxm-validate. `POST /api/v1/lint-tac`.
 `POST /api/v1/convert-bulletin` (multi-result TBD 04); `/convert` single-report only
- 04 (2026-07-12): bulletin multi-result schema. lint-tac multipart-only. lint default on.
 –018
- / (2026-07-13): admin removed. decode-tac. spans. convert `preview`. unified
 work-sessions `product` 
- / (2026-07-16): decode-tac additive `summary` + value-aware explanations (live decode).
 lint-tac `info` severity + MISSING_TERMINATOR advisory (workbench preview). 
- / (2026-07-18): high-churn routes msgspec runtime. pydantic OpenAPI
 aliases. PyPI packages `tac-validate` / `iwxxm-validate` / `tac2iwxxm0.1.0` (TAC validate package through published converter packages)
- / (2026-07-19): METAR and SPECI quality bar registry. lint-tac **wire shape unchanged**. codes from
 `tac-validate` registry. METAR+SPECI adjacency in / and SPECI quality bar.
 **additive** `GET /api/v1/lint-issue-catalog` for FE tooltips/catalog panel
- / (2026-07-21): Planned `POST /api/v1/dissemination/preflight` + `/send`
. dissemination drawer through AMHS SWIM AFS adapters sinks. Batch 1 architecture locked (Q32=A)
- / (2026-09-03): Additive JWT routes for plans/execute/audit/mappings/gateway
 health. public preflight/send unchanged. audit on `DATABASE_URL`
- / (2026-07-22): TAF and SPECI quality bar TAF+SPECI quality: **full endpoint review**. no new routes.
 wire shapes unchanged. `product` enum already includes `taf` \| `speci` on convert /
 convert-bulletin / lint-tac / decode-tac. Registry codes for TAF (+ SPECI deepen) flow through
 existing `lint-tac` + `GET /lint-issue-catalog`. Convert roots `iwxxm:TAF` / `iwxxm:SPECI`
 asserted in goldens (and SPECI quality bar-*). Dissemination routes unchanged (OOS).
- / (2026-07-28): dissemination drawer multi-file selection deepen : **no new routes**.
 document client N-sequential preflight/send + ≤20 selection cap. single-payload request
 shape unchanged.
- / (2026-07-29): SIGMET quality bar SIGMET + VA SIGMET quality: **full endpoint review**. no
 new routes. wire shapes unchanged. `product=sigmet` selects root `iwxxm:SIGMET` vs
 `iwxxm:VolcanicAshSIGMET` from TAC content (=A). Registry codes flow through existing
 `lint-tac` + `GET /lint-issue-catalog`. Dissemination routes unchanged (OOS).
- / (2026-07-30): APAC/codes encode deepen: **no new routes**.
 package-side NSC/nils/`translationFailedTAC`/dual-register/informative translation suite.
 Convert multipart Form (E23-T2): `emit_translation_centre` (bool, default false) + optional
 `translation_centre_designator` / `translation_centre_name` when emit true. Dissemination
 COLLECT multi-version remains dissemination drawer through AMHS SWIM AFS adapters. Informative suite: soft/xfail in main CI (E23-T4).

## / , Endpoint review (TAF and SPECI quality bar)

| Endpoint | Change for TAF and SPECI quality bar? | Notes |
|----------|-----------------|-------|
| `POST /api/v1/convert` | **None (wire)** | `product=taf` \| `speci` already required enum; quality deepen is package-side |
| `POST /api/v1/convert-bulletin` | **None (wire)** | Per-report product identity for SPECI/TAF in bulletins; and SPECI quality bar-006 |
| `POST /api/v1/lint-tac` | **None (wire)** | New TAF (+ SPECI) registry codes in issue payloads; catalog stays source of truth |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | New codes appear in catalog export; response schema unchanged |
| `POST /api/v1/decode-tac` | **None (wire)** | TAF change-group / SPECI value-aware decode already live decode scope; fixtures may expand |
| `POST /api/v1/validate` | **None (wire)** | Round-trip goldens use existing validate levels |
| `POST /api/v1/dissemination/*` | **OOS** | No dissemination drawer through AMHS SWIM AFS adapters changes this cycle |
| `/auth/*`, work-sessions | **None** | Unchanged |

**Breaking changes**: None expected. Frontend OpenAPI types update only if catalog/issue
content requires new documented code enums (prefer additive).

## / , Endpoint review (SIGMET quality bar)

| Endpoint | Change for SIGMET quality bar? | Notes |
|----------|-----------------|-------|
| `POST /api/v1/convert` | **None (wire)** | `product=sigmet` already required enum; package selects `iwxxm:SIGMET` vs `iwxxm:VolcanicAshSIGMET` from TAC (VA / WV); **no** `va_sigmet` enum (=A) |
| `POST /api/v1/convert-bulletin` | **None (wire)** | Per-report root identity for general vs VA SIGMET in bulletins; quality bar-006 |
| `POST /api/v1/lint-tac` | **None (wire)** | New SIGMET (+ VA) registry codes in issue payloads; catalog stays source of truth |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | New codes appear in catalog export; response schema unchanged; **FE catalog panel** adds SIGMET/VA tag filters/copy (=B amends ) |
| `POST /api/v1/decode-tac` | **None (wire)** | SIGMET/VA best-effort decode already live decode sparse-product scope; fixtures may expand |
| `POST /api/v1/validate` | **None (wire)** | Round-trip goldens use existing validate levels |
| `POST /api/v1/dissemination/*` | **OOS** | No dissemination drawer through AMHS SWIM AFS adapters changes this cycle |
| `/auth/*`, work-sessions | **None** | Historical (public operator app public era , pre–); restored hybrid operator sessions |

**Breaking changes**: None expected. Root selection is package-side behavior under existing
`product=sigmet`. FE OpenAPI types update only if catalog/issue content requires new
documented code enums (prefer additive).

## / , Endpoint review (AIRMET quality bar / WMO example parity / live decode deepen)

| Endpoint | Change for ? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **None (wire)** | Package-side WMO default golden fidelity (AIRMET + METAR/SPECI/TAF); no new params |
| `POST /api/v1/lint-tac` | **None (wire)** | New AIRMET registry codes in payloads |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | AIRMET codes; schema unchanged |
| `POST /api/v1/decode-tac` | **None (wire)** | Richer explanation strings via glossary; **no new required fields** |
| `POST /api/v1/validate` | **None (wire)** | Existing levels |
| Airport / OpenAIP (airport data services) | **Reuse** | Optional name enrichment for decode; miss → designator only |
| `POST /api/v1/dissemination/*` | **OOS** | — |

**Breaking changes**: None. FE Examples catalog is static (no new API).

- / (2026-07-29): AIRMET quality bar/WMO example parity WMO default goldens + live decode glossary deepen. wire shapes
 unchanged..

## / , Endpoint review (VAA quality bar / TCA quality bar)

| Endpoint | Change for ? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **Behavior clarify** | `product=vaa` \| `tca`: `manual_text` kept as one multi-line advisory (not line-split); wire schema unchanged |
| `POST /api/v1/convert-bulletin` | **None (wire)** | Per-report product identity for VAA/TCA in bulletins; quality bar-006 / quality bar-006 |
| `POST /api/v1/lint-tac` | **None (wire)** | New VAA/TCA registry codes in issue payloads; catalog stays source of truth |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | New VAA/TCA codes appear in catalog export; response schema unchanged |
| `POST /api/v1/decode-tac` | **None (wire)** | VAA/TCA best-effort decode already live decode sparse-product scope (G4); fixtures may expand |
| `POST /api/v1/validate` | **None (wire)** | Round-trip goldens use existing validate levels |
| `POST /api/v1/dissemination/*` | **OOS** | No dissemination drawer through AMHS SWIM AFS adapters changes this cycle |
| `/auth/*`, work-sessions | **None** | Historical (public operator app public era , pre–); restored hybrid operator sessions |

**Breaking changes**: None expected. FE Examples catalog is static (no new API). FE OpenAPI
types update only if catalog/issue content requires new documented code enums (prefer additive).

- / (2026-07-30): T6.1: VAA/TCA `manual_text` multi-line keep-whole for convert
 ( quality bar-005 / quality bar-005). FE `splitManualEntries` aligned.
- / (2026-07-29): VAA quality bar/TCA quality bar VAA+TCA quality: **full endpoint review**. no new
 routes. wire shapes unchanged. deepen (codes only). golden bar.

## / , Endpoint review (SWXA quality bar + eight-family)

| Endpoint | Change for ? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **Additive enum** | Add `product=swxa` → `iwxxm:SpaceWeatherAdvisory`; keep-whole `manual_text` like VAA/TCA. `product=sigmet` also selects **TC SIGMET** root from TAC |
| `POST /api/v1/convert-bulletin` | **Additive enum** | Same `product` enum; AHL/`T1T2` deepen package-side (FN→LN for SWXA); splitter rules B2 |
| `POST /api/v1/lint-tac` | **Additive enum + codes** | `product=swxa` accepted; new SWXA (+ COM/AHL) registry codes in payloads |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | SWXA/COM codes; response schema unchanged |
| `POST /api/v1/decode-tac` | **Additive enum** | `product=swxa` best-effort decode (live decode G4); TC SIGMET under `sigmet` |
| `POST /api/v1/validate` | **None (wire)** | Existing levels; SWXA/TC SIGMET goldens use same validate path |
| `POST /api/v1/dissemination/*` | **Consume AHL helpers** | No new routes; shared AHL/`T1T2`/filename model for sinks (drawer UI OOS) |
| `/auth/*`, work-sessions | **None** | Historical (public operator app public era , pre–); restored hybrid operator sessions |

**Breaking changes**: None. additive `swxa` only. FE OpenAPI / product pickers must add
`swxa` when SWXA quality bar unlocks Examples. Runtime enum enforcement lands in (backend +
packages). until then docs lead.

- / (2026-08-01): SWXA quality bar SWXA `product=swxa` + TC SIGMET under `sigmet`. eight-family
 AHL/COM deepen: **endpoint review**. additive enum. no new routes ( Q1=2).

## / , Endpoint review (parameterized rule matrices + residuals)

| Endpoint | Change for ? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **None (wire)** | No new `product` enum. TC SIGMET remains under `product=sigmet`. parameterized rule matrices is CI test setup only. |
| `POST /api/v1/convert-bulletin` | **None (wire)** | Unchanged |
| `POST /api/v1/lint-tac` | **Additive content** | New TC SIGMET registry codes appear in issue payloads when pack lands; schema unchanged |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | TC SIGMET codes; response schema unchanged |
| `POST /api/v1/decode-tac` | **Behavior deepen** | VAA/TCA structured field/forecast decode; response shape unchanged (residuals shrink) |
| `POST /api/v1/validate` | **None (wire)** | Same validate path; matrix test setup exercises offline |
| FE Examples / sample menu | **Catalog tier** | may unlock `sigmet-A6-2-TC` (`wmoPass` / `wmoReference` per ) , **static FE catalog**, no new API route. H4–H5 if FE ships. |
| Dissemination / auth / sessions | **None** | Unchanged |

**Breaking changes**: None. No new product enum. Catalog/menu unlock is FE static data + 
tier decision. document deferral if unlock does not ship this cycle.

- / (2026-08-02): parameterized rule matrices matrices + TC deepen + decode: **endpoint review**.
 lean + API/catalog note ( Q1=2).

## / , Endpoint review (VONA quality bar VONA + /corpus)

| Endpoint | Change for ? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **Additive enum** | Add `product=vona` → `iwxxm:VolcanoObservatoryNoticeForAviation`; keep-whole `manual_text` like VAA/TCA/SWXA. remains under `product=sigmet` (TC path) |
| `POST /api/v1/convert-bulletin` | **Additive enum** | Same `product` enum; AHL/`T1T2` for VONA when known |
| `POST /api/v1/lint-tac` | **Additive enum + codes** | `product=vona` accepted; new VONA registry codes in payloads |
| `GET /api/v1/lint-issue-catalog` | **Additive content** | VONA codes; response schema unchanged |
| `POST /api/v1/decode-tac` | **Additive enum** | `product=vona` best-effort decode (live decode G4) |
| `POST /api/v1/validate` | **None (wire)** | Existing levels; VONA / A6-2-TC goldens use same validate path |
| FE product picker / Examples | **Full operator workbench surface** | Add **VONA** to picker; unlock Examples when VONA quality bar golden greens ( Q2=3). may promote A6-2-TC → `wmoPass` (static catalog). H4–H5 when FE ships |
| Dissemination / auth / sessions | **None** | Unchanged |

**Breaking changes**: None. additive `vona` only. FE OpenAPI / product pickers must add
`vona` when VONA quality bar ships. Runtime enum enforcement lands in (backend + packages).
until then docs lead. is docs/checklist only (no wire change).

- / (2026-08-04): VONA quality bar VONA `product=vona` + full operator workbench surface. catalog tier.
 docs , **endpoint review**. full pack ( Q1=2).

## / , Endpoint review (pre-promote UX + catalog + AHL)

| Endpoint | Change for ? | Notes |
|----------|--------------------|-------|
| `POST /api/v1/convert` | **None (wire)** | Unchanged |
| `POST /api/v1/convert-bulletin` | **Additive codes** | `INVALID_AHL` for malformed heading (`detail.alias` = `bulletin_split_failed`); `files` field already required ( test setup). Decode/convert e2e is |
| `POST /api/v1/lint-tac` | **None (wire)** | Unchanged |
| `GET /api/v1/lint-issue-catalog` | **Additive fields + content** | IWXXM validation rows (`family=iwxxm`); `source_type` / `status` / `semantic_identifier` / `last_verified` / `replacement_url`. No new route. |
| `POST /api/v1/decode-tac` | **None (wire)** | AHL bulletins reuse this route: bulletin framing + per-report segments |
| `POST /api/v1/validate` | **Additive optional** | `segments` / `summary` (live decode shape) when Validate IWXXM still produces decode |
| FE catalog tab | **New page** | Top-level nav; consumes catalog GET; H4–H5 when FE ships |
| FE Product/Profile bars | **None (HTTP)** | Layout only |
| Dissemination / auth / sessions | **None** | Unchanged |
| CI promote | **N/A HTTP** | required checks , not an API change |

**Breaking changes**: None required. Additive fields only. `INVALID_AHL` is the operator-facing convert-bulletin code for malformed heading; `bulletin_split_failed` is retained as `detail.alias`.

- / (2026-08-18): – endpoint review.

## , Endpoint review (Validation Issues Catalog)

| Endpoint | Change for ? | Notes |
|----------|--------------------|-------|
| `GET /api/v1/lint-issue-catalog` | **Additive fields + content** | `issue_type`, `source_locator`, `source_access`; richer `message_template`s; optional query `issue_type` / `source_access`. No new route |
| `POST /api/v1/lint-tac` | **None (wire)** | Codes/severity unchanged; message text may deepen via registry |
| FE Validation Issues Catalog | **UX deepen** | Rename; type + multi-filter/sort; locator + access display |
| Dissemination / auth / sessions / convert / validate | **None** | Unchanged |

**Breaking changes**: None. Additive only.

- (2026-08-20): Validation Issues Catalog deepen.

## , Endpoint review 

| Endpoint | Change for ? | Notes |
|----------|-------------------|-------|
| `POST /api/v1/decode-tac` | **None (wire)** | Same `product`, `summary`, `segments`, `residuals`. Pack engine is internal. No `children` / `role` fields |
| `POST /api/v1/convert` | **None (wire)** | IR source moves to packs per product; vendor XML bytes stay identical |
| `POST /api/v1/convert-bulletin` | **None (wire)** | TAC abbreviated-heading split unchanged on the wire. COLLECT handling is package-side |
| `POST /api/v1/lint-tac` | **None (wire)** | Lint issues stay in `tac-validate` |
| `POST /api/v1/validate` | **None (wire)** | Unchanged |
| `product=sigmet` | **None (wire)** | Still one enum. Ordinary / VA / TC SIGMET are packs, not new values |
| FE workbench | **None** | No UI change. H4–H5 not required for this cycle |
| Dissemination / auth / sessions | **None** | Unchanged |

**Breaking changes**: None. Library import `tac2iwxxm.decode` stays. Legacy parsers, validation, and the pin compares stay.

- (2026-09-19): : no HTTP contract change. 

## , Endpoint review ( deepen)

| Endpoint | Change? | Notes |
|----------|---------|-------|
| `POST /api/v1/decode-tac` | **None (wire)** | Same fields. Richer METAR/SPECI pack rules improve spans/summary content only |
| `POST /api/v1/convert` | **None (wire)** | Library default for METAR/SPECI may switch to pack-IR emit when goldens match; request/response shape unchanged |
| Other convert/validate/lint | **None** | Unchanged |
| FE / H4–H5 | **N/A** | No UI or CORS change |

**Breaking changes**: None. `products/metar_speci.py` remains until a later delete-gate evolve.

- (2026-09-20): deepen : no HTTP contract change. 

## , Endpoint review 

| Endpoint | Change? | Notes |
|----------|---------|-------|
| `POST /api/v1/decode-tac` | **None (wire)** | Same fields. More products get richer pack-backed spans/summary |
| `POST /api/v1/convert` | **None (wire)** | Library defaults may expand pack-IR emit per product when goldens match; request/response shape unchanged |
| Other convert/validate/lint | **None** | Unchanged |
| FE / H4–H5 | **N/A** | No UI or CORS change |

**Breaking changes**: None on HTTP. Library: selective removal of `products/*.py` when byte-identical (all-or-nothing per shared file); `pack_ir_map` must not import deleted parsers.

- (2026-09-20): : no HTTP contract change. 

## , Endpoint review 

| Endpoint | Change? | Notes |
|----------|---------|-------|
| `POST /api/v1/decode-tac` | **None (wire)** | Richer station explanation/`summary` strings when airport lookup hits |
| `GET /api/v1/lint-issue-catalog` | **None (already )** | Confirm residual content; filters already documented |
| `GET /api/v1/rule-catalogs` / selection-options | **None ** | FE cutover consumes existing routes |
| Convert / validate / lint | **None** | AU/NZ catalog status + fixtures only |
| FE / H4–H5 | **Required when FE ships** | Profile Builder removal + catalog follow |

**Breaking changes**: None on HTTP. FE removes Profile Builder authoring surfaces.

- (2026-09-21): : no HTTP shape change. 

## , Endpoint review 

| Endpoint | Change? | Notes |
|----------|---------|-------|
| Convert / validate / lint / decode | **None (wire)** | Server-resolved policies/packs via env overlays only |
| OpenAPI body fields for pack/policy YAML | **Forbidden** | |
| FE / H4–H5 | **N/A** | Docs/SDK/deployer only |

**Breaking changes**: None on HTTP.

- (2026-09-21): : no HTTP shape change. 

## , Endpoint review 

| Endpoint | Change? | Notes |
|----------|---------|-------|
| Convert / validate / lint / decode | **None (wire)** in Spec | Emit map + overlays are env/file; |
| OpenAPI body fields for pack/policy/emit-map YAML | **Forbidden** | + |
| FE / H4–H5 | **N/A** unless Build adds UI/OpenAPI | Overlays stay deployer/SDK |

**Breaking changes**: None on HTTP.

- (2026-09-21): / Proposed: no HTTP shape change in Spec. 

## live TAC map live map , 

Public. No JWT. The browser calls this route only. Convert and validate bodies are unchanged. 

```
GET /api/v1/live-map?west=&south=&east=&north=&products=
```

| Query | Rule |
|-------|------|
| `west`, `south`, `east`, `north` | Degrees. West left of east. South below north. Outside −180..180 or −90..90 is 400 |
| `products` | Comma-separated product ids. Default is every geographically located product: `metar,speci,taf,airmet,gairmet,sigmet,vaa,tca,vona`. Unknown token is 400. Family names are not a query parameter. Space weather is not a product here |

**Response**:

```json
{
 "places": [
 {
 "place_key": "KJFK",
 "product": "metar",
 "latitude": 40.64,
 "longitude": -73.78,
 "geometry": { "kind": "point" },
 "reports": [
 {
 "observed_at": "2026-10-03T21:00:00Z",
 "tac": "METAR KJFK ...="
 }
 ]
 }
 ],
 "space_weather": []
}
```

- `reports` has at most three items from the last **24 hours** (UTC now). The newest is first. Each item on this route is `observed_at` and `tac`. Stored IWXXM and issue notes stay in the cache and stay off this list.
- `product` is one id: `metar`, `speci`, `taf`, `airmet`, `gairmet`, `sigmet`, `vaa`, `tca`, or `vona`.
- `geometry.kind` is `point`, `polygon`, `line`, or `circle`. A polygon or line includes `coordinates`. A circle includes `radius_m`.
- `space_weather` is the list of current products with no surface location. Those rows are never in `places`.

**Amend **: `gairmet` joins the allowed set and the default. Rows from the G-AIRMET feed use that id. A domestic row whose text is a SIGMET stays `sigmet`. The page groups ids under Observations, Forecasts, Hazards, and Advisories. Those group names are not query parameters. Hazards includes `airmet`, `gairmet`, and `sigmet`. Country, region, issue time, and hazard phenomenon are chosen in the browser from the places already returned. They are not query parameters. 

**Amend **: Every `observed_at` on this route is within the last 24 hours of UTC now. Places with no remaining in-window reports are omitted. Query parameters are unchanged. Client-only presets (1h / 3h / 6h / 12h / full) further narrow the loaded view and are not query parameters. 

The route reads the cache. It does not call a vendor during the request.

## Live check (open aviation feeds)

Public. No JWT. The browser must not call provider hosts; this route mediates egress.

```
GET /api/v1/live-check?icao=&product=&provider=
```

| Query | Rule |
|-------|------|
| `icao` | Four-letter ICAO code |
| `product` | `METAR` (default) or `TAF`. `knmi` accepts `METAR` only |
| `provider` | Allowlisted feed id: `noaa`, `met_no`, or `knmi` (default `noaa`). Other values are 400 |

**Response** (JSON): `icao`, `product`, `provider`, `profile` (`iwxxm_us` for `K*`, `ca_eccc` for `CY*`, else `annex3`), `source_tac`, `our_iwxxm`, `provider_iwxxm` (when the feed returned a pair), `attribution`, `cached`, `convert_ok`, `convert_issues`.

Egress hosts are fixed (`aviationweather.gov`, `api.met.no`, `api.dataplatform.knmi.nl`, plus validated KNMI download hosts). Callers never supply a URL. `KNMI_OPEN_DATA_API_KEY` stays server-side. Short cache and per-provider pacing stay inside published feed limits. Live network checks remain on `make test-live-feeds`, not pull-request CI.

## Local OpenAPI status and required-field check 

 

This check does not change any request or response. Operator-facing behavior stays as the sections above describe. `POST /api/v1/convert` status 200 still includes `failed`, `successful`, and `total_processed`.

The committed OpenAPI snapshot `apps/frontend/openapi/openapi.json` is compared with local interactions in the repository. The bugs job runs `uv run python scripts/ci/check_openapi_contract.py` with no PactFlow credentials and no broker. The check fails when an operation, an in-scope status, a required JSON request field, or a required JSON response field has no interaction. Path-only tests do not satisfy the check. Acceptance is ****. The implementation is already on `origin/stage` (pull requests and ).
