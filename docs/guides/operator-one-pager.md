# TAC → IWXXM — Operator one-pager

Print this page (one sheet). For more detail, read the
[Operator handbook](operator-handbook.md).

## What this app does

This app turns Traditional Alphanumeric Code (TAC) into IWXXM XML.

TAC products include METAR (routine weather report), SPECI (special METAR),
TAF (terminal aerodrome forecast), and related products.

You can download the IWXXM XML, validate it, and (when your site enables send)
send it onward.

## Five steps

1. Open the converter in your browser. Guest mode works for a quick try. Sign in
   to save work history.
2. Paste or upload TAC text. You can also select an example chip. Open profile
   and advanced options from **Change** or setup when you need them.
3. Select **Convert & validate**. The app builds IWXXM XML and runs schema
   checks. Watch the green status strip and any notes.
4. Download the IWXXM XML when the bulletin is valid. Use **Send…** only when
   your site enables dissemination (send to approved destinations).
5. Open **Help** anytime for a short in-app checklist. The handbook has more
   depth.

## Soft preview (plain language)

While you type or edit TAC, the workbench may show a **soft preview**: a
best-effort decode and IWXXM sketch that updates as you edit. Soft preview is
for guidance only. Soft preview is not the official converted product. Soft
preview never means “ready to publish.” Always use **Convert**, then
**Validate IWXXM** on the **XML output** (not the original TAC), for the file
you will archive or distribute.

## Paste tips

- You can paste a WMO abbreviated heading above the report (for example
  `SAXX31 TNCM 081200` before a METAR, or `FTXX31 …` before a TAF). The
  converter removes that heading when it can.
- **Validate IWXXM** needs XML that starts with `<`. If you paste TAC into that
  field, the app asks you to convert first.
- Result status **Needs attention** or **Do not publish** means do not
  distribute that file until you fix the listed problems.

## Version

Pick the IWXXM release line your centre or partner expects (for example a
recent WMO line). If you are unsure, ask your aviation MET supervisor before
you change the default.

## Dissemination (when available)

Some deployments offer send or upload destinations after convert. If that panel
is hidden or disabled at your site, download the XML and use your
organisation’s normal channels.

## Need more?

Open **Help** in the app header, or read the
[Operator handbook](operator-handbook.md) for login, work history, ingest, and
troubleshooting.
