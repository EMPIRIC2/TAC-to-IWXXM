# tac-validate test naming

[Corpus: tests]

## Current inventory (do not mass-rename in place)

| Prefix                       | Role                       | Forward rule                                              |
| ---------------------------- | -------------------------- | --------------------------------------------------------- |
| `test_<behavior>_…`          | Preferred                  | Keep adding these                                         |
| `test_ev*` / `test_ev040_*`  | Evolve-session dumps       | Prefer behavior names; cite EV in docstring               |
| `test_tc_f*` / `test_tc_ev*` | Feature / TC archives      | Prefer behavior names; cite TC in docstring or marker     |
| `test_m4_*`                  | Milestone detector routing | Prefer `test_<product>_detector_routing.py` for new files |

A later PR may rename historical `test_tc_*` / `test_ev*` modules with an
explicit mapping table and import/path updates. Until then, leave filenames
stable.

## New modules

```text
test_<subject>_<scenario>.py
```

Example: `test_rvr_trend_slash_accepted.py` rather than `test_tc_ev999_001_rvr.py`.
