/**
 * TC-EV-CND-001 — Code names dictionary page regression.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CodeNameDictionaryPage } from './CodeNameDictionaryPage';
import { CODE_NAME_DICTIONARY_PAGE_TITLE } from '@/utils/codeNameDictionaryCopy';

const fetchCodeNameDictionary = vi.fn();

vi.mock('@/utils/api', () => ({
  fetchCodeNameDictionary: (...args: unknown[]) => fetchCodeNameDictionary(...args),
}));

const samplePayload = {
  items: [
    {
      id: 'TS',
      code: 'TS',
      meaning: 'thunderstorm',
      products: ['METAR', 'SPECI', 'SIGMET', 'AIRMET'],
      countries: ['INTL'],
      wmo_amendment: 'WMO No. 306',
    },
  ],
  facets: {
    products: ['METAR', 'SIGMET', 'VAA'],
    countries: ['INTL'],
    wmo_amendments: ['Amd 77', 'WMO No. 306'],
  },
};

describe('CodeNameDictionaryPage', () => {
  beforeEach(() => {
    fetchCodeNameDictionary.mockReset();
    fetchCodeNameDictionary.mockResolvedValue(samplePayload);
  });

  it('renders title, filters, and dictionary rows', async () => {
    render(<CodeNameDictionaryPage />);
    expect(screen.getByTestId('code-name-dictionary-page')).toBeInTheDocument();
    expect(screen.getByText(CODE_NAME_DICTIONARY_PAGE_TITLE)).toBeInTheDocument();
    expect(screen.getByTestId('code-name-dictionary-filters')).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByTestId('code-name-dictionary-table')).toBeInTheDocument();
    });
    expect(screen.getByTestId('code-name-row-TS')).toHaveTextContent('thunderstorm');
    expect(screen.getByTestId('code-name-row-TS')).toHaveTextContent('METAR');
    expect(screen.getByTestId('code-name-row-TS')).toHaveTextContent('INTL');
    expect(screen.getByTestId('code-name-row-TS')).toHaveTextContent('WMO No. 306');
  });

  it('shows load error when the dictionary request fails', async () => {
    fetchCodeNameDictionary.mockRejectedValue(new Error('network'));
    render(<CodeNameDictionaryPage />);
    await waitFor(() => {
      expect(screen.getByTestId('code-name-dictionary-error')).toBeInTheDocument();
    });
  });

  it('shows empty state when no rows match', async () => {
    fetchCodeNameDictionary.mockResolvedValue({
      items: [],
      facets: samplePayload.facets,
    });
    render(<CodeNameDictionaryPage />);
    await waitFor(() => {
      expect(screen.getByTestId('code-name-dictionary-empty')).toBeInTheDocument();
    });
  });

  it('refetches when the product filter changes', async () => {
    const user = userEvent.setup();
    render(<CodeNameDictionaryPage />);
    await waitFor(() => {
      expect(fetchCodeNameDictionary).toHaveBeenCalled();
    });
    fetchCodeNameDictionary.mockClear();
    fetchCodeNameDictionary.mockResolvedValue(samplePayload);
    await user.selectOptions(
      screen.getByTestId('code-name-dictionary-product'),
      'METAR',
    );
    await waitFor(() => {
      expect(fetchCodeNameDictionary).toHaveBeenCalledWith(
        expect.objectContaining({ product: 'METAR' }),
      );
    });
  });

  it('refetches when search, country, and amendment filters change', async () => {
    const user = userEvent.setup();
    render(<CodeNameDictionaryPage />);
    await waitFor(() => {
      expect(fetchCodeNameDictionary).toHaveBeenCalled();
    });
    fetchCodeNameDictionary.mockClear();
    fetchCodeNameDictionary.mockResolvedValue(samplePayload);
    await user.type(screen.getByTestId('code-name-dictionary-search'), 'TS');
    await waitFor(() => {
      expect(fetchCodeNameDictionary).toHaveBeenCalledWith(
        expect.objectContaining({ q: 'TS' }),
      );
    });
    fetchCodeNameDictionary.mockClear();
    fetchCodeNameDictionary.mockResolvedValue(samplePayload);
    await user.selectOptions(
      screen.getByTestId('code-name-dictionary-country'),
      'INTL',
    );
    await waitFor(() => {
      expect(fetchCodeNameDictionary).toHaveBeenCalledWith(
        expect.objectContaining({ country: 'INTL' }),
      );
    });
    fetchCodeNameDictionary.mockClear();
    fetchCodeNameDictionary.mockResolvedValue(samplePayload);
    await user.selectOptions(
      screen.getByTestId('code-name-dictionary-amendment'),
      'WMO No. 306',
    );
    await waitFor(() => {
      expect(fetchCodeNameDictionary).toHaveBeenCalledWith(
        expect.objectContaining({ wmo_amendment: 'WMO No. 306' }),
      );
    });
  });

  it('tolerates missing items/facets and blank tag cells', async () => {
    fetchCodeNameDictionary.mockResolvedValue({
      items: [
        {
          id: 'BLANK',
          code: 'BLANK',
          meaning: 'untagged',
          products: [],
          countries: [],
          wmo_amendment: null,
        },
      ],
      facets: undefined,
    });
    render(<CodeNameDictionaryPage />);
    await waitFor(() => {
      expect(screen.getByTestId('code-name-row-BLANK')).toBeInTheDocument();
    });
    const row = screen.getByTestId('code-name-row-BLANK');
    expect(row).toHaveTextContent('—');
    expect(screen.getByTestId('code-name-dictionary-count')).toHaveTextContent(
      '1 code name',
    );
  });

  it('falls back when items is omitted from the response', async () => {
    fetchCodeNameDictionary.mockResolvedValue({
      facets: samplePayload.facets,
    });
    render(<CodeNameDictionaryPage />);
    await waitFor(() => {
      expect(screen.getByTestId('code-name-dictionary-empty')).toBeInTheDocument();
    });
  });
});
