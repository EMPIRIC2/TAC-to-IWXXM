# Getting started

This page tells you which path to use and where the public hosts are.

## Choose a path

| Your work | Open |
|-----------|------|
| Convert reports in a browser | [Web app overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app) |
| Call conversion from software | [HTTP API overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API) |
| Convert or examine reports in Python | [Python packages overview](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Python-packages) |

## Public hosts

| Environment | Web app | HTTP API |
|-------------|---------|----------|
| Production | `https://app.tac-to-iwxxm.com` | `https://api.tac-to-iwxxm.com` |
| Staging | `https://app.staging.tac-to-iwxxm.com` | `https://api.staging.tac-to-iwxxm.com` |
| Local development | `http://localhost:18000` | `http://localhost:18001` |

## Interactive API reference

1. Open `{API}/docs` in a browser.
2. Replace `{API}` with the HTTP API base URL for your environment.
3. Use the interactive page to inspect routes and try requests.

The machine-readable OpenAPI document is `{API}/openapi.json`.

## Terms used on these pages

| Term | Meaning |
|------|---------|
| TAC | Traditional Alphanumeric Code aviation weather text |
| IWXXM | WMO XML form for the same aviation weather products |
| METAR | Routine aerodrome weather report in TAC |
| SPECI | Special METAR issued when conditions change |
| TAF | Terminal aerodrome forecast in TAC |
| Convert | Turn TAC text into IWXXM XML |
| Validate | Make sure that IWXXM XML meets schema rules |
| Lint | Check TAC text against product rules before convert |

## Examples (same sample METAR)

| Path | Open |
|------|------|
| Web app | [Web app example](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app-Example) |
| HTTP API | [HTTP API example](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-Example) |
| Python packages | [Python packages example](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Python-packages-Example) |

Index: [Examples](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Examples)

## Next step

- Web app users: [Convert and validate](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Web-app-Convert-and-validate)
- API users: [First convert call](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/HTTP-API-First-convert-call)
- Python users: [tac2iwxxm](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac2iwxxm)
