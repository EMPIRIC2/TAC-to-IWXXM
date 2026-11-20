/**
 * Airport record used by ICAO autocomplete and validation.
 * @example
 * const _ = true;
 */
export interface Airport {
  icao: string;
  iata?: string;
  name: string;
  city: string;
  country: string;
}
