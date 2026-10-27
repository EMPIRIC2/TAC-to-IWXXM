import { describe, expect, it } from 'vitest';

import {
  CALM_CONVERT_PRIMARY_LABEL,
  CALM_DOWNLOAD_PRIMARY_LABEL,
  deriveCalmConvertUi,
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

  it('TC-UX-CALM-002/010: post-success → download primary + validity strip', () => {
    const ui = deriveCalmConvertUi({
      hasInput: true,
      hasConverted: true,
      latestReadyToDownload: true,
    });
    expect(ui.phase).toBe('postSuccess');
    expect(ui.primaryKind).toBe('download');
    expect(ui.showValidityStrip).toBe(true);
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
    expect(CALM_CONVERT_PRIMARY_LABEL).toBe('Convert & validate');
    expect(CALM_DOWNLOAD_PRIMARY_LABEL).toBe('Download IWXXM');
    expect(CALM_CONVERT_PRIMARY_LABEL).not.toMatch(/EV-|UJ-|TC-|Corpus/);
  });
});
