# Convert and validate

This procedure turns TAC text into IWXXM XML in the web app.

## Convert

1. Open the web app URL for your environment.
2. Paste TAC, or upload a file, or select a sample.
3. Set the IWXXM version and options that your procedure needs.
4. Select **Convert**.
5. Read lint messages on the TAC and the IWXXM result card.

## Validate

1. Select **Validate** on the IWXXM output.
2. Fix TAC problems when validation fails.
3. Select Convert and Validate again after each fix.
4. Download the `.xml` file when the result meets your procedure.
5. Store the file per your local standard operating procedures.

## Soft preview rule

Do not treat soft preview as an official product. Use Convert and Validate for
shared output.

## Troubleshooting

| Symptom | What to do |
|---------|------------|
| Convert fails or empty result | Make sure that the TAC terminator `=` is present. Make sure that the product type is correct. Fix lint errors first. |
| Validation fails | Read the validation messages. Fix the TAC. Make sure that the IWXXM version matches your schema need. |
| Soft preview disagrees with Convert | Trust Convert and Validate. |
| Slow or timeout | Retry one time. If the problem continues, note the time and product. Then contact your support channel. |

## Next step

Read [Work history and privacy](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app-Work-history).
