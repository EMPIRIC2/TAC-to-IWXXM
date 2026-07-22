# F19 mock destination harness (AMHS / SWIM / AFS HTTP stand-in).

# Local/CI only — not live AMHS/SWIM/AFS protocols.

#

# make compose-mock-byoc-up # includes byoc-f19 when using full profile services

# curl http://127.0.0.1:19099/health

# curl -X POST http://127.0.0.1:19099/amhs --data-binary @sample.iwxxm.xml
