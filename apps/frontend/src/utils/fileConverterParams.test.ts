/** Tests for activeMetarFamilyVariants (profile-scoped METAR-family roots). */

import { describe, expect, it } from 'vitest';
import type { ProfileCatalogEntry } from '@/utils/conversionProfilesApi';
import {
  activeMetarFamilyVariants,
  initialConversionParams,
  snapshotExportContext,
} from './fileConverterParams';

describe('snapshotExportContext', () => {
  it('prefers an explicit report variant, then params, and omits blanks', () => {
    const params = { ...initialConversionParams(), reportVariant: ' LWIS ' };
    expect(snapshotExportContext(params, 'METAR', ' SAWR ').reportVariant).toBe('SAWR');
    expect(snapshotExportContext(params, 'METAR').reportVariant).toBe('LWIS');
    expect(snapshotExportContext(params, 'METAR', '  ')).not.toHaveProperty(
      'reportVariant',
    );
  });
});

const variants = [
  { tac_lead: 'METAR', api_product: 'METAR', iwxxm_root: 'iwxxm:METAR' },
  { tac_lead: 'SPECI', api_product: 'SPECI', iwxxm_root: 'iwxxm:SPECI' },
  { tac_lead: 'LWIS', api_product: ' metar ', iwxxm_root: 'iwxxm-ca:LWIS' },
];

describe('activeMetarFamilyVariants', () => {
  it('returns [] when the entry has no variants', () => {
    const base = {
      id: 'ICAO_2025',
      kind: 'semantic',
      products: [],
      deltas_vs_icao: [],
    } as ProfileCatalogEntry;
    expect(activeMetarFamilyVariants(base, 'METAR')).toEqual([]);
    expect(
      activeMetarFamilyVariants({ ...base, metar_family_variants: [] }, 'METAR'),
    ).toEqual([]);
  });

  it('filters variants by trimmed, case-insensitive api_product', () => {
    const entry = {
      id: 'ICAO_2025',
      kind: 'semantic',
      products: [],
      deltas_vs_icao: [],
      metar_family_variants: variants,
    } as ProfileCatalogEntry;
    expect(activeMetarFamilyVariants(entry, ' metar ').map((v) => v.tac_lead)).toEqual([
      'METAR',
      'LWIS',
    ]);
    expect(activeMetarFamilyVariants(entry, 'SPECI').map((v) => v.tac_lead)).toEqual([
      'SPECI',
    ]);
  });
});
