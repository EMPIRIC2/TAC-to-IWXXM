# HTTP API example

This example shows one public convert call for a METAR on the staging API. No
JWT is required for convert.

## Goal

Send multipart form fields to `POST /api/v1/convert` and receive IWXXM XML in
the JSON response.

## Sample TAC

```text
METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=
```

## Before you start

1. Open `https://api.staging.tac-to-iwxxm.com/docs`.
2. Find `POST /api/v1/convert`.
3. Keep the sample TAC ready, including the final `=`.

## Steps

1. Set the API base to `https://api.staging.tac-to-iwxxm.com`.
2. Send `POST /api/v1/convert` as `multipart/form-data`.
3. Set `product` to `metar`.
4. Set `manual_text` to the sample TAC.
5. Set `lint` to `true`.
6. Read the JSON response.
7. Store the IWXXM XML from the response when convert succeeds.
8. Call `POST /api/v1/validate` with that XML when your procedure needs a separate schema check.

## Curl example

```bash
curl -sS -X POST "https://api.staging.tac-to-iwxxm.com/api/v1/convert" \
  -F "product=metar" \
  -F "manual_text=METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=" \
  -F "lint=true"
```

## What you should see

| Check | Expected result |
|-------|-----------------|
| HTTP status | Success class for a valid convert |
| Lint | No error-severity issues for this sample, or only notes you accept |
| XML | Response includes IWXXM XML text |

Exact JSON field names can differ by release. Make sure that you compare the
response to OpenAPI for the host that you call.

## Optional: decode on the API

1. Send `POST /api/v1/decode-tac` with the same TAC and product.
2. Read the plain-language summary in the response.

## Optional: work session (signed in)

1. Sign in through `/auth/login` when your site enables auth.
2. Call `/api/v1/work-sessions*` with the JWT.
3. Guests skip this path.

## If something fails

| Symptom | What to do |
|---------|------------|
| 4xx on convert | Compare form field names to OpenAPI. Make sure that `product` is lower case. |
| Empty XML | Make sure that the TAC ends with `=`. Fix lint errors. Call convert again. |
| Unexpected product | Set `product` to match the TAC type. |

## Next step

- Field detail: [First convert call](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-First-convert-call)
- Other paths: [Examples](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Examples)
