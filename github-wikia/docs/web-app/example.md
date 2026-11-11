# Web app example

This example shows a guest convert of one METAR in the browser. Staging hosts
are used so you can try without production risk.

## Goal

Paste one METAR, convert it to IWXXM XML, validate the XML, and download the
file.

## Sample TAC

```text
METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=
```

## Steps

1. Open `https://app.staging.tac-to-iwxxm.com` in your browser.
2. Stay in guest mode for this quick try.
3. Paste the sample TAC into the TAC input.
4. Make sure that the product type is METAR (or let the app detect METAR).
5. Set the IWXXM version that your procedure needs, or keep the site default.
6. Select **Convert** (or **Convert & validate** when your site shows that label).
7. Read the lint notes on the TAC side.
8. Read the IWXXM result card.
9. Select **Validate** on the IWXXM output when Convert did not already validate.
10. Download the `.xml` file when the result meets your procedure.

## What you should see

| Step | Expected result |
|------|-----------------|
| After paste | The TAC text ends with `=` |
| After Convert | An IWXXM XML card or panel appears |
| After Validate | Schema notes are empty or list only issues you accept |
| After download | A local `.xml` file is saved |

## Soft preview note

Soft preview may show plain language while you edit. Soft preview is advisory
only. Trust Convert and Validate for the file that you keep.

## Optional: sign in for history

1. Sign in with your organization account.
2. Convert the same sample again.
3. Open work history and select the new session.
4. Make sure that the restored TAC matches the sample.

## If something fails

| Symptom | What to do |
|---------|------------|
| Empty convert | Make sure that `=` is present. Fix lint errors. Convert again. |
| Validation fails | Read the messages. Fix the TAC. Convert and validate again. |
| Download missing | Make sure that Convert finished. Then use the download control on the result card. |

## Next step

- Full procedure: [Convert and validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app-Convert-and-validate)
- Other paths: [Examples](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Examples)
