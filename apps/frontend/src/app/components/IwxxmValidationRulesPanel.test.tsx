/**
 * Tests for IwxxmValidationRulesPanel (TC-EVWB-IWXXM-001..005).
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';

import { IwxxmValidationRulesPanel } from './IwxxmValidationRulesPanel';

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
  id: 'LIB.IWXXM_VALIDATION.ICAO_2025',
  kind: 'iwxxm_validation' as const,
  name: 'IWXXM validation · ICAO_2025',
  access: 'first_party' as const,
  engineProfileId: 'annex3',
  attachedNationalLine: 'ICAO_2025',
  body: {
    rules: [
      {
        id: 'AIRMET.AIRMET-1',
        label: 'AIRMET.AIRMET-1: no AMENDMENT',
        context: '//iwxxm:AIRMET',
        test: "@reportStatus != 'AMENDMENT'",
        enabled_default: true,
      },
      {
        id: 'METAR.METAR-1',
        label: 'METAR.METAR-1: issueTime required',
        context: '//iwxxm:METAR',
        enabled_default: true,
      },
    ],
  },
};

const customAsset = {
  id: 'custom-iwxxm-1',
  kind: 'iwxxm_validation' as const,
  name: 'My IWXXM pack',
  access: 'custom' as const,
  engineProfileId: 'annex3',
  attachedNationalLine: 'ICAO_2025',
  forkOf: builtinAsset.id,
  body: {
    rules: [
      {
        id: 'AIRMET.AIRMET-1',
        label: 'AIRMET.AIRMET-1: no AMENDMENT',
        context: '//iwxxm:AIRMET',
        enabled: true,
      },
    ],
    custom_rules: [
      {
        id: 'CUSTOM.OVERLAY',
        label: 'Overlay',
        regex: 'iwxxm:Cloud',
        enabled: true,
        check: { op: 'eq', value: 1 },
      },
    ],
  },
};

describe('IwxxmValidationRulesPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({ items: [builtinAsset] });
  });

  it('lists searchable IWXXM asserts (TC-EVWB-IWXXM-001)', async () => {
    render(<IwxxmValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rules-panel')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('iwxxm-validation-rules-search'), {
      target: { value: 'metar' },
    });
    expect(screen.getByTestId('iwxxm-validation-rule-select')).toHaveTextContent(
      'METAR',
    );
  });

  it('keeps built-in asserts read-only until fork (TC-EVWB-IWXXM-002)', async () => {
    render(<IwxxmValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rules-readonly')).toBeInTheDocument();
    });
    expect(screen.getByTestId('iwxxm-validation-rule-enabled')).toBeDisabled();
    expect(screen.queryByTestId('iwxxm-validation-rules-save')).not.toBeInTheDocument();
  });

  it('toggles enable and saves custom overlays (TC-EVWB-IWXXM-003)', async () => {
    listMock.mockResolvedValue({ items: [customAsset, builtinAsset] });
    updateMock.mockResolvedValue(customAsset);
    render(<IwxxmValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-asset-select')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('iwxxm-validation-asset-select'), {
      target: { value: 'custom-iwxxm-1' },
    });
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rule-enabled')).not.toBeDisabled();
    });
    fireEvent.click(screen.getByTestId('iwxxm-validation-rule-enabled'));
    fireEvent.click(screen.getByTestId('iwxxm-validation-rules-save'));
    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith(
        'tok',
        'custom-iwxxm-1',
        expect.objectContaining({
          body: expect.objectContaining({
            rules: expect.arrayContaining([
              expect.objectContaining({ id: 'AIRMET.AIRMET-1', enabled: false }),
            ]),
          }),
        }),
      );
    });
  });

  it('forks foundation and adds custom overlay (TC-EVWB-IWXXM-004)', async () => {
    createMock.mockResolvedValue(customAsset);
    listMock
      .mockResolvedValueOnce({ items: [builtinAsset] })
      .mockResolvedValue({ items: [customAsset, builtinAsset] });
    render(<IwxxmValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rules-fork')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('iwxxm-validation-rules-fork'));
    await waitFor(() => {
      expect(createMock).toHaveBeenCalledWith(
        'tok',
        expect.objectContaining({
          kind: 'iwxxm_validation',
          forkOf: builtinAsset.id,
        }),
      );
    });
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rules-add')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('iwxxm-validation-rules-add'));
    expect(screen.getByTestId('iwxxm-validation-rule-id')).toHaveTextContent(
      /CUSTOM\.IWXXM_/,
    );
  });

  it('persists numeric check on custom overlay YAML (TC-EVWB-IWXXM-005)', async () => {
    listMock.mockResolvedValue({ items: [customAsset] });
    updateMock.mockResolvedValue(customAsset);
    render(<IwxxmValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rule-select')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('iwxxm-validation-rule-select'), {
      target: { value: 'CUSTOM.OVERLAY' },
    });
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rule-check-op')).toHaveValue('eq');
    });
    fireEvent.click(screen.getByTestId('iwxxm-validation-rules-save'));
    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith(
        'tok',
        'custom-iwxxm-1',
        expect.objectContaining({
          yamlBody: expect.stringContaining('custom_rules:'),
          body: expect.objectContaining({
            custom_rules: expect.arrayContaining([
              expect.objectContaining({
                id: 'CUSTOM.OVERLAY',
                check: expect.objectContaining({ op: 'eq', value: 1 }),
              }),
            ]),
          }),
        }),
      );
    });
  });
});
