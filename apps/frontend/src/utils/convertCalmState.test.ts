import { describe, expect, it } from 'vitest';

import {
  CALM_CONVERT_PRIMARY_LABEL,
  CALM_DOWNLOAD_PRIMARY_LABEL,
  CALM_PROFILE_LABEL_FALLBACK,
  buildCalmExampleChips,
  deriveCalmConvertUi,
  resolveCalmProfileLabel,
} from './convertCalmState';

describe('deriveCalmConvertUi (TC-UX-CALM)', () => {
  it('TC-UX-CALM-004: empty → hero + convert primary', () => {
    const ui = deriveCalmConvertUi({ hasInput: false, hasConverted: false });
    expect(ui.phase).toBe('empty');
    expect(ui.showEmptyHero).toBe(true);
    expect(ui.primaryKind).toBe('convert');
    expect(ui.hideAdvancedSetup).toBe(true);
    expect(ui.showValidityStrip).toBe(false);
  });

  it('TC-UX-CALM-001: editing keeps convert as primary', () => {
    const ui = deriveCalmConvertUi({ hasInput: true, hasConverted: false });
    expect(ui.phase).toBe('editing');
    expect(ui.primaryKind).toBe('convert');
    expect(ui.showEmptyHero).toBe(false);
  });

  it('TC-UX-CALM-002/010: post-success → download primary; no persistent validity strip', () => {
    const ui = deriveCalmConvertUi({
      hasInput: true,
      hasConverted: true,
      latestReadyToDownload: true,
    });
    expect(ui.phase).toBe('postSuccess');
    expect(ui.primaryKind).toBe('download');
    expect(ui.showValidityStrip).toBe(false);
  });

  it('keeps convert primary when converted but not ready to download', () => {
    const ui = deriveCalmConvertUi({
      hasInput: true,
      hasConverted: true,
      latestReadyToDownload: false,
    });
    expect(ui.primaryKind).toBe('convert');
    expect(ui.showValidityStrip).toBe(false);
  });

  it('exports calm labels without internal planning ids', () => {
    expect(CALM_CONVERT_PRIMARY_LABEL).toBe('Convert');
    expect(CALM_DOWNLOAD_PRIMARY_LABEL).toBe('Download latest');
    expect(CALM_CONVERT_PRIMARY_LABEL).not.toMatch(/EV-|UJ-|TC-|Corpus/);
  });

  it('resolveCalmProfileLabel uses option label or fallback', () => {
    expect(
      resolveCalmProfileLabel('US', [{ value: 'US', label: 'United States' }]),
    ).toBe('United States');
    expect(
      resolveCalmProfileLabel('MISSING', [{ value: 'US', label: 'United States' }]),
    ).toBe(CALM_PROFILE_LABEL_FALLBACK);
  });

  it('buildCalmExampleChips skips products with no example', () => {
    expect(
      buildCalmExampleChips(
        [
          { label: 'METAR', product: 'METAR' },
          { label: 'TAF', product: 'TAF' },
        ],
        (product) => (product === 'METAR' ? { id: 'metar-1' } : undefined),
      ),
    ).toEqual([{ id: 'metar-1', label: 'METAR' }]);
  });
});
