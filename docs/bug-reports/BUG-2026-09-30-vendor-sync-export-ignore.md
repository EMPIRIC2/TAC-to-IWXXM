# BUG-2026-09-30 — Vendor sync checksum mismatch on an unchanged pin

| Field | Value |
| --- | --- |
| **Status** | fixed |
| **Feature** | M6 vendor snapshot sync |
| **Severity** | medium (scheduled Vendor Schema Sync red every week; not a product-runtime failure) |
| **Classification** | CI / sync script |
| **Issue** | #1318 (epic #1307) |
| **Run** | https://github.com/EMPIRIC2/TAC-to-IWXXM/actions/runs/36425616865 |

## Error description

Scheduled Vendor Schema Sync on `main` fails while refreshing `vendor/schemas/iwxxm`
even though `check_upstream.py --update` reports the release pins already match.

## Error logs

```
ValueError: post-sync checksum mismatch for iwxxm:
  manifest=81f7e418a5e2b55947510802723e216fd93592cf82b874ac7d50ca5502cb2157,
  actual=306b33b1851804519dbaefd31da5d0359cd1337c1a66a94705377b7be1daddee
```

`scripts/vendor/sync_iwxxm.py` `sync_from_manifest`, after
`uv run python scripts/vendor/sync_iwxxm.py --manifest vendor/manifest.json --no-legacy --no-verify`.

## Investigation

| When | Finding |
| --- | --- |
| 2026-09-30 | Local `vendor/schemas/iwxxm` hashes to the manifest value `81f7e418…` (2041 files). |
| 2026-09-30 | GitHub archive of pin `35180cbe` hashes to the CI actual value `306b33b1…` (1008 files). |
| 2026-09-30 | `git checkout` of that pin hashes to `660380ff…` (1297 files). Adding the nested `3.0.0` tree brings it back to `81f7e418…` (2041 files). |
| 2026-09-30 | Upstream `.gitattributes` marks `/externalSchema`, `/documentation`, `/bin`, `/IWXXM/XMI`, dotfiles, and `/*.md` as `export-ignore`. |

The July 2026 fix cleared `tree_sha256` only when the release tag changed, and
`--no-verify` only skips `verify_manifest_integrity`. An unchanged pin still
compares `tree_sha256` after the replace.

## Root cause

Two replacements happen on every sync of the pinned commit:

1. The GitHub archive tarball omits `export-ignore` paths, including
   `externalSchema/` (AIXM and other imported schemas). The committed snapshot
   is a full checkout.
2. `iwxxm-3.0.0` lives at `vendor/schemas/iwxxm/3.0.0`, inside the parent
   bundle. Replacing the parent deletes that profile-line tree. It is not part
   of the v2025-2 pin, and the parent hash includes it.

## Repro test

| Field | Value |
| --- | --- |
| Path | `tests/bugs/test_bug_2026_09_30_vendor_sync_export_ignore.py` |
| Also | `tests/scripts/test_sync_iwxxm.py` (`test_fetch_github_tree_checks_out_export_ignore_paths`, `test_sync_preserves_nested_profile_line`) |

## Fix

- Fetch the pin with `git fetch` + `git checkout` so `export-ignore` paths stay.
- Stash nested bundle directories (the `3.0.0` profile line) across the parent
  replace and restore them afterward.

[Corpus: tech-spec] [Corpus: tests]
