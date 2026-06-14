# Research Brief Template

Template for `{output_directory}/research-brief.md`.

```markdown
# Research Brief

> **Project**: [Project Name]
> **Repository**: [Repository URL]
> **Paper**: [Paper title — DOI/URL]
> **Generated**: [Date]
> **Skill**: gather-context

## Executive Summary

[2–3 paragraph synthesis of what the project does, what the paper contributes, and how the
repo implements it. Highlight the most important findings and any resolved contradictions.]

## Resolution Log

| # | Category | Issue | Resolution | Source |
|---|----------|-------|------------|--------|
| R1 | Contradiction | Dataset split differs | Use paper's spec | User decision |
| R2 | Bloat | Viz notebook | Exclude | User decision |
| R3 | Uncertainty | scikit-learn dep | Assumed vestigial | Advisory default |
| ... | ... | ... | ... | ... |

## Paper Analysis Summary

[Condensed version of the paper-analyst output, organized by Build / Run / Test / Configure.
Omit raw detail that's preserved in the full report below — focus on key takeaways.]

### Key Parameters from Paper

| Parameter | Value | Context | Paper Ref |
|-----------|-------|---------|-----------|
| ... | ... | ... | §X |

### Validation Experiments

| Experiment | Dataset | Metric | Target | Paper Ref |
|-----------|---------|--------|--------|-----------|
| ... | ... | ... | ... | §X |

### Hardware & Compute

| Resource | Spec | Context |
|----------|------|---------|
| ... | ... | ... |

## Repository Analysis Summary

[Condensed version of the repo-researcher output. Focus on key takeaways.]

### Build Quick-Reference

| Aspect | Detail | Source |
|--------|--------|--------|
| Language | ... | [Repo: ...] |
| Package manager | ... | [Repo: ...] |
| Key dependencies | ... | [Repo: ...] |

### Pipeline Stages

| Stage | Entry point | Input | Output | Notes |
|-------|------------|-------|--------|-------|
| ... | [Repo: file] | ... | ... | ... |

### Configuration Surface

| Config file | Format | Key fields | Source |
|-------------|--------|------------|--------|
| ... | ... | ... | [Repo: ...] |

## Data & Model Weight Requirements

Assets the project needs to download, stage, or generate before the pipeline can run:

| # | Asset | Type | Source | Size | Auth | Paper Ref | Repo Ref | Status |
|---|-------|------|--------|------|------|-----------|----------|--------|
| D1 | [e.g., ESM-2 650M weights] | model_weights | [HuggingFace Hub] | [2.5 GB] | [gated] | [§3.1] | [src/model.py:L42] | Confirmed / ⚠️ Uncertain |
| D2 | [e.g., SAbDab dataset] | dataset | [direct URL] | [500 MB] | [none] | [§2.1] | [data/README.md] | Confirmed |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Data Gaps

- ⚠️ [description of any data asset that couldn't be fully identified]
- ⚠️ [e.g., "Paper mentions 'pretrained embeddings' (§4.2) but no download URL or repo path found"]

## Cross-Reference Matrix

Alignment of key topics between paper and repo:

| Topic | Paper says | Repo says | Status |
|-------|-----------|-----------|--------|
| Default dataset | SAbDab [§3.2] | OAS [config.yaml:5] | ⚠️ Resolved: R1 |
| GPU requirement | A100 80GB [§4.1] | A100 (no size spec) [README:12] | Consistent |
| Preprocessing | "standard" [§2.1] | normalize_v2.py [src/] | ⚠️ Resolved: R4 |
| ... | ... | ... | ... |

## Unresolved Gaps

Issues that could not be resolved from available evidence and need human input during
downstream work:

- ⚠️ Needs human input: [gap description]
- ⚠️ Needs human input: [gap description]

## Full Agent Reports

<details>
<summary>Paper-Analyst Full Report</summary>

[Full paper-analyst output verbatim]

</details>

<details>
<summary>Repo-Researcher Full Report</summary>

[Full repo-researcher output verbatim]

</details>
```
