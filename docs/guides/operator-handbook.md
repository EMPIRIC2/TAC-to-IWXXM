# TAC → IWXXM — Operator handbook

Short manual for meteorological operators and partners who use the converter
day to day. Start with the [Operator one-pager](operator-one-pager.md) for a
single printed sheet.

## Login and access

- You can try the converter as a **guest**. Guest sessions do not keep cloud
  work history.
- **Sign in** when you need saved work sessions, longer history, or site
  features that require an account.
- Use the email and password issued by your organisation. If sign-in fails,
  make sure that you are on the correct site URL and that caps lock is off.
  Then contact your local IT or MET systems contact. Do not share passwords in
  chat or email.

## Convert and validate

1. Paste TAC, or upload a file, or select samples.
2. Set the **IWXXM version** and other conversion options that your procedure
   requires.
3. Run **Convert**. Review lint messages on the TAC and the IWXXM result card.
4. Run **Validate** on the IWXXM before you treat the file as ready to share.
5. **Download** the `.xml` file and store it per local standard operating
   procedures (SOPs).

**Soft preview** (live decode and sketch while editing) is advisory only.
Official products come from Convert and Validate, not from the preview alone.

## Work history

- When you are signed in, recent sessions appear in the work-history sidebar or
  history page.
- Open a past session to restore TAC and prior outputs for rework.
- Guests: download promptly. Clearing the browser may remove local drafts.
- Privacy settings (footer) control optional local storage. Review those
  settings if you share a workstation.

## Dissemination destinations (high level)

Depending on your deployment, the UI may offer destinations such as databases
or message pathways after convert. Use only destinations your organisation has
configured and approved. If destinations are not shown, download XML and use
your normal dissemination tools. Never paste secret connection strings into
shared tickets or chat.

## Automated ingest — do not rely on paste alone

When your site runs **automated near-real-time ingest** (a poller or worker that
feeds the store), treat that pipeline as the primary path for routine traffic.
Manual paste and convert remain available for ad-hoc fixes, training, and
recovery. Do not rely on manual updates alone for continuous operations if
ingest is available. Confirm with your systems contact whether ingest is active
for your centre.

## Troubleshooting

| Symptom | What to try |
|--------|-------------|
| Convert fails or empty result | Make sure that the TAC terminator (`=`) is present. Make sure that the product type and station groups are correct. Fix lint errors first. |
| Validation red | Read the validation messages. Fix the TAC, or confirm that the IWXXM version matches your schema expectation. |
| Soft preview disagrees with Convert | Trust Convert and Validate. Preview can lag or simplify edge cases. |
| Cannot sign in | Confirm the URL, account, and network. Reset the password only through the approved flow. |
| History empty | Sign in. Check privacy settings. Confirm that you are not in guest mode. |
| Destinations missing | Destinations are likely disabled for your site. Use download and local channels. |
| Slow or timeout | Retry once. If the problem continues, note the time and product and contact support. |

## Where to get help

- In-app **Help** opens the one-pager.
- This handbook covers day-to-day procedures.
- Local MET or IT support covers accounts, network, and approved dissemination
  paths.
