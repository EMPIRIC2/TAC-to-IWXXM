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

  it('documents WMO single-seed gaps plus VAA/TCA', () => {
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
  it('requires every WMO-scope TAC demo to be wmoPass with a seed id', () => {
    for (const example of EXAMPLES) {
      if (example.inputMode !== 'tac' || !example.product) continue;
      if (!WMO_SCOPE.has(example.product)) continue;
      expect(example.wmoPass).toBe(true);
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

  it('documents vendor mirror provenance policy', () => {
    expect(WMO_PROVENANCE_NOTE).toMatch(/vendor\/schemas\/iwxxm/);
    expect(WMO_PROVENANCE_NOTE.toLowerCase()).toMatch(/mirror/);
  });
});
