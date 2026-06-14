<!-- TEMPLATE: migration-plan.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# Migration Plan

> **Project**: [Project Name]
> **Repository**: [Repository URL]
> **Last updated**: [Date]

## Summary

| Field | Value |
|-------|-------|
| **From** | [Starting state — version, system, format, etc.] |
| **To** | [Target state] |
| **Estimated effort** | [Time / person-hours] |
| **Risk level** | [High / Medium / Low] |
| **Rollback possible** | [Yes / Partial / No] |

## Motivation

[Why this migration is needed. What problem does it solve?]

## Scope

**In scope**:
- [What is being migrated]

**Out of scope**:
- [What is NOT being migrated]

## Pre-Migration Checklist

- [ ] [Prerequisite 1 — e.g., "Back up existing data"]
- [ ] [Prerequisite 2 — e.g., "Verify target environment is ready"]
- [ ] [Prerequisite 3 — e.g., "Notify downstream consumers"]
- [ ] [Prerequisite 4 — e.g., "Test migration on staging first"]

## Migration Steps

| # | Step | Command / Action | Duration | Rollback |
|---|------|-----------------|----------|----------|
| 1 | [Step name] | `[command or manual action]` | [est. time] | [how to undo] |
| 2 | [Step name] | `[command or manual action]` | [est. time] | [how to undo] |
| 3 | [Step name] | `[command or manual action]` | [est. time] | [how to undo] |

### Step Details

#### Step 1: [Step Name]

- **What**: [Detailed description]
- **Command**:
  ```bash
  [exact command to run]
  ```
- **Expected output**: [What success looks like]
- **Failure mode**: [What could go wrong]
- **Rollback**:
  ```bash
  [exact rollback command]
  ```

## Post-Migration Validation

| # | Check | Command / Method | Expected Result |
|---|-------|-----------------|-----------------|
| 1 | [Check name] | `[command]` | [expected output] |
| 2 | [Check name] | `[command]` | [expected output] |

## Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | [Risk] | [H/M/L] | [H/M/L] | [How to mitigate] |

## Rollback Plan

If the migration fails:

1. [Step 1 — immediate action]
2. [Step 2 — restore from backup]
3. [Step 3 — notify stakeholders]

**Point of no return**: [After which step rollback is no longer straightforward]

## Communication Plan

| When | Who | What |
|------|-----|------|
| Before migration | [Stakeholders] | [Notification of upcoming change] |
| During migration | [Team] | [Status updates] |
| After migration | [Users] | [Confirmation and any action required] |

## References

- [Paper §X — if migration relates to algorithm or data format changes]
- [Repo: CHANGELOG / migration scripts]
