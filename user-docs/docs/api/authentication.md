# Authentication

This page describes when the HTTP API needs a signed-in user.

## Public routes

Convert TAC to IWXXM does not need a JWT on the current product policy.
Lint TAC does not need a JWT.
Validate IWXXM does not need a JWT.
Decode TAC does not need a JWT.
Dissemination send paths that the deployment enables do not need a JWT.

Guests and signed-in users share the same public convert path.

## Routes that need a JWT

Work-session routes under `/api/v1/work-sessions*` need a valid JWT from the
auth service.

## Auth endpoints

The API mounts auth helpers under `/auth/*`. Common operations include login,
logout, and current-user lookup. Make sure that you read the live list on
`{API}/docs` for your host.

| Operation | Typical path |
|-----------|--------------|
| Login | `POST /auth/login` |
| Logout | `POST /auth/logout` |
| Current user | `GET /auth/me` |

## Rules for credentials

1. Use the account that your organization issues.
2. Do not put passwords or tokens into shared tickets or chat.
3. Do not log `Authorization` headers or JWTs.
4. Prefer the web app sign-in flow when you only need browser work history.

## Guest versus signed-in storage

| Mode | Work history |
|------|----------------|
| Guest | Local browser storage only. If you clear the browser, drafts can disappear. |
| Signed in | Server-side work sessions through the work-session API |

## Next step

- Browser users: [Web app overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app)
- Convert from code: [First convert call](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-First-convert-call)
