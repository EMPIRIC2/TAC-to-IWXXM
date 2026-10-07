# EV-live-map-24h-window decisions

[Corpus: product §F37] [Corpus: decisions] [Corpus: adr/ADR-052]

| ID | Decision |
|----|----------|
| D-EV-MAP24-01 | Deepen F37. No new feature id |
| D-EV-MAP24-02 | Pull, store, and share only reports with `observed_at` within the last **24 hours** of UTC now |
| D-EV-MAP24-03 | Client issue-time presets are **1h, 3h, 6h, 12h, full**; **full** means the entire shared 24h set; remove unbounded All |
| D-EV-MAP24-04 | Age compares to **UTC now**, not the newest report on the map (supersedes EV-map-product-layers filter clock wording) |
| D-EV-MAP24-05 | Keep at most three copies per place/product **inside** the 24h window (`_KEEP` unchanged) |
| D-EV-MAP24-06 | Time presets stay browser-only; `GET /api/v1/live-map` query stays bbox + products |
| D-EV-MAP24-07 | Convert and validate response bodies stay as they are. Staging ship target. Do not promote to production in this cycle |
| D-EV-MAP24-08 | No new env var for the window length in this cycle — fixed 24h product constant |
