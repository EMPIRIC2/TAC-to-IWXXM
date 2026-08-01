/**
 * TC-F7-008 C1 + TC-F25-003 — catalog completeness / WMO-passers only
 * (F7.g / #780 / UJ-032 / UJ-036 / S026 F25 W4).
 */

import { describe, expect, it } from 'vitest';

import {
  EXAMPLE_PRODUCTS,
  EXAMPLES,
  FIXTURE_GAPS,
  WMO_PROVENANCE_NOTE,
  WMO_SCOPE_PRODUCTS,
  getExampleById,
  getTacExamplesForProduct,
  type GoldenExample,
} from './examplesCatalog';

const GAP_PRODUCTS = new Set(FIXTURE_GAPS.map((gap) => gap.product));
const WMO_SCOPE = new Set(WMO_SCOPE_PRODUCTS);

describe('examplesCatalog (TC-F7-008 C1)', () => {
  it('exports seven products and non-empty EXAMPLES', () => {
    expect(EXAMPLE_PRODUCTS).toHaveLength(7);
    expect(EXAMPLES.length).toBeGreaterThan(0);
  });

  it('requires every example to be demo / non-operational with provenance + body', () => {
    for (const example of EXAMPLES) {
      expect(example.nonOperational).toBe(true);
      expect(example.id.trim().length).toBeGreaterThan(0);
      expect(example.label.trim().length).toBeGreaterThan(0);
      expect(example.body.trim().length).toBeGreaterThan(0);
      expect(example.provenance).toMatch(/^packages\/tac2iwxxm\/tests\/fixtures\//);
    }
  });

  it('has unique example ids', () => {
    const ids = EXAMPLES.map((example) => example.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('provides ≥2 TAC examples per product or a documented fixture gap', () => {
    for (const product of EXAMPLE_PRODUCTS) {
      const tacExamples = getTacExamplesForProduct(product);
      if (GAP_PRODUCTS.has(product)) {
        expect(tacExamples.length).toBe(1);
        expect(
          FIXTURE_GAPS.some((gap) => gap.product === product && gap.reason.trim()),
        ).toBe(true);
      } else {
        expect(tacExamples.length).toBeGreaterThanOrEqual(2);
      }
    }
  });

  it('documents WMO single-seed gaps for METAR/SPECI/AIRMET/VAA/TCA', () => {
    expect(FIXTURE_GAPS.map((gap) => gap.product).sort()).toEqual([
      'AIRMET',
      'METAR',
      'SPECI',
      'TCA',
      'VAA',
    ]);
  });

  it('includes ≥1 AHL bulletin example', () => {
    const ahl = EXAMPLES.filter((example) => example.inputMode === 'ahl_bulletin');
    expect(ahl.length).toBeGreaterThanOrEqual(1);
    expect(ahl[0]?.body).toMatch(/^[A-Z]{4}\d{2}\s+/m);
    expect(ahl[0]?.product).toBe('METAR');
  });

  it('includes ≥1 happy-path IWXXM example on collect_iwxxm', () => {
    const iwxxm = EXAMPLES.filter((example) => example.inputMode === 'collect_iwxxm');
    expect(iwxxm.length).toBeGreaterThanOrEqual(1);
    const body = iwxxm[0]?.body ?? '';
    expect(body).toMatch(/<\?xml|iwxxm|METAR/i);
    expect(body.toLowerCase()).not.toMatch(/schematron.?fail|soft.?fail/);
  });

  it('resolves examples by id', () => {
    const sample: GoldenExample | undefined = getExampleById('metar_a3_1');
    expect(sample?.product).toBe('METAR');
    expect(sample?.wmoPass).toBe(true);
    expect(getExampleById('missing-id')).toBeUndefined();
  });

  it('does not include soft-fail or file-queue examples (C5 out of v1)', () => {
    for (const example of EXAMPLES) {
      expect(example.id.toLowerCase()).not.toMatch(
        /soft.?fail|file.?queue|upload.?queue/,
      );
      expect(example.label.toLowerCase()).not.toMatch(/soft.?fail|file.?queue/);
    }
  });
});

describe('examplesCatalog WMO-passers (TC-F25-003)', () => {
  it('requires every WMO-scope TAC demo to be wmoPass or wmoReference with a seed id', () => {
    for (const example of EXAMPLES) {
      if (example.inputMode !== 'tac' || !example.product) continue;
      if (!WMO_SCOPE.has(example.product)) continue;
      const passer = example.wmoPass === true;
      const reference = example.wmoReference === true;
      expect(passer || reference).toBe(true);
      expect(passer && reference).toBe(false);
      expect(example.wmoSeed?.trim().length).toBeGreaterThan(0);
      expect(example.provenance).toMatch(/annex3_golden\//);
    }
  });

  it('lists unlocked WMO seeds for METAR/SPECI/TAF/SIGMET/AIRMET', () => {
    expect(getExampleById('metar_a3_1')?.wmoSeed).toBe('metar-A3-1');
    expect(getExampleById('speci_a3_2')?.wmoSeed).toBe('speci-A3-2');
    expect(getExampleById('taf_a5_1')?.wmoSeed).toBe('taf-A5-1');
    expect(getExampleById('taf_a5_2')?.wmoSeed).toBe('taf-A5-2');
    expect(getExampleById('sigmet_a6_1a_ts')?.wmoSeed).toBe('sigmet-A6-1a-TS');
    expect(getExampleById('sigmet_a6_1b_cnl')?.wmoSeed).toBe('sigmet-A6-1b-CNL');
    expect(getExampleById('airmet_a6_1a_ts')?.wmoSeed).toBe('airmet-A6-1a-TS');
  });

  it('hides non-passing annex3 / iwxxm_us TAC demos for in-scope products', () => {
    for (const id of [
      'metar_basic',
      'metar_cavok',
      'metar_us_auto_ao2',
      'speci_basic',
      'speci_cavok',
      'speci_us_cavok',
      'taf_basic',
      'taf_cavok',
      'sigmet_basic',
      'sigmet_us_basic',
      'airmet_basic',
      'airmet_us_basic',
    ]) {
      expect(getExampleById(id)).toBeUndefined();
    }
  });

  it('retains SIGMET WMO keepers and AIRMET when F24 green', () => {
    expect(getTacExamplesForProduct('SIGMET').length).toBeGreaterThanOrEqual(2);
    expect(getTacExamplesForProduct('AIRMET').some((ex) => ex.wmoPass)).toBe(true);
  });

  it('lists VA SIGMET official stems (EGGX reference; multi-location passer)', () => {
    const eggx = getExampleById('sigmet_va_eggx');
    expect(eggx?.wmoReference).toBe(true);
    expect(eggx?.wmoPass).not.toBe(true);
    expect(eggx?.wmoSeed).toBe('sigmet-VA-EGGX');
    const multi = getExampleById('sigmet_multi_location_va');
    expect(multi?.wmoPass).toBe(true);
    expect(multi?.wmoReference).not.toBe(true);
    expect(multi?.wmoSeed).toBe('sigmet-multi-location-VA');
    expect(multi?.label.toLowerCase()).toMatch(/passer/);
    expect(getTacExamplesForProduct('SIGMET').length).toBeGreaterThanOrEqual(4);
  });

  it('registers every EV-027 inventory happy-path official seed (TC-EV027-002)', () => {
    // Mirrors packages/tac2iwxxm/tests/fixtures/wmo_official_tac_inventory.py registered peers.
    const expected: ReadonlyArray<{ id: string; seed: string }> = [
      { id: 'metar_a3_1', seed: 'metar-A3-1' },
      { id: 'speci_a3_2', seed: 'speci-A3-2' },
      { id: 'taf_a5_1', seed: 'taf-A5-1' },
      { id: 'taf_a5_2', seed: 'taf-A5-2' },
      { id: 'sigmet_a6_1a_ts', seed: 'sigmet-A6-1a-TS' },
      { id: 'sigmet_a6_1b_cnl', seed: 'sigmet-A6-1b-CNL' },
      { id: 'sigmet_va_eggx', seed: 'sigmet-VA-EGGX' },
      { id: 'sigmet_multi_location_va', seed: 'sigmet-multi-location-VA' },
      { id: 'airmet_a6_1a_ts', seed: 'airmet-A6-1a-TS' },
      { id: 'vaa_a7_2', seed: 'va-advisory-A7-2' },
      { id: 'tca_a2_2', seed: 'tc-advisory-A2-2' },
    ];
    for (const { id, seed } of expected) {
      const ex = getExampleById(id);
      expect(ex, `missing catalog id ${id}`).toBeDefined();
      expect(ex?.wmoSeed).toBe(seed);
      expect(ex?.wmoPass === true || ex?.wmoReference === true).toBe(true);
    }
  });

  it('documents vendor mirror provenance policy', () => {
    expect(WMO_PROVENANCE_NOTE).toMatch(/vendor\/schemas\/iwxxm/);
    expect(WMO_PROVENANCE_NOTE.toLowerCase()).toMatch(/mirror/);
  });
});

describe('examplesCatalog US out of WMO menu (TC-EV025-005 / UJ-039 deepen)', () => {
  it('never lists iwxxm_us package goldens in the WMO sample menu', () => {
    for (const example of EXAMPLES) {
      expect(example.provenance).not.toMatch(/iwxxm_us_golden/);
      expect(example.id).not.toMatch(/_us_/);
      expect(example.label.toLowerCase()).not.toMatch(/\biwxxm-us\b|\bus remarks\b/);
    }
    for (const product of WMO_SCOPE_PRODUCTS) {
      for (const example of getTacExamplesForProduct(product)) {
        expect(example.wmoPass === true || example.wmoReference === true).toBe(true);
        expect(example.provenance).toMatch(/annex3_golden\//);
      }
    }
    // Known Lane A / US package stems must remain unregistered.
    for (const id of [
      'metar_us_auto_ao2',
      'metar_us_ao2_slp',
      'metar_us_pk_wnd',
      'speci_us_cavok',
      'speci_us_ao2',
      'speci_us_auto',
      'sigmet_us_basic',
      'airmet_us_basic',
      'taf_us_altimeter',
    ]) {
      expect(getExampleById(id)).toBeUndefined();
    }
  });
});

describe('examplesCatalog VAA/TCA unlock (TC-F26-005 / TC-F27-005 / S02.M2)', () => {
  it('unlocks WMO A7-2 / A2-2 independently with wmoPass + annex3 provenance', () => {
    const vaa = getExampleById('vaa_a7_2');
    expect(vaa?.product).toBe('VAA');
    expect(vaa?.wmoPass).toBe(true);
    expect(vaa?.wmoSeed).toBe('va-advisory-A7-2');
    expect(vaa?.provenance).toMatch(/annex3_golden\/vaa_a7_2\.tac/);

    const tca = getExampleById('tca_a2_2');
    expect(tca?.product).toBe('TCA');
    expect(tca?.wmoPass).toBe(true);
    expect(tca?.wmoSeed).toBe('tc-advisory-A2-2');
    expect(tca?.provenance).toMatch(/annex3_golden\/tca_a2_2\.tac/);
  });

  it('hides product_matrix vaa_basic / tca_basic once WMO passers replace them', () => {
    expect(getExampleById('vaa_basic')).toBeUndefined();
    expect(getExampleById('tca_basic')).toBeUndefined();
  });

  it('treats VAA and TCA as WMO-scope products with independent single-seed gaps', () => {
    expect(WMO_SCOPE_PRODUCTS).toContain('VAA');
    expect(WMO_SCOPE_PRODUCTS).toContain('TCA');
    expect(getTacExamplesForProduct('VAA').every((ex) => ex.wmoPass)).toBe(true);
    expect(getTacExamplesForProduct('TCA').every((ex) => ex.wmoPass)).toBe(true);
    expect(getTacExamplesForProduct('VAA')).toHaveLength(1);
    expect(getTacExamplesForProduct('TCA')).toHaveLength(1);
  });
});
