# BUG-2026-06-23-docker-frontend-bash-not-found

| Field | Value |
|-------|-------|
| Status | verifying |
| Severity | critical |
| Feature | F1 (deploy pipeline — frontend image) |
| Remediation path | local-first |

## Error description

Deploy CI fails when building the frontend Docker image. The builder stage runs
`npm run build`, which invokes `bash ../../scripts/frontend/prepare-config.sh`.
The `node:20-alpine` image does not include `bash`, so the build exits with code 127.

## Error logs

```
> [builder 6/6] RUN npm run build:
0.201 > @metar/frontend@0.0.1 build
0.201 > bash ../../scripts/frontend/prepare-config.sh && vite build
0.206 sh: bash: not found
...
ERROR: failed to build: process "/bin/sh -c npm run build" did not complete successfully: exit code: 127
```

## Symptoms & reproduction

- **Where:** GitHub Actions `ci-cd.yml` — `Build and push frontend Docker image`
- **Frequency:** Every deploy run
- **Trigger:** `docker/build-push-action` with `context: ./apps/frontend`, `target: production`

## Investigation

| Time | Finding |
|------|---------|
| 2026-06-23 | `apps/frontend/Dockerfile` builder uses `FROM node:20-alpine` |
| 2026-06-23 | `apps/frontend/package.json` `build` script requires `bash` + repo-root `scripts/` and `config/` |
| 2026-06-23 | Docker build context is `./apps/frontend` only — `prepare-config.sh` path would be missing even with bash |
| 2026-06-23 | CI already passes `VITE_*` build-args; runtime-config falls back to baked Vite env if `/config.json` absent |

**Root cause (proposed):** Config/infra mismatch — production Docker build reuses the monorepo
`npm run build` script designed for hosts with bash and full repo checkout.

## Spec conformance

| Spec | Result |
|------|--------|
| `docs/deploy.md` / ci-cd frontend image | Implementation drift — Docker build must succeed on Alpine |
| `docs/feature-list.md` F1 | In scope — unblocks deploy |
| `config-spec.md` | N/A — same runtime config fields via VITE_* + generated `config.json` |

## Repro test

| Field | Value |
|-------|------|
| Path | `tests/bugs/test_bug_2026_06_23_docker_frontend_bash_not_found.py` |
| Assertion | Builder stage must not run `npm run build` (bash-dependent) without installing bash |

## TDD iteration log

| # | Action | Result |
|---|--------|--------|
| 1 | Add Dockerfile contract repro test | RED |
| 2 | Replace `npm run build` with node config.json + `npx vite build` | GREEN |

## Fix

**Files:** `apps/frontend/Dockerfile` (builder stage)

Replaced bash-dependent `RUN npm run build` with:
1. `node -e` inline script writing `public/config.json` from `VITE_*` build args
2. `RUN npx vite build`

**Why:** Alpine `node:20-alpine` has no bash; Docker context `./apps/frontend` lacks
`scripts/` and `config/` needed by `prepare-config.sh`. CI already supplies all values
via build-args.

**Local Docker verify:** `docker build --target builder` — exit 0, vite built in ~21s.

## Verification plan

- **Success:** Frontend Docker build succeeds in CI deploy job
- **Checks:** Full main CI parity (local) + gh on main after merge
- **Monitoring:** Re-check next CI deploy run on main

## Interview record

- Intent: New CI deploy failure
- Symptom: Error / crash — bash not found
- Where: CI deploy job
- Severity: Critical — blocks frontend image
- Remediation: Local-first fix + PR

## Verification

### Layer 1 — Automated

- [x] Repro test red → green
- [x] Local Docker builder stage build (Alpine, no bash)
- [ ] Full test suite / CI parity (local)
- [ ] PR branch CI after push

### Layer 2 — Reproduction

- [ ] CI deploy job green after merge

## Prevention & countermeasures

(pending Phase 5)

## Cursor rule

(pending Phase 5.1)
