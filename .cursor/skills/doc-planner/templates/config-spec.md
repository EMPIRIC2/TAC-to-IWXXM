<!-- TEMPLATE: config-spec.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# Configuration Specification

> **Project**: [Project Name]
> **Repository**: [Repository URL]
> **Last updated**: [Date]

## Precedence Order

Configuration values are resolved in this order (highest priority first):

1. CLI flags
2. Environment variables
3. Configuration files
4. Built-in defaults

## Configuration Files

### [filename.yaml]

- **Format**: [YAML / TOML / JSON / INI / Python]
- **Location**: `[path/to/file]`
- **Purpose**: [What this config file controls]

| Field | Type | Default | Required | Valid Values | Description |
|-------|------|---------|----------|--------------|-------------|
| [field] | [str/int/float/bool/list] | [default] | [Yes/No] | [range or options] | [description] |

<details>
<summary>Example configuration</summary>

```yaml
# [Annotated example with comments explaining each field]
field_1: value
field_2: value
nested:
  field_3: value
```

</details>

### [filename2.toml]

- **Format**: [Format]
- **Location**: `[path/to/file]`
- **Purpose**: [What this config file controls]

| Field | Type | Default | Required | Valid Values | Description |
|-------|------|---------|----------|--------------|-------------|
| [field] | [type] | [default] | [Yes/No] | [range] | [description] |

## Environment Variables

| Variable | Type | Default | Required | Description | Maps to Config |
|----------|------|---------|----------|-------------|----------------|
| [VAR_NAME] | [type] | [default] | [Yes/No] | [description] | [config field it overrides] |

### Secrets & Sensitive Values

| Variable | Purpose | How to Obtain |
|----------|---------|---------------|
| [SECRET_VAR] | [purpose] | [instructions] |

## CLI Flags

| Flag | Short | Type | Default | Description | Maps to Config |
|------|-------|------|---------|-------------|----------------|
| --[flag] | -[f] | [type] | [default] | [description] | [config field] |

## Recommended Defaults from Paper

Parameters the authors used for their best-reported results:

| Parameter | Recommended Value | Config Location | Paper Reference |
|-----------|-------------------|-----------------|-----------------|
| [param] | [value] | [config file:field or CLI flag] | [Paper §X] |

## Parameter Groups

### [Group Name — e.g., "Training Parameters"]

| Parameter | Value | Sensitivity | Notes |
|-----------|-------|-------------|-------|
| [param] | [value] | High / Medium / Low | [Paper §X] |

### [Group Name — e.g., "Inference Parameters"]

| Parameter | Value | Sensitivity | Notes |
|-----------|-------|-------------|-------|
| [param] | [value] | High / Medium / Low | [Paper §X] |

## Validation Rules

- [Rule 1 — e.g., "batch_size must be a power of 2"]
- [Rule 2 — e.g., "learning_rate must be between 0 and 1"]

## References

- [Paper §X — parameter tables and recommended settings]
- [Repo: path/to/config — default config files]
