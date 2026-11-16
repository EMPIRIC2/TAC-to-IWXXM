/**
 * Curated airport ICAO catalog for METAR lookup (data only).
 */
import type { Airport } from '@/models/airport';
import { airportsDataPart1 } from './airportsCatalog.part1';
import { airportsDataPart2 } from './airportsCatalog.part2';
import { airportsDataPart3 } from './airportsCatalog.part3';

export const airportsData: Airport[] = [
  ...airportsDataPart1,
  ...airportsDataPart2,
  ...airportsDataPart3,
];
