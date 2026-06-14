<!-- TEMPLATE: spec.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# Technical Specification

> **Project**: [Project Name]
> **Repository**: [Repository URL]
> **Version**: [Version or commit hash this spec describes]
> **Last updated**: [Date]

## Overview

[What this software does at a technical level. One paragraph covering purpose, approach,
and key innovation.]

## System Architecture

[High-level description of how the system is organized. Describe major components and
their relationships. Reference a diagram if one exists.]

```
[ASCII diagram or description of component layout]

  [Input] → [Component A] → [Component B] → [Component C] → [Output]
                  ↓                               ↑
            [Component D] ─────────────────────────┘
```

### Component Overview

| Component | Purpose | Location | Dependencies |
|-----------|---------|----------|--------------|
| [Name] | [What it does] | [Repo: path/] | [Other components] |

## Component Details

### [Component A]

- **Purpose**: [What this component is responsible for]
- **Inputs**: [Data format, source, constraints]
- **Outputs**: [Data format, destination]
- **Algorithm**:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- **Key parameters**:
  | Parameter | Type | Default | Description |
  |-----------|------|---------|-------------|
  | [param] | [type] | [default] | [desc] |
- **Error handling**: [How failures are handled]
- **Source**: [Paper §X] and [Repo: file:lines]

### [Component B]

- **Purpose**: [What this component is responsible for]
- **Inputs**: [Data format, source, constraints]
- **Outputs**: [Data format, destination]
- **Algorithm**:
  1. [Step 1]
  2. [Step 2]
- **Key parameters**:
  | Parameter | Type | Default | Description |
  |-----------|------|---------|-------------|
  | [param] | [type] | [default] | [desc] |
- **Source**: [Paper §X] and [Repo: file:lines]

## Data Flow

[Describe how data moves through the system from input to output.]

| Stage | Input Format | Transformation | Output Format | Notes |
|-------|-------------|----------------|---------------|-------|
| 1. [Name] | [format] | [what happens] | [format] | [notes] |
| 2. [Name] | [format] | [what happens] | [format] | [notes] |
| 3. [Name] | [format] | [what happens] | [format] | [notes] |

## Constraints & Assumptions

### Hard Constraints

- [Constraint 1 — e.g., requires GPU with X GB VRAM]
- [Constraint 2 — e.g., input must be in PDB format]

### Assumptions

- [Assumption 1 — what we assume is true about the input/environment]
- [Assumption 2 — what we assume is true about the use case]

## Security & Privacy

[Any security considerations, data handling requirements, or access control needs.]

## Performance Characteristics

| Operation | Expected Time | Hardware | Notes |
|-----------|---------------|----------|-------|
| [Operation] | [Duration] | [Hardware used] | [Paper §X] |

## Known Limitations

- [Limitation 1 — what doesn't work or isn't supported]
- [Limitation 2 — edge cases or failure modes]

## References

- [Paper §X — relevant methods/architecture sections]
- [Repo: path/to/file — implementation]
