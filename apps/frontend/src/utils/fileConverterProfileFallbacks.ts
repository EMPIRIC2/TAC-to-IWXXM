/** Fallback ConversionProfile catalog entries for FileConverter. */
import type { ProfileCatalogEntry } from '@/utils/conversionProfilesApi';
import {
  CA_ECCC_EXTENSION_LABEL,
  CA_ECCC_SUPPORTED_PRODUCTS,
} from '@/utils/profileWire';
import type { IwxxmProfile } from '@/utils/tacProduct';

/**
 * FALLBACK_PROFILE_SUMMARIES.
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
  US_FAA_NWS: {
    id: 'US_FAA_NWS',
    kind: 'semantic',
    products: ['METAR', 'SPECI', 'TAF', 'SIGMET', 'AIRMET', 'TCA', 'SWXA', 'VONA'],
    deltas_vs_icao: [
      'Adds FAA/NWS national differences on top of the ICAO baseline.',
      'Uses the iwxxm-us schema catalog for United States IWXXM extensions.',
    ],
  },
  CA_ECCC: {
    id: 'CA_ECCC',
    kind: 'semantic',
    products: [...CA_ECCC_SUPPORTED_PRODUCTS],
    deltas_vs_icao: [CA_ECCC_EXTENSION_LABEL],
    metar_family_variants: [
      {
        tac_lead: 'METAR',
        api_product: 'METAR',
        iwxxm_root: 'iwxxm:METAR',
        rule_id_prefix: 'CA.METAR',
      },
      {
        tac_lead: 'SPECI',
        api_product: 'SPECI',
        iwxxm_root: 'iwxxm:SPECI',
        rule_id_prefix: 'CA.SPECI',
      },
      {
        tac_lead: 'LWIS',
        api_product: 'METAR',
        iwxxm_root: 'iwxxm-ca:LWIS',
        rule_id: 'CA.METAR.LWIS',
        minimal_observation: true,
        notes: 'Limited Weather Information System',
      },
      {
        tac_lead: 'SAWR',
        api_product: 'METAR',
        iwxxm_root: 'iwxxm-ca:SAWR',
        rule_id: 'CA.METAR.SAWR',
        notes: 'Surface Aviation Weather Report',
      },
    ],
  },
  US_NWS_CONVECTIVE_SIGMET: {
    id: 'US_NWS_CONVECTIVE_SIGMET',
    kind: 'semantic',
    products: ['SIGMET'],
    deltas_vs_icao: [
      'United States convective SIGMET. Use this for convective SIGMET text, not an international SIGMET.',
    ],
  },
  US_NWS_G_AIRMET: {
    id: 'US_NWS_G_AIRMET',
    kind: 'semantic',
    products: ['AIRMET'],
    deltas_vs_icao: [
      'United States G-AIRMET. Conversion is unavailable until a text bulletin is on file.',
    ],
  },
  US_NWS_VONA: {
    id: 'US_NWS_VONA',
    kind: 'semantic',
    products: ['VONA'],
    deltas_vs_icao: [
      'United States volcano observatory notice. Conversion is unavailable until a complete notice is on file.',
    ],
  },
  CA_MSC_SIGMET: {
    id: 'CA_MSC_SIGMET',
    kind: 'semantic',
    products: ['SIGMET'],
    deltas_vs_icao: [
      'Canadian SIGMET published as IWXXM. This checks the published file. Text conversion is unavailable.',
    ],
  },
};

/**
 * Function `fallbackProfileSummary`.
 */
