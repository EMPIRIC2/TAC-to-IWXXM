# First convert call

This procedure shows one convert request with multipart form fields.

## Before you start

1. Choose an API base URL from [Getting started](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Getting-started).
2. Open `{API}/docs` and find `POST /api/v1/convert`.
3. Prepare one TAC string that ends with the terminator `=`.

## Call convert

1. Send `POST {API}/api/v1/convert` as `multipart/form-data`.
2. Set `product` to the TAC product type in lower case (for example `metar`).
3. Set `manual_text` to your TAC string, or upload files in `files`.
4. Set `iwxxm_version` only when your procedure needs a specific IWXXM line.
5. Read the JSON response for success, XML output, and any issue lists.

Example field set:

| Field | Example value |
|-------|----------------|
| `product` | `metar` |
| `manual_text` | `METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=` |
| `lint` | `true` |

## Curl example

```bash
curl -sS -X POST "https://api.staging.tac-to-iwxxm.com/api/v1/convert" \
  -F "product=metar" \
  -F "manual_text=METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=" \
  -F "lint=true"
```

## After the call

1. Make sure that the response reports a successful convert when your TAC is valid.
2. Store the returned IWXXM XML per your local procedure.
3. Validate the IWXXM when your procedure needs a schema check before share.

## Common failures

| Symptom | What to do |
|---------|------------|
| Empty or failed convert | Make sure that the TAC ends with `=`. Make sure that `product` matches the TAC. |
| Lint errors | Fix the TAC text. Call convert again. |
| Unexpected fields | Compare your form fields to OpenAPI for that host. |

## Next step

Read [Authentication](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-Authentication) if you need saved work sessions.
