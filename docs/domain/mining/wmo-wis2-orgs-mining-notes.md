# WIS2 orgs — focused mining notes

**Status:** working notes (not normative). Verify against the cited repositories.  
**Focus of this pass:** F8 ingest routing and F17 WIS2 publish. Not TAC grammar or IWXXM encode.  
**Ticket:** [#806](https://github.com/EMPIRIC2/TAC-to-IWXXM/issues/806)  
**Date mined:** 2026-10-02

**Promote durable findings into:**

| Doc | Path |
|-----|------|
| Master URL catalog | [../rules/RULE_SOURCE_URLS.md](../rules/RULE_SOURCE_URLS.md) |
| Coverage matrix | [../rules/COVERAGE_MATRIX.md](../rules/COVERAGE_MATRIX.md) |
| Earlier org survey | [wmo-im-org-mining-notes.md](./wmo-im-org-mining-notes.md) |

| Item | Value |
|------|-------|
| Title | WIS2 exchange sources (WMO org + wmo-im) |
| Publisher | World Meteorological Organization |
| Official landing | https://github.com/World-Meteorological-Organization/wis2box |
| Access | public |
| Label | normative-exchange for topics and notification messages; informative for the reference node and guides |

---

## What this source is / is not

| Is | Is not |
|----|--------|
| The reference WIS2 node and the standards for topics and notifications | TAC grammar, Annex 3 SARPs, or IWXXM XSD/Schematron |
| The canonical home of wis2box under the WMO GitHub org | A reason to replace the project Compose harness with a full wis2box stack |

The project harness stays the lightweight MQTT and HTTP stand-in (F17). The WMO org repository is the reference node to cite, not a dependency to vendor.

---

## Canonical runtime home

wis2box moved from `wmo-im` to [World-Meteorological-Organization/wis2box](https://github.com/World-Meteorological-Organization/wis2box). That repository describes itself as the reference implementation of a WMO WIS2 node. `wmo-im` keeps the standards (topics, notification message, guide, manual, cookbook) and training.

---

## World Meteorological Organization repos

Every public repository on 2026-10-02. Rank is for F8/F17 only.

| Repo | Rank | Why |
|------|------|-----|
| wis2box | useful | Reference WIS2 node. Cite this, not a `wmo-im` copy. |
| wis2box-api | useful | Publish and API surface next to the node. |
| wis2box-auth | useful | Auth piece of a real node. The project harness does not run it. |
| wis2box-release | useful | Release image set for a real node. |
| wis2box-minio | useful | Object store used by a real node. |
| pywis-pubsub | useful | Subscribe and download client. |
| pywis-topics | useful | Topic-hierarchy helper. Pair with `wmo-im/wis2-topic-hierarchy`. |
| wis2downloader | useful | Current broker download path. |
| wis2box-ui | watch | Operator UI. Informative only. |
| wis2box-webapp | watch | Metadata and flow UI. Informative only. |
| wis2box-minio-console | watch | Object-store console. Ops only. |
| wis2box-ansible | watch | Install automation, marked WIP. |
| pywcmp | watch | WCMP metadata checks. Relevant only if discovery metadata enters F17. |
| wis2downloader-v1 | skip | Archived. Superseded by `wis2downloader`. |
| csv2bufr | skip | BUFR transform. Not aviation TAC. |
| csv2bufr-templates | skip | Templates for that transform. |
| bufr2geojson | skip | BUFR to GeoJSON. |
| synop2bufr | skip | SYNOP to BUFR. |
| dim_eccodes_baseimage | skip | eccodes base image. |
| capvalidator | skip | CAP alerts. Not an F6 product. |
| cap2geojson | skip | CAP to GeoJSON. |
| cap-composer | skip | CAP composer. |
| .github | skip | Org metadata. |
| world-meteorological-organization.github.io | skip | Org pages. |

---

## wmo-im WIS2 slice

| Repo | Rank | Why |
|------|------|-----|
| wis2-topic-hierarchy | useful | Normative topic leaves. Aviation is under `weather/aviation/`. |
| wis2-notification-message | useful | MQP notification encoding. Drafts at https://wmo-im.github.io/wis2-notification-message |
| wis2-cookbook | useful | `cookbook/sections/data-publishers/publishing-aviation-data.adoc` |
| wis2-guide | useful | IWXXM-on-WIS2 / SWIM prose. |
| wis2-manual | watch | Manual prose. Not a runtime schema. |
| wis2box-training | watch | Exercises. Not runtime source of truth. |
| GTStoWIS2 | watch | Archived AHL-to-topic lineage. |
| pywiscat | watch | Global Discovery Catalogue client. Discover only. |
| wis2-gdc | watch | Global Discovery Catalogue reference. |
| wis2-gb | watch | Global Broker reference. |
| wis2-gc | watch | Global Cache reference. |
| wis2-grep | watch | Global Replay reference. |
| wis2-transition-guide | watch | Transition prose. |
| wis2dev | watch | Development network. |
| wis2-operation | watch | Operations guide. |
| wis2-metric-hierarchy | watch | Metrics, not aviation products. |
| wis2-monitoring-events | watch | Monitoring events. |
| wis2-monitoring-events-codelists | watch | Codes for those events. |
| wis2-global-services-testing | watch | Global-services tests. |
| wis2-subscription-manager | watch | Desktop subscription tool. |
| wis2box-data-subscriber | watch | Automatic weather station subscriber into wis2box. |
| wis2-champions | skip | Meeting documents. |
| wis2-scgdc | skip | Sensor-centre catalogue. |
| wis2-sensor-global-cache | skip | Sensor cache. |
| Archived (`WIS2`, wis2-live, wis2pilot, wis2box-ui-admin, wis2box-ftp, wis2-metadata-search, wis2-data-analysis) | skip | Archived. Do not cite as current. |

---

## Aviation topic leaves

`topic-hierarchy/earth-system-discipline/weather/aviation/index.csv` on 2026-10-02 lists three operational leaves:

| Leaf | Description |
|------|-------------|
| metar | Aerodrome observation |
| taf | Aerodrome forecast |
| qvaci | Quantitative volcanic ash concentration information |

SPECI, SIGMET, AIRMET, VAA, and TCA have no leaf in that file. Do not invent topics. F8 routing and F17 publish for those products stay on the existing bulletin path until WMO adds a leaf.

---

## Gap table

| Need | Source | Status |
|------|--------|--------|
| Cite the reference node | `World-Meteorological-Organization/wis2box` | Covered by this dig and the catalog row |
| Topic for METAR and TAF | `wis2-topic-hierarchy` aviation leaves | Covered |
| Topic for SPECI, SIGMET, AIRMET, VAA, TCA | same file | Gap in the WMO hierarchy. Out of scope to invent a leaf |
| QVACI topic | `qvaci` leaf | Covered as a topic name. QVACI encode stays deferred |
| Notification shape | `wis2-notification-message` | Covered as a citation. The harness does not emit MQP GeoJSON |
| Local publish test | Compose wis2box harness | Covered. It is a stand-in, not the WMO stack |
| Buffer / consumer compatibility | #911 | Already tracked. No second ticket |
| Full in-repo WIS2 node | wis2box-release | Out of scope |

No child issue from this pass. The missing aviation leaves are a WMO hierarchy gap, and the buffer work is already #911.

---

## Domain-knowledge cross-check

| Earlier claim | This pass | Resolution |
|---------------|-----------|------------|
| wis2box treated as a wmo-im service to skip for encode | Runtime home is the WMO org repository | Defer to this pass for F17 citations. Still skip wis2box for TAC encode |
| Aviation leaves are metar, taf, qvaci | Re-read `aviation/index.csv` on 2026-10-02 | Confirmed. No new leaves |
