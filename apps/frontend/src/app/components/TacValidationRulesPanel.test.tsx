/**
 * Tests for TacValidationRulesPanel (TC-EVWB-TAC-001..005).
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';

import { TacValidationRulesPanel } from './TacValidationRulesPanel';

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

const listMock = vi.mocked(listLibraryAssets);
const createMock = vi.mocked(createLibraryAsset);
const updateMock = vi.mocked(updateLibraryAsset);

const builtinAsset = {
  id: 'LIB.TAC_VALIDATION.ICAO_2025',
  kind: 'tac_validation' as const,
  name: 'TAC validation · ICAO_2025',
  access: 'first_party' as const,
  engineProfileId: 'annex3',
  attachedNationalLine: 'ICAO_2025',
  body: {
    rules: [
      {
        id: 'TAC.WIND',
        code: 'WIND',
        label: 'Wind group',
        severity: 'info',
        enabled_default: true,
      },
      {
        id: 'TAC.VIS',
        code: 'VIS',
        label: 'Visibility',
        severity: 'warning',
      },
    ],
  },
};

const customAsset = {
  id: 'custom-tac-1',
  kind: 'tac_validation' as const,
  name: 'My TAC pack',
  access: 'custom' as const,
  engineProfileId: 'annex3',
  attachedNationalLine: 'ICAO_2025',
  forkOf: builtinAsset.id,
  body: {
    rules: [
      {
        id: 'CUSTOM.RULE_A',
        label: 'Custom wind',
        severity: 'error',
        pattern: '(?P<value>\\d+)',
        sample: '12',
        enabled: true,
        check: { op: 'max', value: 99, field: 'value', unit: 'KT' },
      },
    ],
  },
};

describe('TacValidationRulesPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({ items: [builtinAsset] });
  });

  it('lists searchable TAC rules with clear identity (TC-EVWB-TAC-001)', async () => {
    render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-panel')).toBeInTheDocument();
    });
    expect(screen.getByTestId('tac-validation-rule-select')).toHaveTextContent(
      'Wind group',
    );
    fireEvent.change(screen.getByTestId('tac-validation-rules-search'), {
      target: { value: 'vis' },
    });
    expect(screen.getByTestId('tac-validation-rule-select')).toHaveTextContent(
      'Visibility',
    );
    expect(screen.getByTestId('tac-validation-rule-id')).toHaveValue('TAC.VIS');
  });

  it('keeps built-in rules read-only until fork (TC-EVWB-TAC-002)', async () => {
    render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-readonly')).toBeInTheDocument();
    });
    expect(screen.getByTestId('tac-validation-rule-severity')).toBeDisabled();
    expect(screen.queryByTestId('tac-validation-rules-save')).not.toBeInTheDocument();
  });

  it('edits severity, regex, and numeric bounds on customs (TC-EVWB-TAC-003)', async () => {
    listMock.mockResolvedValue({ items: [customAsset, builtinAsset] });
    updateMock.mockResolvedValue({
      ...customAsset,
      body: {
        rules: [
          {
            id: 'CUSTOM.RULE_A',
            label: 'Custom wind',
            severity: 'warning',
            pattern: '(?P<value>\\d{2})',
            sample: '12',
            enabled: true,
            check: { op: 'min', value: 5, field: 'value' },
          },
        ],
      },
    });
    render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-asset-select')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('tac-validation-asset-select'), {
      target: { value: 'custom-tac-1' },
    });
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rule-severity')).not.toBeDisabled();
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-severity'), {
      target: { value: 'warning' },
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-pattern'), {
      target: { value: '(?P<value>\\d{2})' },
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-check-op'), {
      target: { value: 'min' },
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-check-value'), {
      target: { value: '5' },
    });
    fireEvent.click(screen.getByTestId('tac-validation-rules-save'));
    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith(
        'tok',
        'custom-tac-1',
        expect.objectContaining({
          body: expect.objectContaining({
            rules: expect.arrayContaining([
              expect.objectContaining({
                severity: 'warning',
                check: expect.objectContaining({ op: 'min', value: 5 }),
              }),
            ]),
          }),
        }),
      );
    });
    expect(screen.getByTestId('tac-validation-rules-saved')).toBeInTheDocument();
  });

  it('forks foundation and adds a custom regex rule (TC-EVWB-TAC-004)', async () => {
    createMock.mockResolvedValue(customAsset);
    listMock
      .mockResolvedValueOnce({ items: [builtinAsset] })
      .mockResolvedValue({ items: [customAsset, builtinAsset] });
    render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-fork')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('tac-validation-rules-fork'));
    await waitFor(() => {
      expect(createMock).toHaveBeenCalledWith(
        'tok',
        expect.objectContaining({
          kind: 'tac_validation',
          forkOf: builtinAsset.id,
        }),
      );
    });
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-add')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('tac-validation-rules-add'));
    expect(screen.getByTestId('tac-validation-rule-id').getAttribute('value')).toMatch(
      /^CUSTOM\./,
    );
  });

  it('round-trips YAML body on save (TC-EVWB-TAC-005)', async () => {
    listMock.mockResolvedValue({ items: [customAsset] });
    updateMock.mockResolvedValue(customAsset);
    render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-save')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('tac-validation-rules-save'));
    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith(
        'tok',
        'custom-tac-1',
        expect.objectContaining({
          yamlBody: expect.stringContaining('kind: tac_validation'),
        }),
      );
    });
  });
});
