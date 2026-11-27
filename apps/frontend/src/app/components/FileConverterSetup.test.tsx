/* eslint-disable @typescript-eslint/no-explicit-any */
/**
 * Focused tests for FileConverterSetup handlers that are hard to reach through the
 * full workbench after M1 (ICAO-only ship list): library reset confirm, report
 * variant, and the hidden country preset select.
 */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { FileConverterSetup } from './FileConverterSetup';
import { initialConversionParams } from '@/utils/fileConverterParams';
import { libraryResetForProfile } from '@/utils/profileLibraryReset';

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

type LibraryBarProps = {
  onChange: (next: Record<string, string>, engineProfileId?: string) => void;
};
let libraryBarProps: LibraryBarProps | null = null;

vi.mock('./LibraryPickersBar', () => ({
  LibraryPickersBar: (props: LibraryBarProps) => {
    libraryBarProps = props;
    return <div data-testid="library-pickers-bar-mock" />;
  },
}));

/**
 *
 */
function setup(overrides: Record<string, unknown> = {}) {
  const setConversionParams = vi.fn();
  const props = {
    activeReportVariant: '',
    applyWmoLibraryDefaultsSync: vi.fn(),
    caProfileBlocked: false,
    calmProfileLabel: 'ICAO',
    conversionParams: initialConversionParams(),
    inputMode: 'single',
    isReadOnly: false,
    onOpenCatalog: vi.fn(),
    reportVariantOptions: [],
    setConversionParams,
    setProfileDrawerOpen: vi.fn(),
    ...overrides,
  };
  render(<FileConverterSetup {...(props as any)} />);
  return { props, setConversionParams };
}

/** Run the functional updater passed to a ``setConversionParams`` spy. */
function applyUpdater(spy: ReturnType<typeof vi.fn>, prev: unknown) {
  const updater = spy.mock.calls[0]![0] as (p: unknown) => unknown;
  return updater(prev);
}

describe('FileConverterSetup', () => {
  afterEach(() => {
    cleanup();
    libraryBarProps = null;
    vi.restoreAllMocks();
  });

  it('maps removed annex3 wire alias onto the ICAO line without reset confirm', () => {
    const confirmSpy = vi.spyOn(window, 'confirm');
    const { props, setConversionParams } = setup();
    libraryBarProps!.onChange({ decodingLibraryId: 'LIB.DECODING.Z' }, 'annex3');
    const next = applyUpdater(setConversionParams, props.conversionParams) as any;
    expect(next.profile).toBe('ICAO_2025');
    expect(next.decodingLibraryId).toBe('LIB.DECODING.Z');
    expect(confirmSpy).not.toHaveBeenCalled();
  });

  it('coerces legacy iwxxm_us engine id to ICAO_2025 on the same line', () => {
    const confirmSpy = vi.spyOn(window, 'confirm');
    const { props, setConversionParams } = setup();
    libraryBarProps!.onChange({}, 'iwxxm_us');
    const next = applyUpdater(setConversionParams, props.conversionParams) as any;
    expect(next.profile).toBe('ICAO_2025');
    expect(next.reportVariant).toBe('');
    expect(confirmSpy).not.toHaveBeenCalled();
  });

  it('merges library ids without confirm when no engine profile is reported', () => {
    const confirmSpy = vi.spyOn(window, 'confirm');
    const { props, setConversionParams } = setup();
    libraryBarProps!.onChange({ decodingLibraryId: 'LIB.DECODING.X' });
    const next = applyUpdater(setConversionParams, props.conversionParams) as any;
    expect(next.decodingLibraryId).toBe('LIB.DECODING.X');
    expect(confirmSpy).not.toHaveBeenCalled();
  });

  it('merges library ids when the engine profile matches the current line', () => {
    const confirmSpy = vi.spyOn(window, 'confirm');
    const { props, setConversionParams } = setup();
    libraryBarProps!.onChange({ decodingLibraryId: 'LIB.DECODING.Y' }, 'ICAO_2025');
    const next = applyUpdater(setConversionParams, props.conversionParams) as any;
    expect(next.decodingLibraryId).toBe('LIB.DECODING.Y');
    expect(next.profile).toBe('ICAO_2025');
    expect(confirmSpy).not.toHaveBeenCalled();
  });

  it('updates reportVariant from the Report variant select', () => {
    const { props, setConversionParams } = setup({
      reportVariantOptions: [
        { tac_lead: 'METAR', api_product: 'METAR', iwxxm_root: 'iwxxm:METAR' },
        {
          tac_lead: 'LWIS',
          api_product: 'METAR',
          iwxxm_root: 'iwxxm-ca:LWIS',
          minimal_observation: true,
        },
      ],
    });
    // The handler reads ``e.target.value`` inside the updater, so run it synchronously.
    let next: any;
    setConversionParams.mockImplementation((updater: (p: unknown) => unknown) => {
      next = updater(props.conversionParams);
    });
    fireEvent.change(screen.getByTestId('report-variant-select'), {
      target: { value: 'LWIS' },
    });
    expect(next.reportVariant).toBe('LWIS');
    expect(screen.getByText('LWIS (minimal)')).toBeInTheDocument();
  });

  it('applies a country preset and ignores the custom (empty) choice', () => {
    const { props, setConversionParams } = setup({
      conversionParams: {
        ...initialConversionParams(),
        tacValidationLibraryId: 'LIB.TAC_VALIDATION.CUSTOM',
      },
    });
    const select = screen.getByTestId('country-preset-select');
    fireEvent.change(select, { target: { value: 'ICAO_2025' } });
    expect(setConversionParams).toHaveBeenCalledTimes(1);
    const next = applyUpdater(setConversionParams, props.conversionParams) as any;
    expect(next.profile).toBe('ICAO_2025');
    expect(next.reportVariant).toBe('');
    expect(next.tacValidationLibraryId).toBe(
      libraryResetForProfile('ICAO_2025').libraryIds.tacValidationLibraryId,
    );
  });

  it('does not change params when the country preset select picks Custom', () => {
    const { setConversionParams } = setup();
    // Default libraries match ICAO, so switching to Custom (empty) is a change event.
    fireEvent.change(screen.getByTestId('country-preset-select'), {
      target: { value: '' },
    });
    expect(setConversionParams).not.toHaveBeenCalled();
  });
});
