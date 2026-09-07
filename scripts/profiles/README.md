# Profile scaffold helpers (EV-088 / #1044)

- `scaffold_national_profile.py` — copy `_template/` stubs for a new semantic profile id.

```bash
python3 scripts/profiles/scaffold_national_profile.py --id UK_METOFFICE --dry-run
python3 scripts/profiles/scaffold_national_profile.py --id UK_METOFFICE
```

See `docs/domain/profiles/NATIONAL_PROFILE_PLAYBOOK.md`.
