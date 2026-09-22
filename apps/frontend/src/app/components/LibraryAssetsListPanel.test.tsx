/**
 * LibraryAssetsListPanel Vitest coverage.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../utils/conversionProfilesApi', () => ({
  listLibraryAssets: vi.fn(),
}));

import { listLibraryAssets } from '../../utils/conversionProfilesApi';
import { LibraryAssetsListPanel } from './LibraryAssetsListPanel';

const listMock = vi.mocked(listLibraryAssets);

const icaoItem = {
  id: 'LIB.TAC_VALIDATION.ICAO_2025',
  kind: 'tac_validation' as const,
  name: 'ICAO TAC validation',
  access: 'first_party' as const,
  engineProfileId: 'ICAO_2025',
  attachedNationalLine: 'ICAO_2025',
};

const usItem = {
  id: 'LIB.TAC_VALIDATION.US_FAA_NWS',
  kind: 'tac_validation' as const,
  name: 'US TAC validation',
  access: 'custom' as const,
  engineProfileId: 'US_FAA_NWS',
  attachedNationalLine: 'US_FAA_NWS',
};

describe('LibraryAssetsListPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({ items: [icaoItem, usItem] });
  });

  it('loads assets and changes selection', async () => {
    render(
      <LibraryAssetsListPanel
        accessToken="tok"
        kind="tac_validation"
        heading="TAC validation"
      />,
    );
    await waitFor(() => {
      expect(
        screen.getByTestId('library-assets-select-tac_validation'),
      ).toBeInTheDocument();
    });
    expect(listMock).toHaveBeenCalledWith('tok', 'tac_validation');
    expect(
      screen.getByTestId('library-assets-detail-tac_validation'),
    ).toHaveTextContent('ICAO_2025');

    fireEvent.change(screen.getByTestId('library-assets-select-tac_validation'), {
      target: { value: usItem.id },
    });
    expect(
      screen.getByTestId('library-assets-detail-tac_validation'),
    ).toHaveTextContent('US_FAA_NWS');
  });

  it('shows empty and error states including non-Error rejects', async () => {
    listMock.mockResolvedValueOnce({ items: [] });
    const { unmount } = render(
      <LibraryAssetsListPanel
        accessToken="tok"
        kind="iwxxm_validation"
        heading="IWXXM validation"
      />,
    );
    await waitFor(() => {
      expect(screen.getByText(/No assets in this library yet/i)).toBeInTheDocument();
    });
    unmount();

    listMock.mockRejectedValueOnce(new Error('list-boom'));
    const second = render(
      <LibraryAssetsListPanel
        accessToken="tok"
        kind="iwxxm_validation"
        heading="IWXXM validation"
      />,
    );
    await waitFor(() => {
      expect(screen.getByText(/list-boom/)).toBeInTheDocument();
    });
    second.unmount();

    listMock.mockRejectedValueOnce(123);
    render(
      <LibraryAssetsListPanel
        accessToken="tok"
        kind="iwxxm_validation"
        heading="IWXXM validation"
      />,
    );
    await waitFor(() => {
      expect(screen.getByText(/Unknown error/)).toBeInTheDocument();
    });
  });
});
