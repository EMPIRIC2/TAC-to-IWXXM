# tac-validate test naming

[Corpus: tests]

## Forward rule

Name each **new** test module:

```text
test_<subject>_<scenario>.py
```

Example: `test_rvr_trend_slash_accepted.py`.

Put evolve, test-case, and milestone ids in the module docstring, a pytest
marker, or a comment. Do not put those ids in the file name.

## Banned stems (new files only)

Do not add new files whose basename matches:

| Pattern | Meaning |
| ------- | ------- |
| `test_ev_*`, `test_ev`, `test_ev<digits>_*` | Evolve-session dump stems |
| `test_tc_ev*` | Test-case archive tied to an evolve id |
| `test_m<digits>_*` | Milestone / detector-routing stem |

The guard is `scripts/ci/check_test_file_naming.py` (also
`make test-file-naming-guard`). It fails closed on **new** paths versus the
comparison base (default `origin/stage`).

## Historical files

Leave existing `test_ev*`, `test_tc_ev*`, and migration `test_m*` modules in
place. Do not mass-rename them in this cycle. A later change may rename them
with an explicit map and import updates.

## Carve-outs (not banned)

| Kind | Example | Note |
| ---- | ------- | ---- |
| Behavior names | `test_rvr_trend_slash_accepted.py` | Preferred |
| Eval product modules | `test_evaluation_*.py` | Not a planning `test_ev_` stem |
| Words that share letters | `test_every_*`, `test_event_*` | Not planning dumps |
| WMO AHL `fc_*` fixtures | `fc_taf_with_body.txt` | TTAAii `FC` designator; keep |
| Visibility / TAC samples | `metar_*_m_prefix*` | Not `test_mN_` |

## Agent guidance

- Prefer subject + scenario in the stem.
- Cite EV / TC / M only in docs that agents and developers read, not in
  operator-facing copy.
- See also `.cursor/hooks/test_file_naming_guard.py`, `tests/README.md`, and
  the local rule `test-file-naming.mdc` when present on disk.
