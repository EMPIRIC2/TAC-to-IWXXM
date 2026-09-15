/**
 * DecodingLibraryPanel Vitest coverage.
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../utils/conversionProfilesApi', () => ({
  listLibraryAssets: vi.fn(),
}));

import { listLibraryAssets } from '../../utils/conversionProfilesApi';
import { DecodingLibraryPanel } from './DecodingLibraryPanel';

const listMock = vi.mocked(listLibraryAssets);

const icaoItem = {
  id: 'LIB.DECODING.ICAO_2025',
  kind: 'decoding' as const,
  name: 'ICAO decode glossary',
  access: 'first_party' as const,
  engineProfileId: 'ICAO_2025',
  attachedNationalLine: 'ICAO_2025',
  body: {
    entries: [
      { token: 'FEW', explanation: 'few clouds' },
      { token: 'SCT', explanation: 'scattered' },
      { token: 42 },
      null,
      { token: null, explanation: 'null-token' },
      { token: '', explanation: 'empty' },
      { token: 'BKN' },
      { token: 'OVC', explanation: null },
    ],
  },
};

const usItem = {
  id: 'LIB.DECODING.US_FAA_NWS',
  kind: 'decoding' as const,
  name: 'US decode glossary',
  access: 'custom' as const,
  engineProfileId: 'US_FAA_NWS',
  attachedNationalLine: 'US_FAA_NWS',
  body: { entries: 'not-an-array' },
};

describe('DecodingLibraryPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({ items: [icaoItem, usItem] });
  });

  it('loads entries, filters tokens, and switches libraries', async () => {
    render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('library-assets-select-decoding')).toBeInTheDocument();
    });
    expect(listMock).toHaveBeenCalledWith('tok', 'decoding');
    expect(screen.getByTestId('decoding-entries-list')).toHaveTextContent('FEW');
    expect(screen.getByTestId('decoding-entries-list')).toHaveTextContent('BKN');

    fireEvent.change(screen.getByTestId('decoding-entries-filter'), {
      target: { value: 'sct' },
    });
    expect(screen.getByTestId('decoding-entries-list')).toHaveTextContent('SCT');
    expect(screen.getByTestId('decoding-entries-list')).not.toHaveTextContent('FEW');

    fireEvent.change(screen.getByTestId('decoding-entries-filter'), {
      target: { value: 'zzzz' },
    });
    expect(screen.getByText(/No matching decode entries/i)).toBeInTheDocument();

    fireEvent.change(screen.getByTestId('library-assets-select-decoding'), {
      target: { value: usItem.id },
    });
    await waitFor(() => {
      expect(screen.getByText(/No matching decode entries/i)).toBeInTheDocument();
    });
  });

  it('shows empty list and load errors including non-Error rejects', async () => {
    listMock.mockResolvedValueOnce({ items: [] });
    const { unmount } = render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/No assets in this library yet/i)).toBeInTheDocument();
    });
    unmount();

    listMock.mockRejectedValueOnce(new Error('boom'));
    const second = render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/boom/)).toBeInTheDocument();
    });
    second.unmount();

    listMock.mockRejectedValueOnce('string-fail');
    render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/Unknown error/)).toBeInTheDocument();
    });
  });
});
