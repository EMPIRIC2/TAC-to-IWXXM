# Trusted Publisher checklist — EV-028 / T2.2

Configure **before** pushing `*-v0.1.1` tags (T3.3).

For **each** of `tac-validate`, `iwxxm-validate`, `tac2iwxxm`:

1. Open Project → **Publishing**  
   - https://pypi.org/manage/project/tac-validate/settings/publishing/  
   - https://pypi.org/manage/project/iwxxm-validate/settings/publishing/  
   - https://pypi.org/manage/project/tac2iwxxm/settings/publishing/
2. Add GitHub Trusted Publisher:

| Field | Value |
|-------|--------|
| Owner | `EMPIRIC2` |
| Repository | `TAC-to-IWXXM` |
| Workflow | `pypi-publish.yml` |
| Environment | `pypi` |

3. Remove any publisher still pointing at the pre-transfer owner/repo.
4. On [account publishing](https://pypi.org/manage/account/publishing/), clear leftover *pending* publishers for this repo if listed.
5. Confirm GitHub Environment **`pypi`** exists:  
   https://github.com/EMPIRIC2/TAC-to-IWXXM/settings/environments

Do **not** re-add a long-lived `PYPI_API_TOKEN` to Actions secrets.
