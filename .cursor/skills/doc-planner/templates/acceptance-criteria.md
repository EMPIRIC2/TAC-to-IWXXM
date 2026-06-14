<!-- TEMPLATE: acceptance-criteria.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# Acceptance Criteria

> **Project**: [Project Name]
> **Repository**: [Repository URL]
> **Last updated**: [Date]

## Per-Feature Criteria

### [Feature 1 Name]

- [ ] [Measurable condition 1 — e.g., "Pipeline completes without error on sample input"]
- [ ] [Measurable condition 2 — e.g., "Output file contains valid PDB format"]
- [ ] [Measurable condition 3 — e.g., "Runtime under 5 minutes on single A100 GPU"]
- **Source**: [Paper §X] or [Repo: file]

### [Feature 2 Name]

- [ ] [Measurable condition 1]
- [ ] [Measurable condition 2]
- **Source**: [Paper §X] or [Repo: file]

### [Feature 3 Name]

- [ ] [Measurable condition 1]
- [ ] [Measurable condition 2]
- **Source**: [Paper §X] or [Repo: file]

## Quantitative Benchmarks

Results the software must reproduce to be considered correct:

| # | Benchmark | Metric | Target | Tolerance | Dataset | Paper Reference |
|---|-----------|--------|--------|-----------|---------|-----------------|
| B1 | [name] | [metric] | [value] | [± tolerance] | [dataset] | [Paper §X, Table Y] |
| B2 | [name] | [metric] | [value] | [± tolerance] | [dataset] | [Paper §X, Table Y] |

### Benchmark Details

#### B1: [Benchmark Name]

- **What it measures**: [Description]
- **How to run**: `[command]`
- **Expected result**: [Value] ± [tolerance]
- **Paper-reported result**: [Value] — [Paper §X, Table Y]
- **Evaluation dataset**: [Name, where to get it]

## Qualitative Criteria

Non-numeric conditions that must be met:

- [ ] [Criterion — e.g., "Documentation covers all CLI commands"]
- [ ] [Criterion — e.g., "Installation succeeds on a clean Ubuntu 22.04 system"]
- [ ] [Criterion — e.g., "Error messages are informative and actionable"]

## Build Acceptance

- [ ] Builds from source without manual intervention
- [ ] All declared dependencies resolve
- [ ] Docker image builds successfully
- [ ] ⚠️ [Additional project-specific build criteria]

## Deployment Acceptance

- [ ] [Criterion — e.g., "Model weights download automatically on first run"]
- [ ] [Criterion — e.g., "Graceful fallback when GPU is unavailable"]

## Regression Criteria

Conditions that must not regress between versions:

| Metric | Baseline | Source | Must Not Exceed |
|--------|----------|--------|-----------------|
| [metric] | [current value] | [how measured] | [threshold] |

## References

- [Paper §X — validation experiments and reported results]
- [Repo: tests/ — existing test suite]
