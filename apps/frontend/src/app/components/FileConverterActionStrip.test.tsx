/**
 * Action strip download guard coverage (DI-008 leftover branches).
 *
 * [Corpus: fr] #1696
 */
import type { ButtonHTMLAttributes, SVGProps } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { FileConverterActionStrip } from './FileConverterActionStrip';

vi.mock('./fileConverterViewScope', async (importOriginal) => {
  const actual = await importOriginal<typeof import('./fileConverterViewScope')>();
  return {
    ...actual,
    Button: ({
      children,
      onClick,
      disabled,
      ...rest
    }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: string }) => (
      <button type="button" onClick={onClick} disabled={disabled} {...rest}>
        {children}
      </button>
    ),
    Download: (props: SVGProps<SVGSVGElement>) => <svg {...props} />,
    Loader2: (props: SVGProps<SVGSVGElement>) => <svg {...props} />,
    CALM_CONVERT_PRIMARY_LABEL: 'Convert',
    CALM_DOWNLOAD_PRIMARY_LABEL: 'Download IWXXM',
    IWXXM_PRODUCT_CONVERT_ARIA: 'Validate IWXXM',
    IWXXM_PRODUCT_CONVERT_LABEL: 'Validate IWXXM',
  };
});

function baseProps(overrides: Record<string, unknown> = {}) {
  return {
    calmUi: { primaryKind: 'convert' },
    conversionParams: { product: 'METAR' },
    convertDisabled: false,
    handleConvert: vi.fn(),
    handleDownloadSingle: vi.fn(),
    handleNewMetar: vi.fn(),
    inputMode: 'convert',
    isBusy: false,
    isConverting: false,
    latestConverted: null,
    saveIndicatorLabel: '',
    ...overrides,
  };
}

describe('FileConverterActionStrip', () => {
  it('keeps download disabled when latestConverted is missing', () => {
    const handleDownloadSingle = vi.fn();
    render(<FileConverterActionStrip {...baseProps({ handleDownloadSingle })} />);
    expect(screen.getByTestId('convert-download-iwxxm')).toBeDisabled();
    expect(handleDownloadSingle).not.toHaveBeenCalled();
  });

  it('download click exports the latest converted file', () => {
    const handleDownloadSingle = vi.fn();
    const latestConverted = {
      id: 'c1',
      originalName: 'a.tac',
      convertedContent: '<iwxxm/>',
    };
    render(
      <FileConverterActionStrip
        {...baseProps({ handleDownloadSingle, latestConverted })}
      />,
    );
    fireEvent.click(screen.getByTestId('convert-download-iwxxm'));
    expect(handleDownloadSingle).toHaveBeenCalledWith(latestConverted);
  });
});
