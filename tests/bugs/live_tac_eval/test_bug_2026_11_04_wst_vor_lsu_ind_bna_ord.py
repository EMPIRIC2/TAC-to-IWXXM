"""US WST convective SIGMET convert must resolve LSU/IND/BNA/ORD VOR ids.

Live 30d eval: 16 US convective SIGMET convert hard fails with
``PARSE_ERROR: unknown VOR reference`` for LSU, IND, BNA, and ORD (plus peers
on the same FROM-chains). Seed the offline VOR table the same way as prior
chart-id / ambiguous OurAirports misses.

[Corpus: product §F6] [Corpus: tests]
"""

from __future__ import annotations

from tac2iwxxm.geometry.reference_point import resolve_vor

from tac2iwxxm import convert

# Live-eval truncations expanded to minimal FROM-chains that hit each miss.
_ORD_CHAIN = (
    "WSUS32 KKCI 031655\n"
    "MKCC WST 031655\n"
    "CONVECTIVE SIGMET 77C\n"
    "VALID UNTIL 1855Z\n"
    "WI IL LM\n"
    "FROM 30ESE GRB-10N ORD-60SW GRB\n"
    "AREA TS MOV FROM 24025KT. TOPS TO FL350.\n"
)

_LSU_CHAIN = (
    "WSUS32 KKCI 032055\n"
    "MKCC WST 032055\n"
    "CONVECTIVE SIGMET 91C\n"
    "VALID UNTIL 2255Z\n"
    "TN KY IL MS LA MO AR TX\n"
    "FROM 30ENE MEM-40W LSU-30SW MSL-30ENE MEM\n"
    "AREA TS MOV FROM 25020KT. TOPS TO FL400.\n"
)

_IND_CHAIN = (
    "WSUS32 KKCI 040655\n"
    "MKCC WST 040655\n"
    "CONVECTIVE SIGMET 17C\n"
    "VALID UNTIL 0855Z\n"
    "TN KY IN AL IL MO\n"
    "FROM IND-60ESE BNA-40SSW IND\n"
    "AREA TS MOV FROM 26015KT. TOPS TO FL380.\n"
)

_BNA_CHAIN = (
    "WSUS32 KKCI 040855\n"
    "MKCC WST 040855\n"
    "CONVECTIVE SIGMET 25C\n"
    "VALID UNTIL 1055Z\n"
    "TN AL MS\n"
    "FROM 40SSW BNA-30SW VUZ-20NW BNA\n"
    "AREA TS MOV FROM 27020KT. TOPS TO FL360.\n"
)


def test_resolve_vor_seeds_lsu_ind_bna_ord_and_grb() -> None:
    for code in ("LSU", "IND", "BNA", "ORD", "GRB"):
        lat, lon = resolve_vor(code)
        assert -90.0 <= lat <= 90.0
        assert -180.0 <= lon <= 180.0


def test_wst_convert_ok_for_ord_lsu_ind_bna_chains() -> None:
    for tac in (_ORD_CHAIN, _LSU_CHAIN, _IND_CHAIN, _BNA_CHAIN):
        result = convert(
            tac,
            product="SIGMET",
            profile="us_nws_convective_sigmet",
            iwxxm_version="2023-1",
        )
        assert result.ok is True, [f"{i.code}: {i.message}" for i in result.issues]
        assert result.xml
