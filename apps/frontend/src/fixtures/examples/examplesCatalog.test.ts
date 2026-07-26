/**
 * TC-F7-008 C1 — catalog completeness (F7.g / #780 / UJ-032).
 */

import { describe, expect, it } from 'vitest';

import {
  EXAMPLE_PRODUCTS,
  EXAMPLES,
  FIXTURE_GAPS,
  getExampleById,
  getTacExamplesForProduct,
  type GoldenExample,
} from './examplesCatalog';

const GAP_PRODUCTS = new Set(FIXTURE_GAPS.map((gap) => gap.product));

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

  it('documents only VAA and TCA as 1-fixture gaps', () => {
    expect(FIXTURE_GAPS.map((gap) => gap.product).sort()).toEqual(['TCA', 'VAA']);
  });

  it('includes ≥1 AHL bulletin example', () => {
    const ahl = EXAMPLES.filter((example) => example.inputMode === 'ahl_bulletin');
    expect(ahl.length).toBeGreaterThanOrEqual(1);
    expect(ahl[0]?.body).toMatch(/^[A-Z]{4}\d{2}\s+/m);
  });

  it('includes ≥1 happy-path IWXXM example on collect_iwxxm', () => {
    const iwxxm = EXAMPLES.filter((example) => example.inputMode === 'collect_iwxxm');
    expect(iwxxm.length).toBeGreaterThanOrEqual(1);
    const body = iwxxm[0]?.body ?? '';
    expect(body).toMatch(/<\?xml|iwxxm|METAR/i);
    expect(body.toLowerCase()).not.toMatch(/schematron.?fail|soft.?fail/);
  });

  it('includes at least one iwxxm_us METAR and SPECI TAC example', () => {
    const usMetar = EXAMPLES.find(
      (example) =>
        example.product === 'METAR' &&
        example.inputMode === 'tac' &&
        example.provenance.includes('iwxxm_us'),
    );
    const usSpeci = EXAMPLES.find(
      (example) =>
        example.product === 'SPECI' &&
        example.inputMode === 'tac' &&
        example.provenance.includes('iwxxm_us'),
    );
    expect(usMetar).toBeDefined();
    expect(usSpeci).toBeDefined();
  });

  it('resolves examples by id', () => {
    const sample: GoldenExample | undefined = getExampleById('metar_basic');
    expect(sample?.product).toBe('METAR');
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
