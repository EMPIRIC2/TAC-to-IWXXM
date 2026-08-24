import { describe, expect, it } from 'vitest';
import {
  CA_ECCC_NATIONAL_EXTENSION,
  CA_ECCC_SUPPORTED_PRODUCTS,
  exchangeOutputForProfile,
  nationalExtensionsForProfile,
} from '@/utils/profileWire';

describe('profileWire', () => {
  it('auto-wires IWXXM_CA only for ca_eccc', () => {
    expect(nationalExtensionsForProfile('ca_eccc')).toEqual([
      CA_ECCC_NATIONAL_EXTENSION,
    ]);
    expect(nationalExtensionsForProfile('annex3')).toEqual([]);
    expect(nationalExtensionsForProfile('iwxxm_us')).toEqual([]);
  });

  it('requests exchange output only for ca_eccc', () => {
    expect(exchangeOutputForProfile('ca_eccc')).toBe(true);
    expect(exchangeOutputForProfile('annex3')).toBe(false);
  });

  it('lists supported aerodrome products', () => {
    expect(CA_ECCC_SUPPORTED_PRODUCTS).toEqual(['METAR', 'SPECI', 'TAF', 'AIRMET']);
  });
});
