/**
 * DecodingLibraryPanel Vitest coverage.
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
import { DecodingLibraryPanel } from './DecodingLibraryPanel';

const listMock = vi.mocked(listLibraryAssets);
const createMock = vi.mocked(createLibraryAsset);
const updateMock = vi.mocked(updateLibraryAsset);

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

  it('edits meaning, unit, and structured type on customs (TC-EVWB-DECODE-001..003)', async () => {
    const custom = {
      ...usItem,
      body: {
        entries: [
          {
            token: 'POLY',
            explanation: 'polygon',
            unit: 'deg',
            structured_type: 'polygon',
          },
        ],
      },
    };
    listMock.mockResolvedValue({ items: [custom, icaoItem] });
    updateMock.mockResolvedValue(custom);
    render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('library-assets-select-decoding')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('library-assets-select-decoding'), {
      target: { value: custom.id },
    });
    await waitFor(() => {
      expect(screen.getByTestId('decoding-entry-explanation')).not.toBeDisabled();
    });
    fireEvent.change(screen.getByTestId('decoding-entry-explanation'), {
      target: { value: 'polygon area' },
    });
    fireEvent.change(screen.getByTestId('decoding-entry-unit'), {
      target: { value: 'm' },
    });
    fireEvent.change(screen.getByTestId('decoding-entry-structured-type'), {
      target: { value: 'range' },
    });
    fireEvent.click(screen.getByTestId('decoding-rules-save'));
    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith(
        'tok',
        custom.id,
        expect.objectContaining({
          body: expect.objectContaining({
            entries: expect.arrayContaining([
              expect.objectContaining({
                token: 'POLY',
                explanation: 'polygon area',
                unit: 'm',
                structured_type: 'range',
              }),
            ]),
          }),
          yamlBody: expect.stringContaining('kind: decoding'),
        }),
      );
    });
  });

  it('forks foundation and adds an entry (TC-EVWB-DECODE-004)', async () => {
    const forked = {
      ...usItem,
      id: 'forked-decode',
      name: 'ICAO decode glossary (custom)',
      body: { entries: [{ token: 'FEW', explanation: 'few clouds' }] },
    };
    createMock.mockResolvedValue(forked);
    listMock
      .mockResolvedValueOnce({ items: [icaoItem] })
      .mockResolvedValue({ items: [forked, icaoItem] });
    render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('decoding-rules-fork')).toBeInTheDocument();
    });
    expect(screen.getByTestId('decoding-rules-readonly')).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('decoding-rules-fork'));
    await waitFor(() => {
      expect(createMock).toHaveBeenCalledWith(
        'tok',
        expect.objectContaining({ kind: 'decoding', forkOf: icaoItem.id }),
      );
    });
    await waitFor(() => {
      expect(screen.getByTestId('decoding-rules-add')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('decoding-rules-add'));
    expect(screen.getByTestId('decoding-entry-token').getAttribute('value')).toMatch(
      /^NEW/,
    );
  });
});
