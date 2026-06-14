<!-- TEMPLATE: api-contract.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# API Contract

> **Project**: [Project Name]
> **Repository**: [Repository URL]
> **API Type**: [CLI / Python library / REST / gRPC]
> **Last updated**: [Date]

## Overview

[Brief description of the API surface — what consumers can do with it.]

## Entry Points

### [Entry Point 1 — e.g., CLI command or function]

- **Type**: [CLI command / Python function / REST endpoint / gRPC method]
- **Signature / Syntax**:
  ```
  [command or function signature]
  ```
- **Description**: [What this entry point does]
- **Parameters**:
  | Name | Type | Required | Default | Description |
  |------|------|----------|---------|-------------|
  | [param] | [type] | [Yes/No] | [default] | [description] |
- **Returns / Output**:
  | Field | Type | Description |
  |-------|------|-------------|
  | [field] | [type] | [description] |
- **Errors**:
  | Error | Condition | Description |
  |-------|-----------|-------------|
  | [error type/code] | [when it occurs] | [what it means] |
- **Example**:
  ```
  [usage example with expected output]
  ```
- **Source**: [Repo: file:lines]

### [Entry Point 2]

- **Type**: [type]
- **Signature / Syntax**:
  ```
  [signature]
  ```
- **Description**: [What it does]
- **Parameters**:
  | Name | Type | Required | Default | Description |
  |------|------|----------|---------|-------------|
  | [param] | [type] | [Yes/No] | [default] | [description] |
- **Returns / Output**:
  | Field | Type | Description |
  |-------|------|-------------|
  | [field] | [type] | [description] |
- **Example**:
  ```
  [usage example]
  ```
- **Source**: [Repo: file:lines]

## Data Models

### [Model / Schema Name]

[Description of this data structure and where it's used.]

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| [field] | [type] | [Yes/No] | [constraints] | [description] |

### [Model / Schema Name 2]

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| [field] | [type] | [Yes/No] | [constraints] | [description] |

## File Formats

### Input: [Format Name]

- **Extension**: [.ext]
- **Format**: [Description]
- **Schema / Structure**:
  ```
  [example structure]
  ```
- **Validation rules**: [constraints]

### Output: [Format Name]

- **Extension**: [.ext]
- **Format**: [Description]
- **Schema / Structure**:
  ```
  [example structure]
  ```

## Versioning & Compatibility

- **Current version**: [version]
- **Backward compatibility**: [policy]
- **Deprecation policy**: [policy]

## References

- [Paper §X — API described in methods]
- [Repo: path/to/source — implementation]
