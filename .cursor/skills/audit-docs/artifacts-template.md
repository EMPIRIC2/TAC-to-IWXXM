# Audit Artifact Templates

Templates for the three files created during Phase 3.

## 1. `audit-state.md` — Progress tracker (detail mirror)

Primary stage state: repo-root `workflow-state.yaml` §`stages.audit-docs`
(see [workflow-state-reference.md](../workflow-state-reference.md)).

```markdown
# Audit State

> **Last updated**: [date/time]
> **Status**: in_progress

## Progress Summary

| Metric | Value |
|--------|-------|
| Documents total | [N] |
| Documents completed | [0] |
| Documents remaining | [N] |
| Current document | [doc name] |
| Statements total | [N] |
| Statements reviewed | [0] |
| Statements remaining | [N] |
| Approved | [0] |
| Denied | [0] |
| Modified | [0] |

## Document Progress

| # | Document | Statements | Reviewed | Approved | Denied | Modified | Status |
|---|----------|-----------|----------|----------|--------|----------|--------|
| 1 | Deployment Integration Plan | [N] | 0 | 0 | 0 | 0 | pending |
| 2 | Test Plan | [N] | 0 | 0 | 0 | 0 | pending |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Current Position

- **Document**: [1] [doc name]
- **Statement**: S1.1
- **Next**: S1.2
```

## 2. `document-audit.md` — Full audit report

```markdown
# Document Audit

> **Project**: [Project Name]
> **Generated**: [Date]
> **Skill**: audit-docs

## Document 1: [Document Name]

### S1.1
- **Section**: [section path]
- **Statement**: "[quoted claim]"
- **Source**: [Paper §X / Repo: file:L#]
- **Confidence**: [High/Medium/Low]
- **Verdict**: pending
- **User feedback**: —
- **Action taken**: —

### S1.2
...

---

## Document 2: [Document Name]

### S2.1
...
```

## 3. `audit-decisions.md` — Chronological decision log

```markdown
# Audit Decision Log

> **Project**: [Project Name]
> **Generated**: [Date]

| # | Timestamp | Statement | Document | Verdict | User Feedback | Action |
|---|-----------|-----------|----------|---------|---------------|--------|
| 1 | [time] | S1.1 | Deployment Integration Plan | Approved | — | None |
| 2 | [time] | S1.2 | Deployment Integration Plan | Modified | "Should be A100, not H100" | Updated doc |
| 3 | [time] | S1.3 | Deployment Integration Plan | Denied | "This is wrong, remove it" | Removed from doc |
```
