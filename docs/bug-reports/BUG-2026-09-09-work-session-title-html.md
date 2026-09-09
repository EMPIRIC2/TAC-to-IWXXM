# Bug report: work-session title stores raw HTML

**ID:** BUG-2026-09-09-work-session-title-html  
**Date:** 2026-09-09  
**PR:** pending  
**Session:** HF-adv-sink-type-title-sanitize  
**Source:** EV-staging-adversarial-e2e F-ADV-02

## Error description

Work-session `title` accepts raw HTML such as `<script>alert(1)</script>`. The UI
renders the title as a text node (HTML-escaped — no XSS execution), but stored
markup is unnecessary and weaker defense-in-depth.

## Error logs

```text
Browser XSS-ish probe (EV-staging-adversarial-e2e AC7):
Title <script>alert(1)</script> stored; UI renders &lt;script&gt;… — no execution
```

## Investigation

1. `WorkSessionPayload.title` has no write-side sanitizer.
2. React text children escape on render (held under adversarial plunge).
3. Strip HTML tags on create/update before persist.

**Root cause:** No title sanitization on write; reliance on render escape only.

## Repro test

- Path: `tests/bugs/test_bug_2026_09_09_work_session_title_html.py`
- Status: green

## Fix

Pydantic validator on work-session create/update payloads strips HTML tags and
normalizes whitespace so persisted titles are plain text.

## Interview record

- Operator asked to proceed with F-ADV-01/02 polish after staging adversarial plunge held.
- Severity: Low / advisory (XSS not executing; defense-in-depth).
