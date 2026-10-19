# Four open Playwright bugs

Session: EV-100-four-playwright-bugs. Scale: standard. Gate: closed.

[Corpus: tests] [Corpus: product]

## Goal

Finish #1434, #1437, #1438, and #1439 so each acceptance check is true on `stage` and each issue can close. One pull request per bug only if `stage` is still short of that issue's acceptance.

## Out of scope

#1432, #1433, #1435, #1436, #1448. Product behavior. A new test framework. Operator-facing copy.

## Locked intake

- All four bugs, in parallel.
- Tests and CI only. Existing Playwright stack.
- Success: red-then-green regression, then a pull request into `stage`, when the tree is still red.
- Angles: lint-format-typecheck, tests, qa-quality, contracts, human-readable.
- No local UI preview. No CORS or H4–H5 change.

## What is already true

Prior cycles merged into `stage`: #1443 (#1434), #1445 (#1437), #1440 (#1438), #1442 (#1439). Those sessions left the issues open on purpose.

On `origin/stage` at this pass:

- #1434: no `toHaveCount(0)` in `apps/e2e` lacks a same-test proof the locator can match, or a comment that it can.
- #1437: the logout block in `apps/e2e/tc-ev060-1006-auth.e2e.spec.ts` does not call `test.skip`.
- #1438: the UJ-064 block in `apps/e2e/tc-ev061-uj064-068.e2e.spec.ts` has no `segments.count()` guard, and it requires `decode-segments`, visibility, and no raw `<?xml`.
- #1439: `requireF6ePickers` in `apps/e2e/f6e-product-profile-pickers.e2e.spec.ts` does not call `test.skip`.

`CI/CD Pipeline` on `stage` succeeded for `7f5ebbb0` (run 39255268389, 2026-10-19). The issues are still open and their checkboxes are unchecked.

The local regression file `tests/bugs/test_qa_gap_2026_10_18_epic_1431.py` is untracked. Its four tests passed against the dirty worktree in 0.05s. That file is not on `stage`.

## Must not break

Conversion, auth, and picker behavior. The sibling login-persist skip (#1437 out of scope). `apps/e2e/tc-ev060-uj059-063.e2e.spec.ts` (#1439 out of scope).

## Worktree

Current branch is `evolve/plain-language`, with unrelated uncommitted edits, including the three specs above versus `origin/stage`. Do not build these bugs on this branch. A later build uses a clean worktree from `origin/stage`.

## Interview record

Evolve intake and routing approval locked goal, scope, constraints, success, scale, and angles. Session type is evolve. Tickets are #1434, #1437, #1438, #1439. Urgency is normal. Users are people reading CI: a green Playwright run must not hide a missing control, a skipped logout, empty decode rows, or a missing product picker. Journeys touched only as existing specs: auth logout, UJ-064 validate IWXXM, F6 product pickers, and absence checks across `apps/e2e`. Standing docs already cite [Corpus: tests] and [Corpus: product]. No CORPUS gap. No new feature id. Deploy intent is none beyond pull requests into `stage`.

Memory session-open returned no matches. Historical retrieve returned one cross-project question about RAG merge gates (`q-verification-gate`, score 0.0714). Waived: it does not apply to these Playwright bugs.

## Decision

Keep the cycle. Prove the runtime lines on a clean worktree from `stage`: a missing logout fixture fails, zero decode rows fail, an absent picker fails, and the edited Playwright specs pass. Add regression tests for those four bugs to CI. The `tests/bugs` job in `.github/workflows/ci-cd.yml` already runs `pytest tests/bugs`; the regression module is still untracked, so CI does not run it yet.

## Next

Requirements manifest: delta [Corpus: tests] only. No feature-list, spec, journey, API, or deploy rewrite.
