/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * FileConverterSecondaryActions: Disseminate button when destinations UI is enabled.
 * FR-052..056 / DI-008: destinations are off by default; tests flip the flag and restore it.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { FileConverterSecondaryActions } from './FileConverterSecondaryActions';
import { operatorDisseminationUiConfig } from '@/utils/operatorDisseminationUi';

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

/**
 *
 */
function buildProps(overrides: Record<string, unknown> = {}) {
  return {
    calmUi: { primaryKind: 'convert' },
    conversionParams: { product: 'METAR', exchangeProfile: 'GLOBAL_AFS' },
    convertDisabled: false,
    convertedFiles: [],
    handleClear: vi.fn(),
    handleConvertAndSend: vi.fn(),
    handleDisseminationOpenChange: vi.fn(),
    handleDownloadAll: vi.fn(),
    hasConverted: false,
    inputMode: 'single',
    isBusy: false,
    isConvertAndSending: false,
    isReadOnly: false,
    lintHighlightPreset: 'default',
    setLintHighlightPreset: vi.fn(),
    setPackagingExchangeProfile: vi.fn(),
    ...overrides,
  };
}

describe('FileConverterSecondaryActions', () => {
  const originalEnabled = operatorDisseminationUiConfig.destinationsEnabled;

  beforeEach(() => {
    operatorDisseminationUiConfig.destinationsEnabled = true;
  });

  afterEach(() => {
    operatorDisseminationUiConfig.destinationsEnabled = originalEnabled;
    cleanup();
  });

  it('opens the dissemination drawer with the current exchange profile', () => {
    const props = buildProps();
    render(<FileConverterSecondaryActions {...(props as any)} />);
    fireEvent.click(screen.getByTestId('open-dissemination-drawer'));
    expect(props.setPackagingExchangeProfile).toHaveBeenCalledWith('GLOBAL_AFS');
    expect(props.handleDisseminationOpenChange).toHaveBeenCalledWith(true);
  });

  it('hides Disseminate when destinations are disabled (default)', () => {
    operatorDisseminationUiConfig.destinationsEnabled = false;
    render(<FileConverterSecondaryActions {...(buildProps() as any)} />);
    expect(screen.queryByTestId('open-dissemination-drawer')).not.toBeInTheDocument();
  });
});
