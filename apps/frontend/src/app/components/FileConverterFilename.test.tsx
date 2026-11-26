/**
 * UX-2026-11-26-convert-optional-params — Convert optional-parameters strip.
 *
 * [Corpus: ui-style]
 */
import { createRef } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {
  INCLUDE_NATIONAL_REMARKS_HELP,
  INCLUDE_NATIONAL_REMARKS_LABEL,
} from './IncludeNationalRemarksControl';
import { FileConverterFilename } from './FileConverterFilename';
import {
  PROPAGATE_RESIDUALS_HELP,
  PROPAGATE_RESIDUALS_LABEL,
} from './PropagateResidualsControl';

function baseProps(overrides: Record<string, unknown> = {}) {
  return {
    inputMode: 'convert',
    isBusy: false,
    isReadOnly: false,
    liveIwxxm: true,
    outputFilename: 'METARKSB',
    outputFilenameOwnedRef: createRef<boolean>(),
    propagateResiduals: false,
    includeNationalRemarks: true,
    softPreview: false,
    setLiveIwxxm: vi.fn(),
    setOutputFilename: vi.fn(),
    setPropagateResiduals: vi.fn(),
    setIncludeNationalRemarks: vi.fn(),
    setSoftPreview: vi.fn(),
    ...overrides,
  };
}

describe('FileConverterFilename — conversion options strip (UX-2026-11-26)', () => {
  it('groups filename + toggles in one Conversion options block', () => {
    render(<FileConverterFilename {...baseProps()} />);

    const block = screen.getByTestId('conversion-options');
    expect(block).toBeInTheDocument();
    expect(within(block).getByTestId('output-filename-near-convert')).toBeInTheDocument();
    expect(within(block).getByTestId('conversion-option-toggles')).toBeInTheDocument();
    expect(within(block).getByText(PROPAGATE_RESIDUALS_LABEL)).toBeInTheDocument();
    expect(within(block).getByText(INCLUDE_NATIONAL_REMARKS_LABEL)).toBeInTheDocument();
    expect(within(block).getByTestId('live-iwxxm-toggle')).toBeInTheDocument();
  });

  it('keeps the filename control full-width with one-line helper under the field', () => {
    render(<FileConverterFilename {...baseProps()} />);

    const fieldWrap = screen.getByTestId('output-filename-near-convert');
    expect(fieldWrap.className).toMatch(/\bw-full\b/);
    const input = screen.getByTestId('output-filename-input');
    expect(input.className).toMatch(/\bw-full\b/);
    expect(screen.getByTestId('output-filename-preview')).toHaveTextContent('METARKSB.xml');
    // Long residual / national help must not sit under the toggle stack (details may hold it)
    const toggles = screen.getByTestId('conversion-option-toggles');
    expect(within(toggles).queryByText(PROPAGATE_RESIDUALS_HELP)).not.toBeInTheDocument();
    expect(within(toggles).queryByText(INCLUDE_NATIONAL_REMARKS_HELP)).not.toBeInTheDocument();
  });

  it('exposes long option help via About these options (not always-visible paragraphs)', async () => {
    const user = userEvent.setup();
    render(<FileConverterFilename {...baseProps()} />);

    const about = screen.getByTestId('conversion-options-about');
    expect(about).toBeInTheDocument();
    expect(within(about).getByText(/About these options/i)).toBeInTheDocument();
    // Closed by default — open to read deferred help
    await user.click(within(about).getByText(/About these options/i));
    expect(within(about).getByText(PROPAGATE_RESIDUALS_HELP)).toBeInTheDocument();
    expect(within(about).getByText(INCLUDE_NATIONAL_REMARKS_HELP)).toBeInTheDocument();
  });

  it('mutates filename and toggles (success paths)', async () => {
    const user = userEvent.setup();
    const setOutputFilename = vi.fn();
    const setPropagateResiduals = vi.fn();
    const setIncludeNationalRemarks = vi.fn();
    const setLiveIwxxm = vi.fn();

    render(
      <FileConverterFilename
        {...baseProps({
          setOutputFilename,
          setPropagateResiduals,
          setIncludeNationalRemarks,
          setLiveIwxxm,
        })}
      />,
    );

    await user.clear(screen.getByTestId('output-filename-input'));
    await user.type(screen.getByTestId('output-filename-input'), 'K');
    expect(setOutputFilename).toHaveBeenCalled();

    await user.click(screen.getByTestId('propagate-residuals-toggle'));
    expect(setPropagateResiduals).toHaveBeenCalledWith(true);

    await user.click(screen.getByTestId('include-national-remarks-toggle'));
    expect(setIncludeNationalRemarks).toHaveBeenCalledWith(false);

    await user.click(screen.getByTestId('live-iwxxm-toggle'));
    expect(setLiveIwxxm).toHaveBeenCalledWith(false);
  });

  it('rejects edits when read-only (failure / disabled)', () => {
    render(<FileConverterFilename {...baseProps({ isReadOnly: true })} />);
    expect(screen.getByTestId('output-filename-input')).toHaveAttribute('readonly');
    expect(screen.getByTestId('propagate-residuals-toggle')).toBeDisabled();
    expect(screen.getByTestId('include-national-remarks-toggle')).toBeDisabled();
    expect(screen.getByTestId('live-iwxxm-toggle')).toBeDisabled();
  });

  it('hides the strip for validate_iwxxm mode', () => {
    render(<FileConverterFilename {...baseProps({ inputMode: 'validate_iwxxm' })} />);
    expect(screen.queryByTestId('conversion-options')).not.toBeInTheDocument();
  });
});
