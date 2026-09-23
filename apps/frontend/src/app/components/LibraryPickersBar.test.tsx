/**
 * LibraryPickersBar unit tests (TC-EVYCL / #1251).
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../utils/api', () => ({
  fetchSelectionOptions: vi.fn(),
}));

import { fetchSelectionOptions } from '../../utils/api';
import { defaultLibraryId } from '../../utils/libraryIds';
import { LibraryPickersBar } from './LibraryPickersBar';

const fetchMock = vi.mocked(fetchSelectionOptions);

const guestValues = {
  conversionLibraryId: defaultLibraryId('conversion'),
  tacValidationLibraryId: defaultLibraryId('tac_validation'),
  iwxxmValidationLibraryId: defaultLibraryId('iwxxm_validation'),
  disseminationLibraryId: defaultLibraryId('dissemination'),
  decodingLibraryId: defaultLibraryId('decoding'),
};

function mockFourKindsEmpty() {
  fetchMock.mockImplementation(async ({ kind }) => ({
    kind,
    options: [],
  }));
}

describe('LibraryPickersBar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFourKindsEmpty();
  });

  it('renders four library selects with guest defaults (no Dissemination)', async () => {
    const onChange = vi.fn();
    render(<LibraryPickersBar values={guestValues} onChange={onChange} />);
    await waitFor(() => {
      expect(screen.getByTestId('library-pickers-bar')).toBeInTheDocument();
    });
    expect(screen.getByTestId('conversion-library-select')).toBeInTheDocument();
    expect(screen.getByTestId('tac-validation-library-select')).toBeInTheDocument();
    expect(screen.getByTestId('iwxxm-validation-library-select')).toBeInTheDocument();
    expect(screen.getByTestId('decoding-library-select')).toBeInTheDocument();
    expect(
      screen.queryByTestId('dissemination-library-select'),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId('conversion-library-help')).toBeInTheDocument();
    expect(screen.getByTestId('decoding-library-help')).toBeInTheDocument();

    fireEvent.change(screen.getByTestId('conversion-library-select'), {
      target: { value: defaultLibraryId('conversion', 'US_FAA_NWS') },
    });
    expect(onChange).toHaveBeenCalled();
    const [, engineId] = onChange.mock.calls.at(-1) ?? [];
    expect(engineId).toBe('US_FAA_NWS');
  });

  it('loads selection-options and opens catalog links', async () => {
    fetchMock.mockImplementation(async ({ kind }) => ({
      kind,
      options: [
        {
          id: defaultLibraryId(
            kind === 'dissemination' ? 'conversion' : kind,
            'CA_ECCC',
          ),
          label: `${kind} · CA_ECCC`,
        },
      ],
    }));
    const onOpenCatalog = vi.fn();
    render(
      <LibraryPickersBar
        values={guestValues}
        onChange={vi.fn()}
        onOpenCatalog={onOpenCatalog}
      />,
    );
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalled();
    });
    await waitFor(() => {
      expect(
        Array.from(
          screen.getByTestId('conversion-library-select').querySelectorAll('option'),
        ).map((opt) => opt.getAttribute('value')),
      ).toContain(defaultLibraryId('conversion', 'CA_ECCC'));
    });
    fireEvent.click(screen.getByTestId('conversion-library-catalog-link'));
    expect(onOpenCatalog).toHaveBeenCalledWith('conversion');
    fireEvent.click(screen.getByTestId('tac-validation-library-catalog-link'));
    expect(onOpenCatalog).toHaveBeenCalledWith('lint');
  });

  it('omits the engine profile when the conversion id is not a LIB id', async () => {
    const onChange = vi.fn();
    render(<LibraryPickersBar values={guestValues} onChange={onChange} />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-library-select')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-library-select'), {
      target: { value: 'custom-asset' },
    });
    expect(onChange.mock.calls.at(-1)?.[1]).toBeUndefined();
  });

  it('falls back to guest defaults when selection-options rejects', async () => {
    fetchMock.mockRejectedValue(new Error('boom'));
    render(<LibraryPickersBar values={guestValues} onChange={vi.fn()} />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-library-select')).toHaveValue(
        defaultLibraryId('conversion'),
      );
    });
  });
});
