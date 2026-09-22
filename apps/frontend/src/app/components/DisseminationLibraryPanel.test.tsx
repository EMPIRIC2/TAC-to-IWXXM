/**
 * DisseminationLibraryPanel Vitest coverage.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../utils/conversionProfilesApi', () => ({
  listLibraryAssets: vi.fn(),
  createLibraryAsset: vi.fn(),
  updateLibraryAsset: vi.fn(),
}));

import {
  createLibraryAsset,
  listLibraryAssets,
  updateLibraryAsset,
} from '../../utils/conversionProfilesApi';
import { DisseminationLibraryPanel } from './DisseminationLibraryPanel';

const listMock = vi.mocked(listLibraryAssets);
const createMock = vi.mocked(createLibraryAsset);
const updateMock = vi.mocked(updateLibraryAsset);

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

  it('toggles enable and saves custom transforms (TC-EVWB-DISSEM-001..002)', async () => {
    const custom = {
      ...emptyItem,
      body: {
        transforms: [
          {
            id: 'envelope',
            type: 'envelope',
            label: 'Message envelope',
            enabled: true,
            note: 'Pattern-only',
          },
        ],
      },
    };
    listMock.mockResolvedValue({ items: [custom, icaoItem] });
    updateMock.mockResolvedValue(custom);
    render(<DisseminationLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('library-assets-select-dissemination'),
      ).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('library-assets-select-dissemination'), {
      target: { value: custom.id },
    });
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-transform-enabled')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByTestId('dissemination-transform-enabled'));
    fireEvent.click(screen.getByTestId('dissemination-rules-save'));
    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith(
        'tok',
        custom.id,
        expect.objectContaining({
          body: expect.objectContaining({
            transforms: expect.arrayContaining([
              expect.objectContaining({ id: 'envelope', enabled: false }),
            ]),
          }),
          yamlBody: expect.stringContaining('kind: dissemination'),
        }),
      );
    });
  });

  it('forks foundation, adds transform, and never exposes secret fields (TC-EVWB-DISSEM-003..004)', async () => {
    const forked = {
      ...emptyItem,
      id: 'forked-dissem',
      name: 'ICAO dissemination (custom)',
      body: {
        transforms: [
          {
            id: 'envelope',
            type: 'envelope',
            label: 'Message envelope',
            enabled: true,
          },
        ],
      },
    };
    createMock.mockResolvedValue(forked);
    listMock
      .mockResolvedValueOnce({ items: [icaoItem] })
      .mockResolvedValue({ items: [forked, icaoItem] });
    render(<DisseminationLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-rules-fork')).toBeInTheDocument();
    });
    expect(screen.getByTestId('dissemination-rules-readonly')).toBeInTheDocument();
    expect(screen.queryByLabelText(/password/i)).not.toBeInTheDocument();
    expect(screen.queryByPlaceholderText(/https?:\/\//i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByTestId('dissemination-rules-fork'));
    await waitFor(() => {
      expect(createMock).toHaveBeenCalledWith(
        'tok',
        expect.objectContaining({ kind: 'dissemination', forkOf: icaoItem.id }),
      );
    });
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-rules-add')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('dissemination-rules-add'));
    expect(screen.getByTestId('dissemination-transform-type')).toHaveValue('envelope');
  });
});
