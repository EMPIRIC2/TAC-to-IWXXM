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
      expect(screen.getByTestId('profile-overview-product-TAF')).toBeChecked();
    });
    fireEvent.click(screen.getByTestId('profile-overview-product-TAF'));
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-product-TAF')).not.toBeChecked();
    });
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

  it('switches primary/compare selects and flags differing ICAO delta notes', async () => {
    catalogMock.mockResolvedValue({
      profiles: [
        {
          id: 'ICAO_2025',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: 'IWXXM 2025-2 core',
          rule_pack_count: 1,
          overlay_count: 1,
        },
        {
          id: 'US_FAA_NWS',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: 'IWXXM 2025-2 core',
          rule_pack_count: 1,
          overlay_count: 1,
          deltas_vs_icao: ['National RMK'],
        },
      ],
    } as never);

    render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-left-select')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByTestId('profile-overview-left-select'), {
      target: { value: 'US_FAA_NWS' },
    });
    fireEvent.change(screen.getByTestId('profile-overview-right-select'), {
      target: { value: 'ICAO_2025' },
    });

    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
        /Difference notes vs ICAO differ/i,
      );
    });
    expect(screen.getByTestId('profile-overview-left-select')).toHaveValue(
      'US_FAA_NWS',
    );
    expect(screen.getByTestId('profile-overview-right-select')).toHaveValue(
      'ICAO_2025',
    );
  });

  it('shows em-dashes for empty products, missing IWXXM line, and null counts', async () => {
    catalogMock.mockResolvedValue({
      profiles: [
        {
          id: 'EMPTY_A',
          kind: 'semantic',
          status: 'planned',
          products: [],
          // omit iwxxm_line / counts / deltas → cover ?? and ternary em-dashes
        },
        {
          id: 'EMPTY_B',
          kind: 'semantic',
          status: 'planned',
          products: ['SPECI', 'TAF'],
          iwxxm_line: 'IWXXM 2023-1',
          rule_pack_count: 3,
          overlay_count: 2,
          deltas_vs_icao: [],
        },
      ],
    } as never);

    render(<ProfileOverviewPanel accessToken="tok" preferredProfileId="EMPTY_A" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
        'Products:',
      );
    });
    const diffs = screen.getByTestId('profile-overview-compare-diffs');
    expect(diffs).toHaveTextContent('—');
    expect(diffs).toHaveTextContent('IWXXM line:');
    expect(diffs).toHaveTextContent('Rule packs:');
    expect(diffs).toHaveTextContent('Overlays:');

    // Flip compare so the empty side is on the right (right-side em-dash branches)
    fireEvent.change(screen.getByTestId('profile-overview-left-select'), {
      target: { value: 'EMPTY_B' },
    });
    fireEvent.change(screen.getByTestId('profile-overview-right-select'), {
      target: { value: 'EMPTY_A' },
    });
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
        'SPECI, TAF vs —',
      );
    });
  });

  it('defaults IWXXM 2025-2 enablement when primary line is blank', async () => {
    catalogMock.mockResolvedValue({
      profiles: [
        {
          id: 'BLANK_LINE',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: '',
          rule_pack_count: 0,
          overlay_count: 0,
        },
      ],
    } as never);

    render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-iwxxm-2025-2')).toBeChecked();
    });
    expect(screen.getByTestId('profile-overview-enablement-yaml')).toHaveTextContent(
      'profile_id: "BLANK_LINE"',
    );
  });

  it('handles single-profile catalog, unknown preferred id, and same-side compare', async () => {
    catalogMock.mockResolvedValue({
      profiles: [
        {
          id: 'ONLY',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: 'IWXXM 2025-2',
          rule_pack_count: 0,
          overlay_count: 0,
          deltas_vs_icao: ['Same'],
        },
      ],
    } as never);

    const { rerender, unmount } = render(
      <ProfileOverviewPanel accessToken="tok" preferredProfileId="missing" />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-left-select')).toHaveValue('ONLY');
    });
    expect(screen.getByTestId('profile-overview-right-select')).toHaveValue('ONLY');
    expect(screen.getByTestId('profile-overview-compare-diffs').textContent ?? '').toBe(
      '',
    );

    rerender(<ProfileOverviewPanel accessToken="tok" preferredProfileId="ONLY" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-left-select')).toHaveValue('ONLY');
    });
    unmount();
  });

  it('shows identical-profile message, empty catalog, and catalog load errors', async () => {
    catalogMock.mockResolvedValue({
      profiles: [
        {
          id: 'ICAO_2025',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: 'IWXXM 2025-2',
          rule_pack_count: 0,
          overlay_count: 0,
          deltas_vs_icao: ['Same'],
        },
        {
          id: 'CA_ECCC',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: 'IWXXM 2025-2',
          rule_pack_count: 0,
          overlay_count: 0,
          deltas_vs_icao: ['Same'],
        },
      ],
    } as never);

    const { unmount } = render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
        /No catalog differences/i,
      );
    });
    unmount();

    catalogMock.mockResolvedValue({ profiles: [] } as never);
    const empty = render(
      <ProfileOverviewPanel accessToken="tok" preferredProfileId="ICAO_2025" />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-left-select')).toBeInTheDocument();
    });
    expect(screen.getByTestId('profile-overview-enablement-yaml')).toHaveTextContent(
      'profile_id: "unknown"',
    );
    empty.unmount();

    catalogMock.mockRejectedValueOnce(new Error('network down'));
    const errRender = render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-error')).toHaveTextContent(
        'network down',
      );
    });
    errRender.unmount();

    catalogMock.mockRejectedValueOnce('boom');
    render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-error')).toHaveTextContent(
        'Failed to load catalog',
      );
    });
  });
});
