/**
 * TC-EV090-002 / TC-EV090-003 — Exchange profile light picker (#1024 / EV-090).
 *
 * Spec: docs/test-plan.md TC-EV090-002..003; UJ-069;
 * [Corpus: product §F7] [Corpus: product §F36] [Corpus: tests].
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';
import { EXCHANGE_PROFILE_OPTIONS } from '../utils/exchangeProfile';

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));
const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    results: [
      {
        name: 'manual_input.txt',
        content: '<iwxxm:METAR>exchange</iwxxm:METAR>',
        source: 'manual_input',
        size_bytes: 40,
      },
    ],
    errors: [],
    issues: [],
    total_processed: 1,
    successful: 1,
    failed: 0,
  }),
);
const mockConvertBulletin = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    bulletin_meta: {
      ahl: 'SAUS31 KZNY 121200',
      report_count: 1,
      cccc: 'KZNY',
      yygggg: '121200',
    },
    results: [
      {
        report_index: 0,
        ok: true,
        tac_input: 'METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=',
        xml: '<collect:MeteorologicalBulletin xmlns:collect="http://icao.int/iwxxm/collect/2025-2"/>',
        issues: [],
        fixes: [],
      },
    ],
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
  lintTac: vi.fn().mockResolvedValue({
    ok: true,
    issues: [],
    fixes: [],
  }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
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
  DecodePanel: () => null,
}));

vi.mock('sonner', () => ({
  toast: mockToast,
}));

describe('TC-EV090: Exchange profile light picker', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('TC-EV090-002: lists registered exchange ids with accessible label', () => {
    render(
      <FileConverter accessToken="tok" isGuest={false} userEmail="op@example.com" />,
    );
    const exchange = screen.getByTestId('exchange-profile-select') as HTMLSelectElement;
    expect(exchange).toBeVisible();
    expect(exchange).toHaveAccessibleName(/exchange profile/i);
    expect(screen.getByTestId('exchange-profile-help')).toHaveTextContent(
      /does not choose destinations or credentials/i,
    );
    const values = Array.from(exchange.options).map((o) => o.value);
    expect(values).toEqual(EXCHANGE_PROFILE_OPTIONS.map((o) => o.value));
    expect(exchange.value).toBe('GLOBAL_AFS');
    expect(screen.getByTestId('profile-type-select')).toBeVisible();
  });

  it('TC-EV090-003: sends exchange_profile on AHL bulletin convert', async () => {
    const user = userEvent.setup();
    render(
      <FileConverter accessToken="tok" isGuest={false} userEmail="op@example.com" />,
    );

    await user.click(screen.getByTestId('input-mode-ahl_bulletin'));
    await user.selectOptions(
      screen.getByTestId('exchange-profile-select'),
      'APAC_ROBEX',
    );
    fireEvent.change(screen.getByTestId('tac-editor'), {
      target: {
        value:
          'SAUS31 KZNY 121200\nMETAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=',
      },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertBulletin).toHaveBeenCalled();
    });
    expect(mockConvertBulletin).toHaveBeenCalledWith(
      expect.objectContaining({
        exchangeProfile: 'APAC_ROBEX',
      }),
    );
  });

  it('hydrates exchange_profile snake_case from a stored session', () => {
    render(
      <FileConverter
        accessToken="tok"
        isGuest={false}
        userEmail="op@example.com"
        loadedWorkSession={
          {
            id: 'sess-ex-snake',
            status: 'wip',
            conversion_params: {
              product: 'METAR',
              profile: 'annex3',
              exchange_profile: 'EUR_RODEX',
            },
          } as any
        }
      />,
    );
    expect(screen.getByTestId('exchange-profile-select')).toHaveValue('EUR_RODEX');
  });

  it('hydrates exchangeProfile camelCase from a stored session', () => {
    render(
      <FileConverter
        accessToken="tok"
        isGuest={false}
        userEmail="op@example.com"
        loadedWorkSession={
          {
            id: 'sess-ex-camel',
            status: 'wip',
            conversion_params: {
              product: 'METAR',
              profile: 'annex3',
              exchangeProfile: 'AFI',
            },
          } as any
        }
      />,
    );
    expect(screen.getByTestId('exchange-profile-select')).toHaveValue('AFI');
  });
});
