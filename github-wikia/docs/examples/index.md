# Examples

This section shows three basic paths for the same sample METAR. Use the path
that matches your work.

## Sample TAC

All three examples use this Traditional Alphanumeric Code (TAC) METAR:

```text
METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005=
```

The terminator `=` must stay at the end of the TAC string.

## Choose an example

| Path | Open |
|------|------|
| Browser (web app) | [Web app example](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app-Example) |
| HTTP API | [HTTP API example](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-Example) |
| Python packages | [Python packages example](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Python-packages-Example) |

## What success looks like

| Path | You finish when |
|------|-----------------|
| Web app | You download IWXXM XML after Convert and Validate |
| HTTP API | You receive convert JSON that includes IWXXM XML |
| Python packages | `convert` returns `ok` and optional lint or validate reports pass |

## Related pages

- [Getting started](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Getting-started)
- [Web app overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app)
- [HTTP API overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API)
- [Python packages overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Python-packages)
