/**
 * DisseminationLibraryPanel Vitest coverage.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../utils/conversionProfilesApi', () => ({
  listLibraryAssets: vi.fn(),
}));

import { listLibraryAssets } from '../../utils/conversionProfilesApi';
import { DisseminationLibraryPanel } from './DisseminationLibraryPanel';

const listMock = vi.mocked(listLibraryAssets);

const icaoItem = {
  id: 'LIB.DISSEMINATION.ICAO_2025',
  kind: 'dissemination' as const,
  name: 'ICAO dissemination',
  access: 'first_party' as const,
  engineProfileId: 'ICAO_2025',
  attachedNationalLine: 'ICAO_2025',
  body: {
    transforms: [
      'compress',
      { id: 'sign', type: 'sign-xml' },
      { type: 'wrap' },
      { id: 'only-id' },
      {},
      99,
      null,
    ],
  },
};

const emptyItem = {
  id: 'LIB.DISSEMINATION.US_FAA_NWS',
  kind: 'dissemination' as const,
  name: 'US dissemination',
  access: 'custom' as const,
  engineProfileId: 'US_FAA_NWS',
  attachedNationalLine: 'US_FAA_NWS',
  body: { transforms: 'bad' },
};

describe('DisseminationLibraryPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({ items: [icaoItem, emptyItem] });
  });

  it('loads transforms and switches libraries', async () => {
    render(<DisseminationLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('library-assets-select-dissemination'),
      ).toBeInTheDocument();
    });
    expect(listMock).toHaveBeenCalledWith('tok', 'dissemination');
    const list = screen.getByTestId('dissemination-transforms-list');
    expect(list).toHaveTextContent('compress');
    expect(list).toHaveTextContent('sign-xml');
    expect(list).toHaveTextContent('(sign)');
    expect(list).toHaveTextContent('wrap');

    fireEvent.change(screen.getByTestId('library-assets-select-dissemination'), {
      target: { value: emptyItem.id },
    });
    await waitFor(() => {
      expect(
        screen.getByText(/No transforms defined for this asset/i),
      ).toBeInTheDocument();
    });
  });

  it('shows empty list and load errors including non-Error rejects', async () => {
    listMock.mockResolvedValueOnce({ items: [] });
    const { unmount } = render(<DisseminationLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/No assets in this library yet/i)).toBeInTheDocument();
    });
    unmount();

    listMock.mockRejectedValueOnce(new Error('dissem-fail'));
    const second = render(<DisseminationLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/dissem-fail/)).toBeInTheDocument();
    });
    second.unmount();

    listMock.mockRejectedValueOnce({ nope: true });
    render(<DisseminationLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/Unknown error/)).toBeInTheDocument();
    });
  });
});
