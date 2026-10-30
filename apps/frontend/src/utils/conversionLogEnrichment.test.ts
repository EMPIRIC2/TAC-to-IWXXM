import { describe, it, expect } from 'vitest';
import type { LintIssueCatalogEntry } from '@/utils/api';
import {
  catalogTemplateToLogHint,
  productLabelFromIssueMessage,
  resolveConversionLogHint,
} from './conversionLogEnrichment';

const RVR_CATALOG: LintIssueCatalogEntry = {
  code: 'RVR_PRESENT',
  severity: 'info',
  message_template:
    '{product} includes one or more runway visual range (RVR) groups. ' +
    'Informational: noted for operator awareness; does not by itself block conversion. ' +
    'Source: ICAO Annex 3 Table A3-2 / App 3. Full normative text may require purchase.',
  product: null,
  tags: ['rvr', 'metar'],
  family: 'lint',
};

const NSW_CATALOG: LintIssueCatalogEntry = {
  code: 'NSW_PRESENT',
  severity: 'info',
  message_template:
    '{product} includes NSW (nil significant weather). ' +
    'Informational: noted for operator awareness; does not by itself block conversion. ' +
    'Source: ICAO Annex 3 App 5 / Table A5-1. Full normative text may require purchase.',
  product: null,
  tags: ['weather', 'metar'],
  family: 'lint',
};

describe('conversionLogEnrichment', () => {
  it('guesses product labels from issue titles', () => {
    expect(productLabelFromIssueMessage("METAR RVR group 'R12/1000U' present")).toBe(
      'METAR',
    );
    expect(productLabelFromIssueMessage('SPECI NSW present')).toBe('SPECI');
    expect(productLabelFromIssueMessage('untitled')).toBe('This report');
  });

  it('cleans catalog templates into log hints with product fill and no source tail', () => {
    const hint = catalogTemplateToLogHint(RVR_CATALOG.message_template, 'METAR');
    expect(hint).toMatch(
      /METAR includes one or more runway visual range \(RVR\) groups/i,
    );
    expect(hint).toMatch(/does not by itself block conversion/i);
    expect(hint).not.toMatch(/Source:/i);
    expect(hint).not.toMatch(/paywall|purchase/i);
    expect(hint).not.toMatch(/\{product\}/i);
  });

  it('prefers an explicit issue hint (UNKNOWN_ICAO pattern)', () => {
    expect(
      resolveConversionLogHint(
        {
          code: 'UNKNOWN_ICAO',
          message: 'Station YUDO is not in the aerodrome registry',
          hint: "Designator 'YUDO' was not found in the local airport catalog; conversion continues, but coordinates and airport name may be incomplete",
        },
        null,
      ),
    ).toMatch(/Designator 'YUDO'/);
  });

  it('derives RVR_PRESENT and NSW_PRESENT hints from catalog when hint is missing', () => {
    const rvr = resolveConversionLogHint(
      {
        code: 'RVR_PRESENT',
        message: "METAR RVR group 'R12/1000U' present",
      },
      RVR_CATALOG,
    );
    expect(rvr).toMatch(/runway visual range \(RVR\)/i);
    expect(rvr).toMatch(/does not by itself block conversion/i);

    const nsw = resolveConversionLogHint(
      {
        code: 'NSW_PRESENT',
        message: 'METAR NSW present',
      },
      NSW_CATALOG,
    );
    expect(nsw).toMatch(/NSW \(nil significant weather\)/i);
    expect(nsw).toMatch(/does not by itself block conversion/i);
  });

  it('falls back to plain-language glosses when catalog is missing', () => {
    expect(
      resolveConversionLogHint({
        code: 'RVR_PRESENT',
        message: "METAR RVR group 'R12/1000U' present",
      }),
    ).toMatch(/Runway Visual Range/i);
    expect(
      resolveConversionLogHint({
        code: 'NSW_PRESENT',
        message: 'METAR NSW present',
      }),
    ).toMatch(/No Significant Weather/i);
  });

  it('scrubs planning ids from derived and explicit hints', () => {
    expect(
      resolveConversionLogHint({
        code: 'X',
        hint: 'Fix the group — see EV-048 / ADR-022',
      }),
    ).not.toMatch(/EV-048|ADR-022/);
  });

  it('returns null for sparse uncatalogued codes without a fallback', () => {
    expect(
      resolveConversionLogHint({
        code: 'REMARKS_EXCLUDED',
        message: 'METAR remarks excluded from IWXXM',
      }),
    ).toBeNull();
  });
});
