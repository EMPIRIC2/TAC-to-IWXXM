# Caribbean tester regression kit

Durable copies of the October 2026 Met Services tester pack
(`TAC-IWXXM TRANSLATOR TESTING RESULTS`).

| Path | Role |
|------|------|
| `fixtures/caribbean_tester_all.jsonl` | Base packet (755) + harvest extras; convert issue locks |
| `fixtures/caribbean_tester_harvest_extra.jsonl` | New TAC from XLSX/DOCX/GTS not in the base packet |
| `fixtures/source_file_inventory.json` | Every Downloads file (124) and how it was ingested |
| `raw/` | `.tac` / `.xml` / `.xlsx` plus text members from tester ZIPs |

DOCX/PDF/PNG stay out of git (images). Their TAC strings are in the JSONL.
Screenshots are listed in the inventory as `binary_evidence_skipped`.

[Corpus: product §F6] [Corpus: tests]
