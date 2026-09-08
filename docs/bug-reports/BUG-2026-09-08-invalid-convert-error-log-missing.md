# Bug report: invalid convert error log missing on staging

**ID:** BUG-2026-09-08-invalid-convert-error-log-missing  
**Date:** 2026-09-08  
**PR:** pending  
**Session:** EV-staging-adversarial-e2e

## Error description

On the staging converter, a hard convert with invalid TAC shows a generic `Conversion Error`
state but does not render the visible `Conversion error log` panel. The operator therefore
loses the structured validation and lint details that the API already returns for the failure.

## Error logs

```text
POST https://api.staging.tac-to-iwxxm.com/api/v1/convert
HTTP 400

detail.message = "All conversions failed"
detail.errors = ["manual_input: Validation failed - 1 validation issue(s) found"]
detail.issues[0].code = "VALIDATION_FAILED"
detail.issues[1].code = "ICAO_VALIDATION_FAILED"
detail.issues[3].code = "MISSING_CCCC"
```

Targeted live repro:

```text
cd apps/e2e
PLAYWRIGHT_BASE_URL=https://app.staging.tac-to-iwxxm.com \
PLAYWRIGHT_API_BASE_URL=https://api.staging.tac-to-iwxxm.com \
pnpm exec playwright test issue-555-ux-delta.e2e.spec.ts --grep "failed convert shows error log panel"
```

Result: red on staging; `getByLabel(/conversion error log/i)` not found.

## Investigation

1. Staging `config.json` points at `https://api.staging.tac-to-iwxxm.com`.
2. Direct API probe shows hard-convert invalid TAC returns HTTP 400 with structured
   `detail.errors` and `detail.issues`.
3. `apps/frontend/src/utils/api.ts` currently throws `new Error(message)` for non-2xx convert
   responses and discards `detail.errors` / `detail.issues`.
4. `apps/frontend/src/app/components/FileConverter.tsx` catch block only reads
   `error.message`, so it can show the generic banner/toast but cannot render `ErrorLogPanel`.

**Root cause:** structured convert failure payloads are dropped at the frontend API boundary
for hard-convert HTTP errors.

## Repro test

- Path: `apps/frontend/src/utils/api.test.ts`
- Path: `apps/frontend/src/app/components/FileConverter.test.tsx`
- Status: red before fix; green after fix

## Fix

Preserve structured `errors` / `issues` in a frontend convert-specific error type, then let
`FileConverter` populate `conversionLog` from that error in the hard-convert catch path.

## Interview record

- Build gate: Open Build and proceed with fixes now.
- First bug: Missing visible conversion error log on invalid convert.
- Remediation path: Fix locally first, then verify with targeted and live tests.
- Severity: High.
- Repro confirmation: confirmed from targeted staging Playwright repro.
- Root cause confirmation: approved before patching.

## Prevention & countermeasures

- Add API-client regression coverage so non-2xx convert responses keep structured details.
- Add converter regression coverage so hard-convert failures still render `ErrorLogPanel`.

## Cursor rule

- No new rule proposed yet; existing bug-investigation and TDD rules covered the workflow.
