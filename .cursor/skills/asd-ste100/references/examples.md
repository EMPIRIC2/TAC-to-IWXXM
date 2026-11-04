# Examples (Markdown docs)

Illustrative only. Confirm vocabulary against Issue 9 Part 2 in strict runs.

## Procedural

**Before**

```markdown
If the conversion fails you should check the TAC input and also verify the schema
pin — then re-run the job once you've fixed things.
```

**After (STE-oriented)**

```markdown
If the conversion fails, make sure that the TAC input is correct.
Make sure that the schema pin is correct.
Then operate the job again.
```

## Descriptive

**Before**

```markdown
The dissemination drawer is a comprehensive UI that lets operators seamlessly
leverage multiple BYOC destinations; credentials aren't persisted to sessions.
```

**After (STE-oriented)**

```markdown
The dissemination drawer is the operator panel that sends weather products to
Bring Your Own Credential (BYOC) destinations.
The backend API sends each product to the destinations that the operator selects.
The dissemination drawer does not store destination credentials in work sessions.
```

## Jargon and ambiguous reference

**Before**

```markdown
After the cutover, run it against stage so that path picks up the soft-fail
banner we added in EV-048.
```

**After (STE-oriented + clarity)**

```markdown
After the GIFTs-to-tac2iwxxm package cutover, operate the end-to-end test suite
against the `stage` Git branch deploy environment.
Make sure that the workbench soft-fail lint banner appears.
The soft-fail lint banner shows validation problems that do not block preview.
```

**Check tags**

```text
[Clarity:jargon] docs/guides/x.md:10 — "the cutover"
→ STE: "the GIFTs-to-tac2iwxxm package cutover"
[Clarity:ambiguous-ref] docs/guides/x.md:10 — "run it" / "that path"
→ STE: name the test suite and the deploy environment
[Clarity:assumed-context] docs/guides/x.md:11 — "EV-048"
→ STE: describe the soft-fail lint banner in plain language; keep the id only if required after the name
```

## Check finding shape

```text
[Rule 5.1] docs/guides/convert.md:42 — "Put the bulletin through the worker pipeline until the quarantine store shows a terminal state or the operator acknowledges the soft-fail lint banner."
→ STE: "Send the bulletin through the worker pipeline."
         "Continue until the quarantine store shows a terminal state."
         "Or continue until the operator acknowledges the soft-fail lint banner."
```

## Protected region

**Before / after (unchanged code)**

```markdown
Run:

`uv run pytest packages/tac-validate`

Do not change the command text when applying STE to the surrounding prose.
```
