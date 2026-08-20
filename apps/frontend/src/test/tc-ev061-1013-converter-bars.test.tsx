/**
 * T4.1 / TC-EV061-1013 — Product/Profile + param bars (#1013).
 *
 * Spec: docs/test-plan.md TC-EV061-1013-001..003; UJ-066; UJ-067;
 * [Corpus: product §F7] [Corpus: journeys] [Corpus: tests]
 */
/* eslint-disable @typescript-eslint/no-explicit-any */
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FileConverter } from '../app/components/FileConverter';

const mockSignOutWithScope = vi.hoisted(() => vi.fn().mockResolvedValue(true));

vi.mock('/utils/supabase/logout', () => ({
  signOutWithScope: mockSignOutWithScope,
}));

vi.mock('/utils/api', () => ({
  convertMetarToIwxxm: vi.fn(),
  convertBulletin: vi.fn(),
  ingestCollect: vi.fn(),
  EndpointNotImplementedError: class extends Error {},
  convertTafToIwxxm: vi.fn().mockResolvedValue({ success: true, data: '<iwxxm />' }),
  fetchLintIssueCatalog: vi.fn().mockResolvedValue({ issues: [] }),
  lintTac: vi.fn().mockResolvedValue({ ok: true, issues: [], fixes: [] }),
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
  IcaoAutocomplete: ({ value, onChange, id, inputTestId, label }: any) => (
    <div>
      {label ? <label htmlFor={id}>{label}</label> : null}
      <input
        id={id}
        data-testid={inputTestId}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label={label}
      />
    </div>
  ),
}));

function desktopNowrapContract(el: HTMLElement): void {
  expect(el.className).toMatch(/\blg:flex-nowrap\b/);
  expect(el.className).toMatch(/\bflex-col\b/);
  expect(el.className).toMatch(/\blg:flex-row\b/);
}

describe('T4.1 / TC-EV061-1013: converter chrome bars', () => {
  const defaultProps = {
    onLogout: vi.fn(),
    userEmail: 'bars@example.com',
    accessToken: 'bars-token',
    onSwitchToAdmin: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('keeps Product Type + Profile on one no-wrap bar at ≥1024px (TC-EV061-1013-001)', () => {
    render(<FileConverter {...defaultProps} />);

    const bar = screen.getByTestId('product-profile-bar');
    const product = screen.getByTestId('product-type-select');
    const profile = screen.getByTestId('profile-type-select');

    expect(bar).toContainElement(product);
    expect(bar).toContainElement(profile);
    expect(bar).not.toContainElement(screen.getByTestId('input-mode-group'));
    desktopNowrapContract(bar);

    expect(product).toHaveAccessibleName(/^product$/i);
    expect(profile).toHaveAccessibleName(/^profile$/i);
    expect(screen.getByLabelText(/^product$/i)).toBe(product);
    expect(screen.getByLabelText(/^profile$/i)).toBe(profile);
  });

  it('keeps mode selects on one aligned no-wrap row at ≥1024px (TC-EV061-1013-002)', () => {
    render(<FileConverter {...defaultProps} />);

    const modeBar = screen.getByTestId('input-mode-bar');
    const modeGroup = screen.getByTestId('input-mode-group');

    expect(modeBar).toContainElement(modeGroup);
    expect(modeBar).not.toContainElement(screen.getByTestId('product-type-select'));
    expect(modeBar).not.toContainElement(screen.getByTestId('profile-type-select'));
    desktopNowrapContract(modeBar);

    expect(modeGroup).toHaveAccessibleName(/^input mode$/i);
    expect(screen.getByTestId('input-mode-tac')).toBeVisible();
    expect(screen.getByTestId('input-mode-ahl_bulletin')).toBeVisible();
    expect(screen.getByTestId('input-mode-collect_iwxxm')).toBeVisible();
    expect(screen.getByTestId('input-mode-validate_iwxxm')).toBeVisible();
  });

  it('keeps conversion parameters on one bar and stacks below 1024px (TC-EV061-1013-003)', async () => {
    const user = userEvent.setup();
    render(<FileConverter {...defaultProps} />);

    const paramBar = screen.getByTestId('conversion-params-bar');
    expect(paramBar).toContainElement(screen.getByTestId('bulletin-id-input'));
    expect(paramBar).toContainElement(screen.getByTestId('issuing-center-input'));
    desktopNowrapContract(paramBar);

    await user.click(screen.getByLabelText(/expand parameters/i));
    expect(paramBar).toContainElement(
      document.querySelector('#param-iwxxm-version') as HTMLElement,
    );
    expect(paramBar).toContainElement(
      document.querySelector('#param-on-error') as HTMLElement,
    );
    expect(paramBar).toContainElement(
      document.querySelector('#param-log-level') as HTMLElement,
    );

    expect(screen.getByLabelText(/bulletin id/i)).toBe(
      screen.getByTestId('bulletin-id-input'),
    );
    expect(screen.getByLabelText(/issuing center/i)).toBe(
      screen.getByTestId('issuing-center-input'),
    );
  });
});
