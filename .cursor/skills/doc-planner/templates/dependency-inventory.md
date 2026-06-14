<!-- TEMPLATE: dependency-inventory.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# Dependency Inventory

> **Project**: [Project Name]
> **Repository**: [Repository URL]
> **Last updated**: [Date]

## Runtime Dependencies

| Package | Version | Purpose | License | Pinned | Source |
|---------|---------|---------|---------|--------|--------|
| [package] | [version or constraint] | [why it's needed] | [SPDX id] | [Yes/No] | [Repo: requirements.txt:L#] |

## Build / Dev Dependencies

| Package | Version | Purpose | License | Source |
|---------|---------|---------|---------|--------|
| [package] | [version] | [why it's needed] | [SPDX id] | [Repo: file] |

## System-Level Dependencies

| Package | Minimum Version | Platform | Install Command | Purpose |
|---------|-----------------|----------|-----------------|---------|
| [package] | [version] | Debian/Ubuntu | `apt install [pkg]` | [purpose] |
| [package] | [version] | RHEL/Fedora | `dnf install [pkg]` | [purpose] |
| [package] | [version] | macOS | `brew install [pkg]` | [purpose] |

## Language Runtimes

| Runtime | Minimum Version | Recommended Version | Version Manager |
|---------|-----------------|---------------------|-----------------|
| [Python / Node / Rust / R / etc.] | [version] | [version] | [pyenv / nvm / rustup / etc.] |

## Hardware Requirements

| Resource | Minimum | Recommended | Context | Source |
|----------|---------|-------------|---------|--------|
| GPU | [spec] | [spec] | [training / inference / both] | [Paper §X] |
| GPU Memory | [spec] | [spec] | [which operations] | [Paper §X] |
| RAM | [spec] | [spec] | [which operations] | [Paper §X] |
| Disk | [spec] | [spec] | [corpus fixtures / data / scratch] | |
| CPU Cores | [spec] | [spec] | [data loading / preprocessing] | |

## Pre-trained Models / Weights

| Model | Size | Source | Required For | How to Obtain |
|-------|------|--------|--------------|---------------|
| [model name] | [size] | [URL] | [which feature] | [download command or instructions] |

## External Datasets

| Dataset | Size | Source | Format | Required For | How to Obtain |
|---------|------|--------|--------|--------------|---------------|
| [name] | [size] | [URL] | [format] | [which feature/test] | [instructions] |

## External Services

| Service | URL | Required | Purpose | Auth Required |
|---------|-----|----------|---------|---------------|
| [service] | [URL] | [Yes/No] | [purpose] | [Yes/No — type] |

## Container Images

| Image | Tag | Registry | Size | Contains |
|-------|-----|----------|------|----------|
| [image name] | [tag] | [Docker Hub / GHCR / etc.] | [size] | [what's bundled] |

## Known Compatibility Issues

- [Issue 1 — e.g., "Package X v2.0 breaks compatibility with Y"]
- [Issue 2 — e.g., "CUDA 12.x required; CUDA 11.x not supported"]

## References

- [Paper §X — dependencies and environment described]
- [Repo: requirements.txt / setup.py / Dockerfile — source of truth]
