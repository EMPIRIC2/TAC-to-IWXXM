/** Fallback ConversionProfile catalog entries for FileConverter. */
import type { ProfileCatalogEntry } from '@/utils/conversionProfilesApi';
import type { IwxxmProfile } from '@/utils/tacProduct';

/**
 * FALLBACK_PROFILE_SUMMARIES — ICAO baseline only (FR-019..022 / M1).
 */
export const FALLBACK_PROFILE_SUMMARIES: Partial<
  Record<IwxxmProfile, ProfileCatalogEntry>
> = {
  ICAO_2025: {
    id: 'ICAO_2025',
    kind: 'semantic',
    products: [
      'METAR',
      'SPECI',
      'TAF',
      'SIGMET',
      'AIRMET',
      'VAA',
      'TCA',
      'SWXA',
      'VONA',
    ],
    deltas_vs_icao: ['Baseline ICAO/WMO line used for cross-profile comparison.'],
  },
};
