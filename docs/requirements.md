# Product intake requirements (CMO feedback)

> Matrix: [requirements.csv](requirements.csv)
> Last updated: 2026-11-20

The CSV is the source of truth for intake rows extracted from CMO IWXXM
testing feedback forms. This file defines columns only.

[Corpus: product] [Corpus: doc-standards]

## Columns

| Column | Meaning |
|--------|---------|
| `id` | Stable intake id (`REQ-CMO-NNN`) |
| `source` | Feedback form or guide file name |
| `priority` | high, med, or low |
| `product_area` | convert, validate, accuracy, usability, error_handling, performance, testing, adoption, or intake |
| `requirement` | Short product or process ask |
| `acceptance_criteria` | How testers or CI would show the ask is met |
| `status` | open, mapped, or closed |
| `notes` | Trace detail (form section, gap notes) |

## Rules

1. Every row must name a real feedback source file in `source`.
2. Do not invent standing F* rows in [product-requirements.md](product-requirements.md) from this CSV alone; promote through a later planning cycle.
3. Filled questionnaire responses were not available in the extract cycle; rows come from the form instruments and testing guide.
