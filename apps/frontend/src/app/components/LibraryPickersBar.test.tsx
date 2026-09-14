/**
 * LibraryPickersBar unit tests (TC-EVBRIDGE-007 UI).
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

import { LibraryPickersBar } from './LibraryPickersBar';
import { defaultLibraryId } from '../../utils/libraryIds';

describe('LibraryPickersBar', () => {
  it('renders five library selects with guest defaults', async () => {
    const onChange = vi.fn();
    render(
      <LibraryPickersBar
        values={{
          conversionLibraryId: defaultLibraryId('conversion'),
          tacValidationLibraryId: defaultLibraryId('tac_validation'),
          iwxxmValidationLibraryId: defaultLibraryId('iwxxm_validation'),
          disseminationLibraryId: defaultLibraryId('dissemination'),
          decodingLibraryId: defaultLibraryId('decoding'),
        }}
        onChange={onChange}
      />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('library-pickers-bar')).toBeInTheDocument();
    });
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
});
