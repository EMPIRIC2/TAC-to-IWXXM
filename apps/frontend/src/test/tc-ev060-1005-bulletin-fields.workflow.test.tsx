/**
 * T3.3 / TC-EV060-1005 (browser unit): Bulletin ID + Issuing Center (#1005).
 *
 * Spec: docs/test-plan.md TC-EV060-1005-001..003; UJ-062;
 * [Corpus: product §F7] [Corpus: tests].
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));
const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    results: [
      {
        name: 'manual_input.txt',
        content: '<iwxxm:METAR>bulletin</iwxxm:METAR>',
        source: 'manual_input',
        size_bytes: 40,
      },
    ],
    errors: [],
    issues: [],
    total_processed: 1,
    successful: 1,
    failed: 0,
    metadata: { bulletin_id: 'SAAA00', issuing_center: 'KWBC' },
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
  convertBulletin: vi.fn(),
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

const TAC_SAMPLE = 'METAR KJFK 121251Z 24016G28KT 3SM -RA BR BKN020 OVC040 14/11 A2990';

describe('T3.3 / TC-EV060-1005: Bulletin ID and Issuing Center', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'bulletin@example.com',
    accessToken: 'bulletin-token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('shows labeled Bulletin ID and Issuing Center without expanding parameters (TC-EV060-1005-001)', () => {
    render(<FileConverter {...defaultProps} />);

    const bulletinId = screen.getByTestId('bulletin-id-input');
    const issuingCenter = screen.getByTestId('issuing-center-input');
    expect(bulletinId).toBeVisible();
    expect(issuingCenter).toBeVisible();
    expect(bulletinId).toHaveAccessibleName(/bulletin id/i);
    expect(issuingCenter).toHaveAccessibleName(/issuing center/i);
  });

  it('sends filled Bulletin ID and Issuing Center on convert (TC-EV060-1005-001)', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.type(screen.getByTestId('bulletin-id-input'), 'saaa00');
    await user.type(screen.getByTestId('issuing-center-input'), 'kwbc');
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: TAC_SAMPLE },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });
    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({
        bulletinId: 'SAAA00',
        issuingCenter: 'KWBC',
      }),
    );
  });

  it('omits empty Bulletin ID and Issuing Center so AHL/defaults apply (TC-EV060-1005-002)', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: TAC_SAMPLE },
    });
    await user.click(screen.getByTestId('convert-button'));

    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });
    const payload = mockConvertMetarToIwxxm.mock.calls[0]?.[0] as Record<
      string,
      unknown
    >;
    expect(payload.bulletinId).toBeUndefined();
    expect(payload.issuingCenter).toBeUndefined();
  });

  it('shows one field error for invalid Issuing Center and does not convert (TC-EV060-1005-003)', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await user.type(screen.getByTestId('issuing-center-input'), 'KW1C');
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: TAC_SAMPLE },
    });
    await user.click(screen.getByTestId('convert-button'));

    expect(mockConvertMetarToIwxxm).not.toHaveBeenCalled();
    expect(screen.getByTestId('issuing-center-field-error')).toHaveTextContent(
      /4-letter/i,
    );
  });
});
