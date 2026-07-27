/**
 * Frontend-only golden examples catalog (F7.g / #780).
 *
 * Bodies are copied from package fixtures — never import Python at runtime.
 */

import type { OperatorInputMode } from '@/utils/inputKind';
import type { TacProduct } from '@/utils/tacProduct';

import airmetBasic from './bodies/airmet_basic.tac?raw';
import airmetUsBasic from './bodies/airmet_us_basic.tac?raw';
import metarBasicGolden from './bodies/metar_basic.golden.xml?raw';
import metarBasic from './bodies/metar_basic.tac?raw';
import metarCavok from './bodies/metar_cavok.tac?raw';
import metarMultiAhl from './bodies/metar_multi_ahl.txt?raw';
import metarUsAutoAo2 from './bodies/metar_us_auto_ao2.tac?raw';
import sigmetBasic from './bodies/sigmet_basic.tac?raw';
import sigmetUsBasic from './bodies/sigmet_us_basic.tac?raw';
import speciBasic from './bodies/speci_basic.tac?raw';
import speciCavok from './bodies/speci_cavok.tac?raw';
import speciUsCavok from './bodies/speci_us_cavok.tac?raw';
import tafBasic from './bodies/taf_basic.tac?raw';
import tafCavok from './bodies/taf_cavok.tac?raw';
import tcaBasic from './bodies/tca_basic.tac?raw';
import vaaBasic from './bodies/vaa_basic.tac?raw';

/** Seven F6 products covered by the Examples catalog. */
export const EXAMPLE_PRODUCTS: readonly TacProduct[] = [
  'METAR',
  'SPECI',
  'TAF',
  'SIGMET',
  'AIRMET',
  'VAA',
  'TCA',
] as const;

/**
 * One loadable workbench example.
 */
export interface GoldenExample {
  /** Stable id for Vitest / Select value */
  id: string;
  /** Operator-visible label */
  label: string;
  /** Product for convert params; set for TAC/AHL/IWXXM when known (else load → `auto`) */
  product?: TacProduct;
  /** ADR-024 input mode to apply on load */
  inputMode: OperatorInputMode;
  /** Editor body */
  body: string;
  /** Always true — demo / non-operational */
  nonOperational: true;
  /** Package-relative provenance path */
  provenance: string;
}

/**
 * Documented 1-fixture gap (E16-8 / E16-13).
 */
export interface FixtureGap {
  product: TacProduct;
  reason: string;
}

const PKG = 'packages/tac2iwxxm/tests/fixtures';

/**
 * Curated demo examples for convert + validate workbench.
 */
export const EXAMPLES: readonly GoldenExample[] = [
  {
    id: 'metar_basic',
    label: 'METAR basic (annex3)',
    product: 'METAR',
    inputMode: 'tac',
    body: metarBasic,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/metar_basic.tac`,
  },
  {
    id: 'metar_cavok',
    label: 'METAR CAVOK (annex3)',
    product: 'METAR',
    inputMode: 'tac',
    body: metarCavok,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/metar_cavok.tac`,
  },
  {
    id: 'metar_us_auto_ao2',
    label: 'METAR AUTO AO2 (iwxxm_us)',
    product: 'METAR',
    inputMode: 'tac',
    body: metarUsAutoAo2,
    nonOperational: true,
    provenance: `${PKG}/iwxxm_us_golden/metar_us_auto_ao2.tac`,
  },
  {
    id: 'speci_basic',
    label: 'SPECI basic (annex3)',
    product: 'SPECI',
    inputMode: 'tac',
    body: speciBasic,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/speci_basic.tac`,
  },
  {
    id: 'speci_cavok',
    label: 'SPECI CAVOK (annex3)',
    product: 'SPECI',
    inputMode: 'tac',
    body: speciCavok,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/speci_cavok.tac`,
  },
  {
    id: 'speci_us_cavok',
    label: 'SPECI CAVOK (iwxxm_us)',
    product: 'SPECI',
    inputMode: 'tac',
    body: speciUsCavok,
    nonOperational: true,
    provenance: `${PKG}/iwxxm_us_golden/speci_us_cavok.tac`,
  },
  {
    id: 'taf_basic',
    label: 'TAF basic (annex3)',
    product: 'TAF',
    inputMode: 'tac',
    body: tafBasic,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/taf_basic.tac`,
  },
  {
    id: 'taf_cavok',
    label: 'TAF CAVOK (annex3)',
    product: 'TAF',
    inputMode: 'tac',
    body: tafCavok,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/taf_cavok.tac`,
  },
  {
    id: 'sigmet_basic',
    label: 'SIGMET basic (product_matrix)',
    product: 'SIGMET',
    inputMode: 'tac',
    body: sigmetBasic,
    nonOperational: true,
    provenance: `${PKG}/product_matrix/sigmet_basic.tac`,
  },
  {
    id: 'sigmet_us_basic',
    label: 'SIGMET basic (iwxxm_us)',
    product: 'SIGMET',
    inputMode: 'tac',
    body: sigmetUsBasic,
    nonOperational: true,
    provenance: `${PKG}/iwxxm_us_golden/sigmet_us_basic.tac`,
  },
  {
    id: 'airmet_basic',
    label: 'AIRMET basic (product_matrix)',
    product: 'AIRMET',
    inputMode: 'tac',
    body: airmetBasic,
    nonOperational: true,
    provenance: `${PKG}/product_matrix/airmet_basic.tac`,
  },
  {
    id: 'airmet_us_basic',
    label: 'AIRMET basic (iwxxm_us)',
    product: 'AIRMET',
    inputMode: 'tac',
    body: airmetUsBasic,
    nonOperational: true,
    provenance: `${PKG}/iwxxm_us_golden/airmet_us_basic.tac`,
  },
  {
    id: 'vaa_basic',
    label: 'VAA basic (product_matrix)',
    product: 'VAA',
    inputMode: 'tac',
    body: vaaBasic,
    nonOperational: true,
    provenance: `${PKG}/product_matrix/vaa_basic.tac`,
  },
  {
    id: 'tca_basic',
    label: 'TCA basic (product_matrix)',
    product: 'TCA',
    inputMode: 'tac',
    body: tcaBasic,
    nonOperational: true,
    provenance: `${PKG}/product_matrix/tca_basic.tac`,
  },
  {
    id: 'ahl_metar_multi',
    label: 'AHL METAR multi-report bulletin',
    product: 'METAR',
    inputMode: 'ahl_bulletin',
    body: metarMultiAhl,
    nonOperational: true,
    provenance: `${PKG}/metar_multi_ahl.txt`,
  },
  {
    id: 'iwxxm_metar_basic',
    label: 'IWXXM METAR basic (happy-path XML)',
    product: 'METAR',
    inputMode: 'collect_iwxxm',
    body: metarBasicGolden,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/metar_basic.golden.xml`,
  },
] as const;

/**
 * Products that ship with a single in-repo TAC golden (do not invent TAC).
 */
export const FIXTURE_GAPS: readonly FixtureGap[] = [
  {
    product: 'VAA',
    reason:
      'Only product_matrix/vaa_basic.tac exists in-repo; second golden deferred (E16-8).',
  },
  {
    product: 'TCA',
    reason:
      'Only product_matrix/tca_basic.tac exists in-repo; second golden deferred (E16-8).',
  },
] as const;

/**
 * Look up an example by id.
 *
 * @param id - Catalog id
 * @returns Example or undefined
 */
export function getExampleById(id: string): GoldenExample | undefined {
  return EXAMPLES.find((example) => example.id === id);
}

/**
 * TAC examples for a product (excludes AHL / IWXXM-only rows unless product matches).
 *
 * @param product - F6 product
 * @returns Matching TAC-mode examples
 */
export function getTacExamplesForProduct(
  product: TacProduct,
): readonly GoldenExample[] {
  return EXAMPLES.filter(
    (example) => example.inputMode === 'tac' && example.product === product,
  );
}
