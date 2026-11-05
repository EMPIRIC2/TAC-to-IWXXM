# HTTP API overview

The **HTTP API** is the network service that converts TAC, lints TAC, and
makes sure that IWXXM meets schema rules. The service also supports related
operator tasks.

## What the API does

| Capability | Typical route family |
|------------|----------------------|
| Convert TAC to IWXXM | `POST /api/v1/convert` and related convert routes |
| Lint TAC | `POST /api/v1/lint-tac` |
| Validate IWXXM | `POST /api/v1/validate` |
| Decode TAC to plain language | `POST /api/v1/decode-tac` |
| Work sessions | `/api/v1/work-sessions*` (sign-in required) |
| Auth helpers | `/auth/*` |

The live route list can change. Always read OpenAPI for the host that you call.

## Base URLs

| Environment | API base URL |
|-------------|--------------|
| Production | `https://api.tac-to-iwxxm.com` |
| Staging | `https://api.staging.tac-to-iwxxm.com` |
| Local development | `http://localhost:18001` |

## OpenAPI (source of routes)

| Document | URL pattern |
|----------|-------------|
| Interactive docs | `{API}/docs` |
| OpenAPI JSON | `{API}/openapi.json` |

Replace `{API}` with the API base URL for your environment.

## Auth in one sentence

Convert, lint, validate, decode, and dissemination calls stay public on the
current product policy. A JSON Web Token (JWT) is required only for work-session
routes under `/api/v1/work-sessions*`.

See [Authentication](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-Authentication).

## Request shape for convert

The convert and validate routes take **multipart form** fields (`Form` /
`File`). Do not send the product type only in a JSON body for those routes.

See [First convert call](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-First-convert-call).

## Health check

```
GET /health
```

A healthy response includes a status field. The response also shows whether the
convert engine is available.

## Related pages

- [HTTP API example journey](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-Example-journey)
- [First convert call](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-First-convert-call)
- [Authentication](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-Authentication)
- [Web app overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app)
