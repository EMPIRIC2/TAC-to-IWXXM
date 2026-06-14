# Config Validator

Validates that settings and API payload fields in code match approved configuration docs
(ephemeral `config-spec` artifact from 04-tech-plan or inline spec tables). Use when adding
request parameters, defaults, validation rules, or env-based settings.

## State management

Read repo-root `workflow-state.yaml` §`template` and §`stages.config-validator` before
validating. After a validation pass, set status and log drift in `issue_log`.
Rules: [workflow-state-reference.md](../workflow-state-reference.md).

## Triggers

- New env var or settings field in `src/config/` or equivalent
- Request body / query parameters in API routers
- Changing defaults that affect behavior

## Validation checks

### 1. Parameter existence

Every user-facing field must appear in the config spec artifact or `docs/api-contract.md`.
Undocumented fields → `[Scope Drift]`.

### 2. Example parameters (adjust to spec)

| Parameter | Spec type | Notes |
|-----------|-----------|-------|
| `{{EXAMPLE_PARAM}}` | str | Replace with project parameters |

### 3. Defaults

Defaults in code must match config spec. Mismatch → `[Contradiction]` with section cite.

### 4. Validation rules

Document in config spec (e.g. ranges, required fields, mutual constraints).

### 5. Precedence

Document order (e.g. request body > env defaults). Secrets only via env/platform — never in repo.

## Output

- **PASS** — types, defaults, rules aligned
- **FAIL** — list code vs spec per field

## References

- Config spec artifact in `workflow-state.yaml` §`artifacts`
- `docs/api-contract.md`
