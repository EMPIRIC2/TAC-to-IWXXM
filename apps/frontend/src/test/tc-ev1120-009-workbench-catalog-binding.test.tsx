/**
 * TC-EV1120-009 — workbench Validation Issues Catalog after M1 drops.
 *
 * Changing Conversion library to a national LIB id does not change semantic_profile
 * (ICAO-only coerce). Dissemination packaging UI is off by default.
 *
 * [Corpus: tests] [Corpus: product §F15] [Corpus: fr]
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';
import { defaultLibraryId } from '../utils/libraryIds';

const fetchLintIssueCatalog = vi.hoisted(() =>
  vi.fn().mockResolvedValue({ issues: [] }),
);

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: vi.fn().mockResolvedValue({
    results: [],
    errors: [],
    issues: [],
    total_processed: 0,
    successful: 0,
    failed: 0,
  }),
  convertBulletin: vi.fn(),
  ingestCollect: vi.fn(),
  EndpointNotImplementedError: class extends Error {},
  convertTafToIwxxm: vi.fn(),
  fetchLintIssueCatalog,
  fetchSelectionOptions: vi
    .fn()
    .mockImplementation(async ({ kind }: { kind: string }) => ({
      kind,
      options: [],
    })),
  fetchSchemaStatus: vi.fn().mockResolvedValue({ profile_pins: {} }),
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
  decodeTac: vi
    .fn()
    .mockResolvedValue({ product: 'METAR', segments: [], residuals: [] }),
  fetchAirportRegion: vi.fn().mockResolvedValue(null),
  validateIwxxm: vi.fn().mockResolvedValue({
    ok: true,
    layers: [],
    issues: [],
  }),
  listDisseminationTemplates: vi.fn().mockResolvedValue({ templates: [] }),
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
  toast: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    loading: vi.fn(),
    dismiss: vi.fn(),
    promise: vi.fn(),
    info: vi.fn(),
  },
}));

vi.mock('../app/components/IcaoAutocomplete', () => ({
  IcaoAutocomplete: ({ value, onChange, id }: any) => (
    <input
      id={id}
      data-testid="icao-autocomplete"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  ),
}));

describe('TC-EV1120-009 workbench catalog Profile/Exchange binding', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'ev1123@example.com',
    accessToken: 'token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    fetchLintIssueCatalog.mockResolvedValue({ issues: [] });
    vi.spyOn(window, 'confirm').mockReturnValue(true);
  });

  it('keeps ICAO_2025 catalog binding when Conversion library changes to national LIB id', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenCalledWith(
        expect.objectContaining({
          semantic_profile: 'ICAO_2025',
          exchange_profile: 'GLOBAL_AFS',
        }),
      );
    });

    const callsBefore = fetchLintIssueCatalog.mock.calls.length;
    await user.selectOptions(
      screen.getByTestId('conversion-library-select'),
      defaultLibraryId('conversion', 'US_FAA_NWS'),
    );

    // M1: US coerces to ICAO_2025 — catalog profile filter does not switch to US_FAA_NWS.
    await waitFor(() => {
      expect(screen.getByTestId('conversion-library-select')).toHaveValue(
        defaultLibraryId('conversion', 'US_FAA_NWS'),
      );
    });
    const usProfileCalls = fetchLintIssueCatalog.mock.calls.filter(
      (call) => call[0]?.semantic_profile === 'US_FAA_NWS',
    );
    expect(usProfileCalls).toHaveLength(0);
    expect(fetchLintIssueCatalog.mock.calls.length).toBeGreaterThanOrEqual(callsBefore);
    expect(fetchLintIssueCatalog).toHaveBeenCalledWith(
      expect.objectContaining({
        semantic_profile: 'ICAO_2025',
      }),
    );
  });

  it('does not expose Disseminate Exchange packaging controls by default', async () => {
    render(<FileConverter {...defaultProps} />);

    await waitFor(() => {
      expect(fetchLintIssueCatalog).toHaveBeenCalled();
    });

    expect(screen.queryByTestId('open-dissemination-drawer')).not.toBeInTheDocument();
    expect(screen.queryByTestId('dissemination-drawer')).not.toBeInTheDocument();
    expect(
      screen.queryByTestId('dissemination-exchange-profile'),
    ).not.toBeInTheDocument();
  });
});
