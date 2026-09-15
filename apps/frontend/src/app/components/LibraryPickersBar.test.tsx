/**
 * LibraryPickersBar unit tests (TC-EVBRIDGE-007 UI).
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../utils/conversionProfilesApi', () => ({
  listLibraryAssets: vi.fn(),
}));

import { listLibraryAssets } from '../../utils/conversionProfilesApi';
import { defaultLibraryId } from '../../utils/libraryIds';
import { LibraryPickersBar } from './LibraryPickersBar';

const listMock = vi.mocked(listLibraryAssets);

const guestValues = {
  conversionLibraryId: defaultLibraryId('conversion'),
  tacValidationLibraryId: defaultLibraryId('tac_validation'),
  iwxxmValidationLibraryId: defaultLibraryId('iwxxm_validation'),
  disseminationLibraryId: defaultLibraryId('dissemination'),
  decodingLibraryId: defaultLibraryId('decoding'),
};

describe('LibraryPickersBar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({ items: [] });
  });

  it('renders five library selects with guest defaults', async () => {
    const onChange = vi.fn();
    render(<LibraryPickersBar values={guestValues} onChange={onChange} />);
    await waitFor(() => {
      expect(screen.getByTestId('library-pickers-bar')).toBeInTheDocument();
    });
    expect(
      screen
        .getByTestId('library-pickers-bar')
        .querySelector('[data-testid="beta-badge"]'),
    ).toBeTruthy();
    expect(screen.getByTestId('conversion-library-select')).toBeInTheDocument();
    expect(screen.getByTestId('tac-validation-library-select')).toBeInTheDocument();
    expect(screen.getByTestId('iwxxm-validation-library-select')).toBeInTheDocument();
    expect(screen.getByTestId('dissemination-library-select')).toBeInTheDocument();
    expect(screen.getByTestId('decoding-library-select')).toBeInTheDocument();

    fireEvent.change(screen.getByTestId('conversion-library-select'), {
      target: { value: defaultLibraryId('conversion', 'US_FAA_NWS') },
    });
    expect(onChange).toHaveBeenCalled();
    const [, engineId] = onChange.mock.calls.at(-1) ?? [];
    expect(engineId).toBe('US_FAA_NWS');
  });

  it('falls back to guest defaults when signed-in list is empty or rejects', async () => {
    listMock.mockResolvedValueOnce({ items: [] });
    const { unmount } = render(
      <LibraryPickersBar
        accessToken="tok"
        values={{
          conversionLibraryId: '',
          tacValidationLibraryId: '',
          iwxxmValidationLibraryId: '',
          disseminationLibraryId: '',
          decodingLibraryId: '',
        }}
        onChange={vi.fn()}
      />,
    );
    await waitFor(() => {
      expect(listMock).toHaveBeenCalledWith('tok');
    });
    expect(screen.getByTestId('conversion-library-select')).toHaveValue(
      defaultLibraryId('conversion'),
    );
    unmount();

    listMock.mockRejectedValueOnce(new Error('boom'));
    render(
      <LibraryPickersBar accessToken="tok" values={guestValues} onChange={vi.fn()} />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('conversion-library-select')).toHaveValue(
        defaultLibraryId('conversion'),
      );
    });
  });

  it('uses API assets when present and keeps empty value when a kind has no options', async () => {
    listMock.mockResolvedValueOnce({
      items: [
        {
          id: 'LIB.CONVERSION.CUSTOM',
          kind: 'conversion',
          name: 'Custom conversion',
          access: 'custom',
          engineProfileId: 'US_FAA_NWS',
          attachedNationalLine: 'US_FAA_NWS',
        },
      ],
    });
    render(
      <LibraryPickersBar
        accessToken="tok"
        values={{
          conversionLibraryId: '',
          tacValidationLibraryId: '',
          iwxxmValidationLibraryId: '',
          disseminationLibraryId: '',
          decodingLibraryId: '',
        }}
        onChange={vi.fn()}
      />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('conversion-library-select')).toHaveValue(
        'LIB.CONVERSION.CUSTOM',
      );
    });
    const tacSelect = screen.getByTestId(
      'tac-validation-library-select',
    ) as HTMLSelectElement;
    expect(tacSelect).toBeDisabled();
    expect(tacSelect.value).toBe('');
    expect(tacSelect.options).toHaveLength(0);
  });
});
