# Reference lookup

`packages/reference-lookup` resolves a 3-letter navaid id or a 4-letter ICAO location indicator to a latitude and longitude.

The live files are OurAirports `navaids.csv` and `airports.csv`, which are public domain. Each file is downloaded once per process. A miss, more than one matching row, or any download error means the source is unavailable. `tac2iwxxm` then uses the checked-in coordinate table.

Unit tests copy a few rows from that dataset. They do not call the host. A pytest plugin fails a test that opens a socket to `ourairports.com` or `davidmegginson.github.io`.
