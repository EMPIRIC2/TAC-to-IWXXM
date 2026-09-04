import { describe, expect, it } from 'vitest';
import {
  CA_ECCC_NATIONAL_EXTENSION,
  CA_ECCC_SUPPORTED_PRODUCTS,
  exchangeOutputForProfile,
  nationalExtensionsForProfile,
} from '@/utils/profileWire';

describe('profileWire', () => {
  it('auto-wires IWXXM_CA only for CA_ECCC', () => {
    expect(nationalExtensionsForProfile('CA_ECCC')).toEqual([
      CA_ECCC_NATIONAL_EXTENSION,
    ]);
    expect(nationalExtensionsForProfile('ca_eccc')).toEqual([
      CA_ECCC_NATIONAL_EXTENSION,
    ]);
    expect(nationalExtensionsForProfile('ICAO_2025')).toEqual([]);
    expect(nationalExtensionsForProfile('annex3')).toEqual([]);
    expect(nationalExtensionsForProfile('iwxxm_us')).toEqual([]);
  });

  it('requests exchange output only for CA_ECCC', () => {
    expect(exchangeOutputForProfile('CA_ECCC')).toBe(true);
    expect(exchangeOutputForProfile('ICAO_2025')).toBe(false);
    expect(exchangeOutputForProfile('annex3')).toBe(false);
  });

  it('lists supported aerodrome products', () => {
    expect(CA_ECCC_SUPPORTED_PRODUCTS).toEqual(['METAR', 'SPECI', 'TAF', 'AIRMET']);
  });
});
