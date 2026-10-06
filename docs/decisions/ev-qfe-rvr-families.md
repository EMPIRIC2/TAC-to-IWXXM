# EV-qfe-rvr-families

[Corpus: product §F9] [Corpus: decisions]

## Decision

`R19/290052` and `QFE747` on SPECI ULOO are real groups, not junk. Explain them
in the existing METAR and SPECI decoder after the build gate opens. Do not add a
product id.

## Why

The decoder already explains runway visual range of the form `R19/2900`. The
Pskov token has six digits after the slash, which is the older runway state
group: runway 19, wet, most of the runway covered, depth under 1 mm, friction
0.52. Annex 3 dropped that group when the global runway report replaced it.
Russia still sends it.

`QFE747` is the aerodrome pressure in millimetres of mercury, about 996 hPa.
The report already has QNH `Q1002`. The gap fits Pskov’s elevation. Russian
remarks often write both units (`QFE747/0996`).

The Error label on those chips means the decoder did not explain the token.
It is not a validation failure. The United States decode profile did not cause
the miss: the rest of the report is still in metric units.

## Build

The gate is open. The METAR and SPECI decoder explains both families, including
the two-unit QFE form and a cleared runway. Ordinary four-digit runway visual
range stays a visual range.
