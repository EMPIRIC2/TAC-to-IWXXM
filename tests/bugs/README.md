# Bug and qa-gap regressions

[Corpus: tests]

Pinned repros for hotfix and qa-gap finds. CI runs the whole tree:

```bash
uv run pytest tests/bugs -m "not live and not live_api" --no-cov
# or
make test-bugs
```

## Layout

| Path | Purpose |
|------|---------|
| `auth/` | Login, logout, admin, RLS, auth bypass |
| `work_session/` | Work-history persist, titles, staging mount |
| `tac/` | TAC decode, lint, convert, product bugs |
| `frontend/` | UI, map, Playwright, baked hosts |
| `ci_deploy/` | Docker, Render, Actions, promote, vendor sync |
| `qa_gap/` | QA-gap and staging/OpenAPI contract regressions |
| `dissemination/` | Sink / dissemination regressions |
| `worker/` | Background worker poller |
| `supabase/` | Sync CLI / service-key (non-auth-primary) |
| `quality/` | Metrics scripts, catalog storage, GH project hooks |
| `live_tac_eval/` | Live-tac-eval skill finds (see that README) |
| `test_bug_log_repro_paths.py` | Meta: every `docs/bug-reports/BUG-*.md` still has a repro |

## Naming (new files)

- Hotfix: `tests/bugs/<theme>/test_bug_YYYY_MM_DD_<slug>.py`
- QA gap: `tests/bugs/qa_gap/test_qa_gap_YYYY_MM_DD_<slug>.py`
- Live eval: `tests/bugs/live_tac_eval/test_<behavior>.py`
- Pair with `docs/bug-reports/BUG-YYYY-MM-DD-<slug>.md` when using bug-investigation
- Prefer a behavior slug in the filename; put session/TC ids in the module docstring

Do not mass-rename historical filenames without a mapping table and path updates.

## Path checks

`test_bug_log_repro_paths.py` resolves default repros by basename under
`tests/bugs/**`. Overrides cover reports whose filename differs from the report stem.

## Repo-root paths in tests

Theme modules sit one directory deeper than the old flat layout. Resolve the
repo root with `Path(__file__).resolve().parents[3]` (or walk upward for
`pyproject.toml`). The meta check `test_bug_log_repro_paths.py` at the bugs
root still uses `parents[2]`.
