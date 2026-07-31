/**
 * Frontend-only golden examples catalog (F7.g / #780 / F25 W4 / F26–F27 / ADR-032).
 *
 * Bodies are copied from package fixtures — never import Python at runtime.
 * In-scope TAC demos are **WMO passers** (`wmoPass`) and/or **WMO reference** samples
 * (`wmoReference`) per ADR-032 amend / UJ-039 (EV-024). Translation-failed and US
 * demos stay out of the WMO happy-path list.
 */

import type { OperatorInputMode } from '@/utils/inputKind';
import type { TacProduct } from '@/utils/tacProduct';

import airmetA61aTs from './bodies/airmet_a6_1a_ts.tac?raw';
import metarA31 from './bodies/metar_a3_1.tac?raw';
import metarBasicGolden from './bodies/metar_basic.golden.xml?raw';
import metarMultiAhl from './bodies/metar_multi_ahl.txt?raw';
import sigmetA61aTs from './bodies/sigmet_a6_1a_ts.tac?raw';
import sigmetA61bCnl from './bodies/sigmet_a6_1b_cnl.tac?raw';
import sigmetMultiLocationVa from './bodies/sigmet_multi_location_va.tac?raw';
import sigmetVaEggx from './bodies/sigmet_va_eggx.tac?raw';
import speciA32 from './bodies/speci_a3_2.tac?raw';
import tafA51 from './bodies/taf_a5_1.tac?raw';
import tafA52 from './bodies/taf_a5_2.tac?raw';
import tcaA22 from './bodies/tca_a2_2.tac?raw';
import vaaA72 from './bodies/vaa_a7_2.tac?raw';

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

/** Products gated to strict WMO default golden parity (F24/F25/F26/F27). */
export const WMO_SCOPE_PRODUCTS: readonly TacProduct[] = [
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
  /** Package-relative provenance path (mirrored vendor / annex3 golden) */
  provenance: string;
  /**
   * True when this TAC demo passes ADR-032 WMO default golden bar (or SIGMET keeper).
   * Strict passers for WMO_SCOPE_PRODUCTS (TC-F25-003 / TC-F26-005 / TC-F27-005).
   */
  wmoPass?: boolean;
  /**
   * Official WMO example loadable from the sample menu before convert equality
   * (ADR-032 amend / UJ-039). Mutually exclusive with ``wmoPass`` for UI tier copy.
   */
  wmoReference?: boolean;
  /** Vendor / annex3 seed id when ``wmoPass`` or ``wmoReference`` (e.g. ``metar-A3-1``). */
  wmoSeed?: string;
}

/**
 * Documented 1-fixture gap (E16-8 / E16-13 / F25–F27 WMO-only).
 */
export interface FixtureGap {
  product: TacProduct;
  reason: string;
}

const PKG = 'packages/tac2iwxxm/tests/fixtures';
const VENDOR =
  'vendor/schemas/iwxxm/2025-2/IWXXM/examples (mirrored under annex3_golden)';

/**
 * Curated demo examples for convert + validate workbench.
 *
 * WMO-scope TAC rows: strict passers and official WMO reference samples (EV-024).
 * AHL / IWXXM modes remain non-WMO-scope demos.
 */
export const EXAMPLES: readonly GoldenExample[] = [
  {
    id: 'metar_a3_1',
    label: 'METAR WMO A3-1 (annex3)',
    product: 'METAR',
    inputMode: 'tac',
    body: metarA31,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/metar_a3_1.tac`,
    wmoPass: true,
    wmoSeed: 'metar-A3-1',
  },
  {
    id: 'speci_a3_2',
    label: 'SPECI WMO A3-2 (annex3)',
    product: 'SPECI',
    inputMode: 'tac',
    body: speciA32,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/speci_a3_2.tac`,
    wmoPass: true,
    wmoSeed: 'speci-A3-2',
  },
  {
    id: 'taf_a5_1',
    label: 'TAF WMO A5-1 (annex3)',
    product: 'TAF',
    inputMode: 'tac',
    body: tafA51,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/taf_a5_1.tac`,
    wmoPass: true,
    wmoSeed: 'taf-A5-1',
  },
  {
    id: 'taf_a5_2',
    label: 'TAF WMO A5-2 AMD/CNL (annex3)',
    product: 'TAF',
    inputMode: 'tac',
    body: tafA52,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/taf_a5_2.tac`,
    wmoPass: true,
    wmoSeed: 'taf-A5-2',
  },
  {
    id: 'sigmet_a6_1a_ts',
    label: 'SIGMET WMO A6-1a-TS (annex3)',
    product: 'SIGMET',
    inputMode: 'tac',
    body: sigmetA61aTs,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/sigmet_a6_1a_ts.tac`,
    wmoPass: true,
    wmoSeed: 'sigmet-A6-1a-TS',
  },
  {
    id: 'sigmet_a6_1b_cnl',
    label: 'SIGMET WMO A6-1b-CNL (annex3)',
    product: 'SIGMET',
    inputMode: 'tac',
    body: sigmetA61bCnl,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/sigmet_a6_1b_cnl.tac`,
    wmoPass: true,
    wmoSeed: 'sigmet-A6-1b-CNL',
  },
  {
    id: 'sigmet_va_eggx',
    label: 'VA SIGMET WMO EGGX (reference)',
    product: 'SIGMET',
    inputMode: 'tac',
    body: sigmetVaEggx,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/sigmet_va_eggx.tac`,
    wmoReference: true,
    wmoSeed: 'sigmet-VA-EGGX',
  },
  {
    id: 'sigmet_multi_location_va',
    label: 'VA SIGMET WMO multi-location (passer)',
    product: 'SIGMET',
    inputMode: 'tac',
    body: sigmetMultiLocationVa,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/sigmet_multi_location_va.tac`,
    wmoPass: true,
    wmoSeed: 'sigmet-multi-location-VA',
  },
  {
    id: 'airmet_a6_1a_ts',
    label: 'AIRMET WMO A6-1a-TS (annex3)',
    product: 'AIRMET',
    inputMode: 'tac',
    body: airmetA61aTs,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/airmet_a6_1a_ts.tac`,
    wmoPass: true,
    wmoSeed: 'airmet-A6-1a-TS',
  },
  {
    id: 'vaa_a7_2',
    label: 'VAA WMO A7-2 (annex3)',
    product: 'VAA',
    inputMode: 'tac',
    body: vaaA72,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/vaa_a7_2.tac`,
    wmoPass: true,
    wmoSeed: 'va-advisory-A7-2',
  },
  {
    id: 'tca_a2_2',
    label: 'TCA WMO A2-2 (annex3)',
    product: 'TCA',
    inputMode: 'tac',
    body: tcaA22,
    nonOperational: true,
    provenance: `${PKG}/annex3_golden/tca_a2_2.tac`,
    wmoPass: true,
    wmoSeed: 'tc-advisory-A2-2',
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
    product: 'METAR',
    reason:
      'WMO-only catalog (F25): single unlocked seed metar-A3-1; second WMO METAR deferred.',
  },
  {
    product: 'SPECI',
    reason:
      'WMO-only catalog (F25): single unlocked seed speci-A3-2; second WMO SPECI deferred.',
  },
  {
    product: 'AIRMET',
    reason:
      'WMO-only catalog (F24): single unlocked seed airmet-A6-1a-TS; CNL peer deferred.',
  },
  {
    product: 'VAA',
    reason:
      'WMO-only catalog (F26): single unlocked seed va-advisory-A7-2; second WMO VAA deferred.',
  },
  {
    product: 'TCA',
    reason:
      'WMO-only catalog (F27): single unlocked seed tc-advisory-A2-2; second WMO TCA deferred.',
  },
] as const;

/** Provenance note for operators (vendor mirror policy). */
export const WMO_PROVENANCE_NOTE = VENDOR;

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
