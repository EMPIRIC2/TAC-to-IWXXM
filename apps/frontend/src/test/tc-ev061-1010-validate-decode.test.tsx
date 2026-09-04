/**
 * TC-EV061-1010 / UJ-064 — Validate IWXXM item-by-item decode panel (#1010).
 *
 * [Corpus: product §F7] [Corpus: product §F9] [Corpus: tests]
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';
import { ValidateIwxxmReport } from '../app/components/ValidateIwxxmReport';
import type { ValidateResponse } from '/utils/openapiTypes';

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));
const mockConvertMetarToIwxxm = vi.hoisted(() => vi.fn());
const mockConvertBulletin = vi.hoisted(() => vi.fn());
const mockValidateIwxxm = vi.hoisted(() => vi.fn());
const mockDecodeTac = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    product: 'METAR',
    segments: [
      {
        start: 0,
        end: 80,
        code: '<?xml version="1.0"?><iwxxm:METAR',
        explanation: 'raw dump',
      },
    ],
    residuals: [],
    summary: '<?xml version="1.0"?>',
  }),
);
const mockToast = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  loading: vi.fn(),
  dismiss: vi.fn(),
  promise: vi.fn(),
  info: vi.fn(),
}));

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: mockSignOutWithScope,
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertBulletin: mockConvertBulletin,
  ingestCollect: vi.fn(),
  EndpointNotImplementedError: class extends Error {},
  convertTafToIwxxm: vi.fn().mockResolvedValue({ success: true, data: '<iwxxm />' }),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  fetchSchemaStatus: vi.fn().mockResolvedValue({
    profile_pins: {
      ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
    },
  }),
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
  decodeTac: mockDecodeTac,
  fetchAirportRegion: vi
    .fn()
    .mockResolvedValue({ airport_code: 'KJFK', icao_region: 'NAM' }),
  validateIwxxm: mockValidateIwxxm,
}));

vi.mock('../app/components/TacEditor', () => ({
  TacEditor: ({ id, value, onChange, readOnly, 'aria-label': ariaLabel }: any) => (
    <textarea
      id={id}
      value={value}
      readOnly={readOnly}
      aria-label={ariaLabel}
      data-testid="tac-editor"
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}));

vi.mock('sonner', () => ({
  toast: mockToast,
}));

const GOLDEN_SNIPPET =
  '<iwxxm:METAR xmlns:iwxxm="http://icao.int/iwxxm/2025-2"><ok/></iwxxm:METAR>';

const DECODE_REPORT = {
  is_valid: true,
  version: '2025-2',
  layers_passed: ['XML_WELLFORMED', 'XML_SCHEMA'],
  layers_failed: [],
  package_ok: true,
  package_issues: [],
  summary: 'KJFK METAR. Wind 180 degrees at 12 knots. Temperature 15.0 °C.',
  segments: [
    { start: 0, end: 4, code: 'KJFK', explanation: 'Aerodrome' },
    { start: 10, end: 16, code: '180 deg', explanation: 'Mean wind direction' },
    { start: 20, end: 26, code: '15.0 °C', explanation: 'Air temperature' },
  ],
};

const defaultProps = {
  onLogout: vi.fn(),
  userEmail: 'decode@example.com',
  accessToken: 'decode-token',
};

describe('TC-EV061-1010 Validate IWXXM readable decode', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockValidateIwxxm.mockResolvedValue(DECODE_REPORT);
    mockConvertMetarToIwxxm.mockResolvedValue({
      results: [
        {
          name: 'iwxxm_pass_through.xml',
          content: GOLDEN_SNIPPET,
          source: 'manual',
          size_bytes: GOLDEN_SNIPPET.length,
        },
      ],
      errors: [],
      issues: [],
      total_processed: 1,
      successful: 1,
      failed: 0,
      metadata: { product: 'iwxxm', pass_through: true },
    });
  });

  it('TC-EV061-1010-001: shows item-by-item rows, not a raw XML dump', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);
    await user.click(screen.getByTestId('input-mode-validate_iwxxm'));
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: GOLDEN_SNIPPET },
    });
    await user.click(screen.getByRole('button', { name: /validate iwxxm xml/i }));

    await waitFor(() => {
      expect(screen.getByTestId('validate-iwxxm-report')).toBeInTheDocument();
    });
    expect(screen.getByTestId('decode-segments')).toBeInTheDocument();
    expect(screen.getByText('KJFK')).toBeInTheDocument();
    expect(screen.getByText('Aerodrome')).toBeInTheDocument();
    expect(screen.getByText('Air temperature')).toBeInTheDocument();
    expect(screen.queryByText(/raw dump/i)).not.toBeInTheDocument();
    expect(screen.getByTestId('decode-segments').textContent).not.toContain('<?xml');
  });

  it('TC-EV061-1010-001: ValidateIwxxmReport renders F9 rows when segments exist', () => {
    render(
      <ValidateIwxxmReport report={DECODE_REPORT as unknown as ValidateResponse} />,
    );
    expect(screen.getByTestId('decode-segments')).toBeInTheDocument();
    expect(screen.getByText('Mean wind direction')).toBeInTheDocument();
    expect(screen.getByTestId('decode-plain-language')).toHaveTextContent(/KJFK METAR/);
  });

  it('TC-EV061-1010-003: F7.s validate-only and F7.t IWXXM product still work', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);
    await user.click(screen.getByTestId('input-mode-validate_iwxxm'));
    expect(screen.getByTestId('validate-iwxxm-help')).toBeInTheDocument();
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: GOLDEN_SNIPPET },
    });
    await user.click(screen.getByRole('button', { name: /validate iwxxm xml/i }));
    await waitFor(() => {
      expect(mockValidateIwxxm).toHaveBeenCalled();
    });
    expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();

    await user.click(screen.getByTestId('input-mode-tac'));
    await user.selectOptions(screen.getByTestId('product-type-select'), 'IWXXM');
    expect(screen.getByTestId('iwxxm-product-help')).toBeInTheDocument();
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: GOLDEN_SNIPPET },
    });
    await user.click(screen.getByTestId('convert-button'));
    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
        expect.objectContaining({ product: 'IWXXM' }),
      );
    });
  });
});
