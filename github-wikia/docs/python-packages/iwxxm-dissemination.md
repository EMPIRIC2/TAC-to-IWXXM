# iwxxm-dissemination

The **iwxxm-dissemination** package helps send IWXXM and bulletin payloads to
operator destinations. It covers multi-database writer-contract helpers, WIS2
and EDIS sinks, AMHS/SWIM/AFS staging stubs, and egress host allowlisting.

The PyPI name is `iwxxm-dissemination`. The import path is `dissemination`.

## Install

```bash
pip install iwxxm-dissemination
```

Requires Python 3.12 or newer. SQL Server via `aioodbc` needs a host ODBC driver
(prefer Microsoft ODBC Driver 18).

## Example

```python
from dissemination import parse_allowlist, validate_egress_host, writer_contract_ddl

allow = parse_allowlist("example.org")
validate_egress_host("example.org", allowlist=allow)
ddl = writer_contract_ddl("sqlite")
```

Egress is fail-closed when the allowlist is empty. One-shot destination
credentials stay with the caller and must not be stored in this library.

## Links

- Source: [EMPIRIC2/TAC-to-IWXXM](https://github.com/EMPIRIC2/TAC-to-IWXXM)
- Related: [tac2iwxxm](https://github.com/EMPIRIC2/TAC-to-IWXXM/wiki/Package-tac2iwxxm)
