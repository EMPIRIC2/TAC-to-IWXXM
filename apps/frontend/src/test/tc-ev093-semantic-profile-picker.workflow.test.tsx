/**
 * TC-EV093-001..005 — Semantic Profile light picker deepen (#1024 / EV-093).
 *
 * Spec: docs/test-plan.md TC-EV093-*; UJ-069;
 * [Corpus: product §F7] [Corpus: product §F35] [Corpus: tests].
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';
import {
  CANONICAL_SEMANTIC_PROFILES,
  LEGACY_SEMANTIC_ALIASES,
} from '../utils/semanticProfile';

const mockConvertMetarToIwxxm = vi.hoisted(() =>
  vi.fn().mockResolvedValue({
    results: [
      {
        name: 'manual_input.txt',
        content: '<iwxxm:METAR>ev093</iwxxm:METAR>',
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

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: vi.fn().mockResolvedValue(true),
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: mockConvertMetarToIwxxm,
  convertBulletin: vi.fn(),
  ingestCollect: vi.fn(),
  EndpointNotImplementedError: class extends Error {},
  convertTafToIwxxm: vi.fn(),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  fetchSchemaStatus: vi.fn().mockResolvedValue({
    profile_pins: {
      ca_eccc: { extension_bundle_available: true, iwxxm_version: '3.0.0' },
    },
  }),
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

const TAC = 'METAR KJFK 121151Z 18008KT 10SM FEW250 22/14 A3012=';

describe('TC-EV093 — semantic Profile picker deepen', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'ev093@example.com',
    accessToken: 'token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('TC-EV093-001 lists all canonicals + aliases; default ICAO_2025', () => {
    render(<FileConverter {...defaultProps} />);
    const profile = screen.getByTestId('profile-type-select') as HTMLSelectElement;
    const values = Array.from(profile.options).map((o) => o.value);
    for (const id of CANONICAL_SEMANTIC_PROFILES) {
      expect(values).toContain(id);
    }
    for (const alias of LEGACY_SEMANTIC_ALIASES) {
      expect(values).toContain(alias);
    }
    expect(profile.value).toBe('ICAO_2025');
    expect(profile).toHaveAccessibleName(/^profile$/i);
  });

  it('TC-EV093-003 sends legacy annex3 alias when selected', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);
    await user.selectOptions(screen.getByTestId('profile-type-select'), 'annex3');
    fireEvent.change(screen.getByLabelText(/enter metar data manually/i), {
      target: { value: TAC },
    });
    await user.click(screen.getByTestId('convert-button'));
    await waitFor(() => {
      expect(mockConvertMetarToIwxxm).toHaveBeenCalledTimes(1);
    });
    expect(mockConvertMetarToIwxxm).toHaveBeenCalledWith(
      expect.objectContaining({ profile: 'annex3' }),
    );
  });

  it('TC-EV093-004 CA_ECCC still shows metadata and pins 3.0.0', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);
    await user.selectOptions(screen.getByTestId('profile-type-select'), 'CA_ECCC');
    expect(screen.getByTestId('ca-eccc-profile-metadata')).toBeVisible();
    await user.click(screen.getByLabelText(/expand parameters/i));
    const version = document.querySelector('#param-iwxxm-version') as HTMLSelectElement;
    expect(version.value).toBe('3.0.0');
  });

  it('TC-EV093-005 shows Profile trust copy without internal doc refs', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    const summary = screen.getByTestId('product-profile-bar-summary');
    expect(summary).toBeVisible();
    expect(summary.textContent).toMatch(/not destinations/i);
    expect(summary.textContent).toMatch(/editable overlays/i);
    expect(summary.textContent).not.toMatch(/ADR-|EV-|Corpus:|#\d{3,}/);

    expect(screen.getByTestId('semantic-profile-help-icon')).toBeVisible();
    expect(screen.getByTestId('exchange-profile-help-icon')).toBeVisible();

    const bar = screen.getByTestId('product-profile-bar');
    expect(bar).not.toContainElement(screen.getByTestId('semantic-profile-help'));
    expect(bar).not.toContainElement(screen.getByTestId('exchange-profile-help'));
    expect(bar).not.toContainElement(summary);

    await user.click(screen.getByText(/what's this\?/i));
    const help = screen.getByTestId('semantic-profile-help');
    expect(help).toBeVisible();
    expect(help.textContent).toMatch(/does not set destinations/i);
    expect(help.textContent).toMatch(/does not make national overlays editable/i);
    expect(help.textContent).not.toMatch(/ADR-|EV-|Corpus:|#\d{3,}/);
  });
});
