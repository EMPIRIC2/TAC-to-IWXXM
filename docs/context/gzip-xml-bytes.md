# Gzip the IWXXM bytes that match a .xml.gz name

Session: EV-1291-gzip-bytes. Ticket: #1291. Scale: standard. Gate: open.

[Corpus: product §F6] [Corpus: tests]

## Goal

When bulletin convert suggests a filename ending in `.xml.gz`, the bytes that go with that name are gzip-compressed IWXXM. The XML text stays available beside those bytes.

## Out of scope

Do not change the filename pattern. Do not open an AMHS connection. Do not re-check the guidelines' minimum fields (#1292). Do not promote `stage` to `main`. Do not change the operator UI or the HTTP response shape.

## What is already true

A bulletin with a parsed heading, on a profile other than Canada, gets `suggested_filename` from `iwxxm_filename(..., gzip=True)`. That name ends in `.xml.gz`. `ConvertResult.xml` is the IWXXM document as text. Those bytes are not gzip-compressed.

Canada convert does not set that name. The Canada datamart name ends in `.xml`. A paste with no heading leaves `suggested_filename` empty.

## Locked rule

- Keep `xml` as the IWXXM document text.
- When `suggested_filename` ends in `.xml.gz` and `xml` is present, also return gzip bytes that decompress to that text.
- When the suggested name ends in `.xml`, or there is no suggested name, do not return gzip bytes. The XML text stays plain.
- Do not invent a filename for a paste that has no heading.

## Success

- A bulletin convert whose suggested filename ends in `.xml.gz` returns gzip bytes that decompress to the IWXXM document.
- A Canada convert whose suggested name ends in `.xml` stays plain XML.
- A paste with no heading still has no filename.
