<!-- TEMPLATE: data-management-plan.md -->
<!-- Instructions: Replace all [bracketed placeholders] with project-specific content. -->
<!-- Remove this comment block before finalizing. -->

# Data Management Plan

> **Project**: deployed service
> **Repository**: [Repository URL]
> **Last updated**: [Date]

## Overview

Corpus sources, database schema lifecycle, seed data, and verification before build tasks
that depend on real documents or vectors.

### Scope

| In scope | Out of scope |
|----------|--------------|
| Document/chunk schema, migrations, seed fixtures | Ad-hoc analyst notebooks |
| Initial corpus import for dev/staging | Production customer PII (unless specified) |
| Embedding model version pinning | Training custom embedding models from scratch |

### Total data budget

| Metric | Value |
|--------|-------|
| Seed documents (dev) | [N] |
| Staging corpus size | [X MB / N docs] |
| Embedding dimensions | [e.g., 1536] |
| Auth-gated sources | [N] |

## Asset inventory

| # | Asset | Type | Size | Source | Auth | Needed by |
|---|-------|------|------|--------|------|-----------|
| D1 | [e.g., sample PDF set] | corpus_fixture | [10 MB] | [repo `fixtures/`] | none | T1.x ingest tests |
| D2 | [e.g., schema migration 001] | migration | — | [Alembic] | none | all DB tasks |
| D3 | [e.g., golden Q&A pairs] | eval_set | [1 MB] | [JSON in repo] | none | retrieval quality tests |

### Asset types

| Type | Description |
|------|-------------|
| corpus_fixture | Files or records used to test ingest |
| migration | Versioned DDL for Postgres/pgvector |
| eval_set | Question + expected chunk/doc ids for RAG regression |
| reference_config | Collection names, chunk size, overlap defaults |

## Schema & migrations

### Current revision

- **Head revision**: [alembic revision id]
- **Extensions**: `vector`, [others]

### Core entities

| Entity | Purpose | Key fields |
|--------|---------|------------|
| documents | Source metadata | `id`, `source_uri`, `checksum`, `status` |
| chunks | Text segments | `document_id`, `ordinal`, `content`, `token_count` |
| embeddings | Vector rows | `chunk_id`, `model`, `vector` |
| ingestion_jobs | Async work | `status`, `error`, `started_at` |

## Ingestion pipeline

1. **Register** document row (`pending`)
2. **Extract** text (format-specific parsers)
3. **Chunk** with `[size]` / `[overlap]`
4. **Embed** via `[model]` → store in pgvector
5. **Mark** `indexed` or `failed` with reason

## Local development

```bash
# Example — adjust to project Makefile
docker compose up -d postgres
alembic upgrade head
python scripts/seed_corpus.py --fixtures fixtures/dev/
```

## Staging / production

| Step | Command / process | Verification |
|------|-------------------|--------------|
| Migrate | [deploy hook] | `alembic current` == head |
| Seed (staging only) | [optional script] | row counts match manifest |
| Reindex | [worker job] | job table `completed` |

## Integrity checks

| Check | Method |
|-------|--------|
| No orphan chunks | SQL FK / count query |
| Embedding dimension | `vector_dims()` matches model |
| Duplicate documents | unique on `checksum` or `source_uri` |

## Security & compliance

- [PII handling policy]
- [Retention / delete API for GDPR]

## Task mapping

| Execution plan task | Data dependency |
|--------------------|-----------------|
| [T1.1] | D2 migrations |
| [T2.1] | D1 fixtures |
| [T3.1] | D3 eval_set |
