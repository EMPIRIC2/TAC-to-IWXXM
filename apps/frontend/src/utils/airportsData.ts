/**
 * Airport data utility for ICAO code validation and lookup.
 * This replaces the vulnerable airport-codes package.
 * @example
 * const _ = true;
 */

import type { Airport } from '@/models/airport';
import { airportsData } from '@/data/airportsCatalog';

export type { Airport } from '@/models/airport';
export { airportsData } from '@/data/airportsCatalog';

const airportsByIcao = new Map<string, Airport>();
airportsData.forEach((airport) => {
  airportsByIcao.set(airport.icao.toUpperCase(), airport);
});

/**
 * Airport utility functions
 */
export const airports = {
  findWhere(criteria: { icao?: string }): Airport | undefined {
    if (criteria.icao) {
      return airportsByIcao.get(criteria.icao.toUpperCase());
    }
    return undefined;
  },
  toJSON(): Airport[] {
    return airportsData;
  },
  searchByIcao(prefix: string, limit = 10): Airport[] {
    const upperPrefix = prefix.toUpperCase();
    return airportsData
      .filter((apt) => apt.icao.startsWith(upperPrefix))
      .slice(0, limit);
  },
  isValid(icao: string): boolean {
    return airportsByIcao.has(icao.toUpperCase());
  },
};
