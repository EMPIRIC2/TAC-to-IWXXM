/**
 * TC-EV061-1012-003 / UJ-065 — FileConverter AHL decode + convert parity (#1012).
 *
 * [Corpus: product §F6] [Corpus: product §F7] [Corpus: tests]
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';

const GOLDEN = `SAUS31 KZNY 121200
METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=
METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=
`;

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));
const mockConvertMetarToIwxxm = vi.hoisted(() => vi.fn());
const mockConvertBulletin = vi.hoisted(() => vi.fn());
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
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
  decodeTac: vi.fn().mockResolvedValue({
    product: 'METAR',
    summary: 'Bulletin SAUS31 KZNY 121200 (2 reports). Station KJFK. Station KLGA.',
    segments: [
      {
        start: 0,
        end: 18,
        code: 'SAUS31 KZNY 121200',
        explanation: 'WMO abbreviated heading — SAUS31 from KZNY at day-time 121200',
      },
    ],
    residuals: [],
  }),
  fetchAirportRegion: vi
    .fn()
    .mockResolvedValue({ airport_code: 'KJFK', icao_region: 'NAM' }),
  validateIwxxm: vi.fn(),
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

vi.mock('../app/components/DecodePanel', () => ({
  DecodePanel: () => <div data-testid="decode-panel-mock" />,
}));

vi.mock('sonner', () => ({
  toast: mockToast,
}));

vi.mock('../app/components/IcaoAutocomplete', () => ({
  IcaoAutocomplete: ({ value, onChange, id, label }: any) => (
    <div>
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        data-testid="issuing-center-input"
        value={value}
        onChange={(e) => onChange(e.target.value.toUpperCase())}
      />
    </div>
  ),
}));

const defaultProps = {
  onLogout: vi.fn(),
  userEmail: 'ahl@example.com',
  accessToken: 'ahl-token',
};

describe('TC-EV061-1012 FileConverter AHL parity', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockConvertBulletin.mockResolvedValue({
      bulletin_meta: {
        ahl: 'SAUS31 KZNY 121200',
        report_count: 2,
        tt: 'SA',
        aa: 'US',
        cccc: 'KZNY',
        yygggg: '121200',
      },
      results: [
        {
          report_index: 0,
          ok: true,
          xml: '<iwxxm:METAR>jfk</iwxxm:METAR>',
          tac_input: 'METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=',
          issues: [],
        },
        {
          report_index: 1,
          ok: true,
          xml: '<iwxxm:METAR>lga</iwxxm:METAR>',
          tac_input: 'METAR KLGA 121151Z 19010KT 10SM SCT040 21/13 A3010=',
          issues: [],
        },
      ],
    });
  });

  it('convert-bulletin honors product and profile on golden AHL (TC-EV061-1012-003)', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);
    await user.click(screen.getByTestId('input-mode-ahl_bulletin'));
    fireEvent.change(screen.getByTestId('tac-editor'), { target: { value: GOLDEN } });
    expect(screen.getByTestId('bulletin-id-input')).toBeInTheDocument();
    expect(screen.getByTestId('issuing-center-input')).toBeInTheDocument();
    await user.click(screen.getByTestId('convert-button'));
    await waitFor(() => {
      expect(mockConvertBulletin).toHaveBeenCalled();
    });
    expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();
    expect(mockConvertBulletin).toHaveBeenCalledWith(
      expect.objectContaining({
        product: 'METAR',
        profile: 'annex3',
        manualText: expect.stringContaining('SAUS31 KZNY 121200'),
      }),
    );
    expect(mockToast.success).toHaveBeenCalledWith(
      expect.stringMatching(/Bulletin:\s*2 report/i),
    );
  });

  it('malformed AHL convert shows operator error without planning ids (TC-EV061-1012-004)', async () => {
    mockConvertBulletin.mockRejectedValueOnce(
      new Error(
        'The abbreviated heading is not valid. Use TTAAii CCCC YYGGgg, then one or more TAC reports.',
      ),
    );
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);
    await user.click(screen.getByTestId('input-mode-ahl_bulletin'));
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: { value: 'NOTANAHL XXXX 999999\nMETAR KJFK=\n' },
    });
    await user.click(screen.getByTestId('convert-button'));
    await waitFor(() => {
      expect(mockToast.error).toHaveBeenCalled();
    });
    const msg = String(mockToast.error.mock.calls[0]?.[0] ?? '');
    expect(msg).toMatch(/abbreviated heading/i);
    expect(msg).not.toMatch(/\[Corpus:|EV-\d+|ADR-\d+|TC-EV|#1012|docs\/sessions/);
  });
});
