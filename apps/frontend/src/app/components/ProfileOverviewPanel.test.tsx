/**
 * Tests for ProfileOverviewPanel (TC-EVWB-OVERVIEW-001..004).
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ProfileOverviewPanel } from './ProfileOverviewPanel';

vi.mock('../../utils/conversionProfilesApi', () => ({
  fetchProfileCatalog: vi.fn(),
}));

import { fetchProfileCatalog } from '../../utils/conversionProfilesApi';

const catalogMock = vi.mocked(fetchProfileCatalog);

const catalog = {
  profiles: [
    {
      id: 'ICAO_2025',
      kind: 'semantic',
      status: 'implemented',
      products: ['METAR', 'TAF'],
      iwxxm_line: 'IWXXM 2025-2 core',
      rule_pack_count: 1,
      overlay_count: 1,
      deltas_vs_icao: ['Baseline'],
    },
    {
      id: 'US_FAA_NWS',
      kind: 'semantic',
      status: 'implemented',
      products: ['METAR'],
      iwxxm_line: 'IWXXM-US 3.0.0',
      rule_pack_count: 2,
      overlay_count: 0,
      deltas_vs_icao: ['RMK retained'],
    },
  ],
};

describe('ProfileOverviewPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    catalogMock.mockResolvedValue(catalog as never);
  });

  it('compares products and IWXXM lines between profiles (TC-EVWB-OVERVIEW-001)', async () => {
    render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-compare-diffs')).toBeInTheDocument();
    });
    expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
      'Products:',
    );
    expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
      'IWXXM line:',
    );
  });

  it('edits product enablement into YAML (TC-EVWB-OVERVIEW-002)', async () => {
    render(<ProfileOverviewPanel accessToken="tok" preferredProfileId="ICAO_2025" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-product-METAR')).toBeChecked();
    });
    fireEvent.click(screen.getByTestId('profile-overview-product-TAF'));
    expect(
      screen.getByTestId('profile-overview-enablement-yaml'),
    ).not.toHaveTextContent('- TAF');
    expect(screen.getByTestId('profile-overview-enablement-yaml')).toHaveTextContent(
      'kind: overview_enablement',
    );
  });

  it('toggles file types and IWXXM versions (TC-EVWB-OVERVIEW-003)', async () => {
    render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-filetype-tac')).toBeChecked();
    });
    fireEvent.click(screen.getByTestId('profile-overview-filetype-bulletin'));
    fireEvent.click(screen.getByTestId('profile-overview-iwxxm-2023-1'));
    const yaml =
      screen.getByTestId('profile-overview-enablement-yaml').textContent ?? '';
    expect(yaml).toContain('- bulletin');
    expect(yaml).toContain('2023-1');
  });

  it('keeps Activate fail-closed note and stub compat ids (TC-EVWB-OVERVIEW-004)', async () => {
    render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-panel')).toBeInTheDocument();
    });
    expect(screen.getByTestId('profile-overview-stub')).toBeInTheDocument();
    expect(screen.getByTestId('profile-overview-compare-stub')).toBeInTheDocument();
    expect(screen.getByTestId('profile-overview-enablement-stub')).toBeInTheDocument();
    expect(screen.getByTestId('profile-overview-enablement')).toHaveTextContent(
      /fail-closed/i,
    );
  });
});
