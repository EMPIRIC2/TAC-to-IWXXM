# GAMET spike — parse-only disposition (EV-089 / #920)

> **Corpus**: [Corpus: domain-profiles] · **Issue**: [#920](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/920)  
> **Decision**: `D-EV089-gamet` · **Status**: accepted (Spec 2026-08-29)

## Verdict

**Parse-only / OOS for IWXXM emit.**

GAMET (WMO TAC low-level area forecast, often `FAxx`) remains TAC in operational circuits
(including SADIS in places). There is **no** IWXXM message type / schema mapping to target for
conversion in the current WMO IWXXM pin set used by this repo.

## Implications for #920

| Action | Allowed? |
|--------|----------|
| Accept GAMET TAC in fixtures under `BR_DECEA` (ops/archive) | Yes |
| tac-validate lexical/parse checks if already generic | Optional Build |
| Convert GAMET → IWXXM | **No** (v1) |
| Add `GAMET` to convert product enum / OpenAPI | **No** (v1) |
| List GAMET in other national `products:` convert allowlists | **No** |

## Profiles

- **BR_DECEA**: may include GAMET TAC fixtures; convert allowlist excludes GAMET.
- **IN / JP / others**: do not list GAMET (not issued or N/A).

## Future reopen

Reopen only when WMO publishes an IWXXM GAMET (or successor) schema and this project pins it
via vendor sync — then a dedicated evolve cycle, not a silent #920 deepen.

## EV-094 reaffirmation (2026-08-31)

Deepen research (`EV-094…/evidence/deep-research-report-deepen.md`) found **no** GAMET /
low-level area-forecast message type in current IWXXM releases. Disposition **unchanged**:
parse-only; no convert enum; BR fixtures only (D-EV094-gamet).

## References

- Session research: `EV-089…/evidence/deep-research-report-920.md`
- Deepen research: `EV-094…/evidence/deep-research-report-deepen.md`
- Playbook thin path: [NATIONAL_PROFILE_PLAYBOOK.md](NATIONAL_PROFILE_PLAYBOOK.md)
- Tracking: [#1098](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/1098)
