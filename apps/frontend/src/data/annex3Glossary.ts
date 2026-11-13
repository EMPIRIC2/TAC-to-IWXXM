/**
 * Annex 3 Glossary seed (F38) — short original paraphrases only.
 *
 * Citation: ICAO Annex 3 (2025), Chapter 1. Not official ICAO text.
 * Get the official manual from ICAO. Do not paste verbatim Annex definitions here.
 */

/** Shared citation shown on the Glossary page and in hover tips. */
export const ANNEX3_GLOSSARY_CITATION = 'ICAO Annex 3 (2025), Chapter 1' as const;

/**
 * Type `Annex3GlossaryEntry`.
 * @example
 * const _ = true;
 */
export type Annex3GlossaryEntry = {
  /** Stable slug for deep links. */
  id: string;
  /** Primary display term. */
  term: string;
  /** Alternate spellings or abbreviations used for matching. */
  aliases?: string[];
  /** One-to-two sentence hover blurb. */
  shortBlurb: string;
  /** Page paraphrase (still short; not official text). */
  pageBody: string;
  /** Source citation line. */
  citation: typeof ANNEX3_GLOSSARY_CITATION;
};

/**
 * Type `Annex3LimitedMeaningNote`.
 * @example
 * const _ = true;
 */
export type Annex3LimitedMeaningNote = {
  id: string;
  term: string;
  note: string;
};

/**
 * Hover-eligible glossary entries (longest-match prefers multi-word terms).
 */
export const ANNEX3_GLOSSARY_ENTRIES: readonly Annex3GlossaryEntry[] = [
  {
    id: 'visibility',
    term: 'Visibility',
    shortBlurb:
      'How far an observer can see and identify objects in daylight, or lighted objects at night, for aviation reports.',
    pageBody:
      'Visibility is the greatest distance at which an observer can see and identify specified objects in daylight, or lighted objects at night, for aviation reports.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'rvr',
    term: 'Runway visual range',
    aliases: ['RVR'],
    shortBlurb:
      'How far a pilot on the runway center line can see runway markings or lights for that runway.',
    pageBody:
      'Runway visual range (RVR) is the distance a pilot on the runway center line can see. The pilot can see runway markings or the lights that mark the runway.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'sigmet',
    term: 'SIGMET',
    shortBlurb:
      'A meteorological watch office sends this warning about specified en-route weather that can affect aircraft safety.',
    pageBody:
      'A SIGMET is information from a meteorological watch office about specified en-route weather that can affect the safety of aircraft operations.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'airmet',
    term: 'AIRMET',
    shortBlurb:
      'Information about specified en-route weather that can affect low-level flights. The severity is below SIGMET.',
    pageBody:
      'An AIRMET describes specified en-route weather that can affect the safety of low-level aircraft operations. A related area forecast did not already cover that weather.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'fir',
    term: 'Flight information region',
    aliases: ['FIR'],
    shortBlurb:
      'Airspace with defined limits where flight information service and alerting service operate.',
    pageBody:
      'A flight information region (FIR) is airspace of defined dimensions where flight information service and alerting service operate.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'mwo',
    term: 'Meteorological watch office',
    aliases: ['MWO'],
    shortBlurb:
      'An office that watches weather that affects flight and that sends SIGMET and related information.',
    pageBody:
      'A meteorological watch office watches meteorological conditions that affect flight operations and sends SIGMET and related information as required.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'iwxxm',
    term: 'IWXXM',
    shortBlurb:
      'The ICAO and WMO XML format for digital exchange of aviation weather information.',
    pageBody:
      'IWXXM is the ICAO Meteorological Information Exchange Model. It is an XML form for digital exchange of aviation weather information.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'prevailing-visibility',
    term: 'Prevailing visibility',
    shortBlurb:
      'The visibility value that best represents conditions around the aerodrome under Annex 3 report rules.',
    pageBody:
      'Prevailing visibility is the visibility value that represents conditions at the aerodrome under the report rules in Annex 3.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'vaac',
    term: 'VAAC',
    aliases: ['Volcanic ash advisory centre'],
    shortBlurb:
      'A center that sends advisory information on volcanic ash for aviation.',
    pageBody:
      'A volcanic ash advisory centre (VAAC) sends advisory information on volcanic ash clouds that can affect aviation.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'tcac',
    term: 'TCAC',
    aliases: ['Tropical cyclone advisory centre'],
    shortBlurb:
      'A center that sends advisory information on tropical cyclones for aviation.',
    pageBody:
      'A tropical cyclone advisory centre (TCAC) sends advisory information on tropical cyclones for aviation.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'aerodrome',
    term: 'Aerodrome',
    shortBlurb:
      'A defined area on land or water for aircraft arrival, departure, and surface movement.',
    pageBody:
      'An aerodrome is a defined area on land or water (with buildings, installations, and equipment) for aircraft arrival, departure, and surface movement.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'flight-level',
    term: 'Flight level',
    aliases: ['FL'],
    shortBlurb:
      'A surface of constant atmospheric pressure that aircraft use as a vertical reference.',
    pageBody:
      'A flight level is a surface of constant atmospheric pressure related to a specific pressure datum. Set pressure intervals separate that surface from other such surfaces.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'observation',
    term: 'Observation',
    shortBlurb:
      'A statement of meteorological conditions that an observer records at a stated time and place.',
    pageBody:
      'An observation is a statement of the meteorological conditions that an observer records at a specified time and location.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
  {
    id: 'forecast',
    term: 'Forecast',
    shortBlurb:
      'A statement of expected meteorological conditions for a specified time or period and area or portion of airspace.',
    pageBody:
      'A forecast is a statement of expected meteorological conditions for a specified time or period, and for a specified area or portion of airspace.',
    citation: ANNEX3_GLOSSARY_CITATION,
  },
] as const;

/**
 * §1.2 limited-meaning notes — Glossary page subsection only (never hover-linked).
 */
export const ANNEX3_LIMITED_MEANING_NOTES: readonly Annex3LimitedMeaningNote[] = [
  {
    id: 'provide',
    term: 'provide',
    note: 'In Annex 3, provide has a limited procedural meaning for services that States make available. It does not apply to every ordinary use of the word.',
  },
  {
    id: 'issue',
    term: 'issue',
    note: 'In Annex 3, issue often means that an office officially releases a meteorological product. It does not mean a software finding or a general topic.',
  },
  {
    id: 'supply',
    term: 'supply',
    note: 'In Annex 3, supply can mean delivery of meteorological information under the Annex service frame.',
  },
] as const;

/**
 * Look up a glossary entry by id.
 *
 * @param id - Entry slug
 * @returns Matching entry or undefined
 * @example
 * const _ = true;
 */
export function getAnnex3GlossaryEntry(id: string): Annex3GlossaryEntry | undefined {
  return ANNEX3_GLOSSARY_ENTRIES.find((entry) => entry.id === id);
}
