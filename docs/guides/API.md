# API guide

The HTTP API is the FastAPI application in `apps/backend`.

## Live reference

The live reference is the OpenAPI document that the FastAPI application serves:

- `{API}/openapi.json`
- `{API}/docs`

Replace `{API}` with your API base URL (for example
`http://localhost:8001` for local `make dev`, or
`https://api.staging.tac-to-iwxxm.com` for staging).

## Related docs

- Local ports and environment variables:
  [Development](../ops/DEVELOPMENT.md)
- Checked-in field contract: [api-contract.md](../api-contract.md)
