/**
 * Coverage fills for EVWB P1–P4 panels (100% FE gate).
 */

import { fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../utils/conversionProfilesApi', () => ({
  listLibraryAssets: vi.fn(),
  listConversionTemplates: vi.fn(),
  createLibraryAsset: vi.fn(),
  updateLibraryAsset: vi.fn(),
  createConversionTemplate: vi.fn(),
  updateConversionTemplate: vi.fn(),
  previewConversionTemplate: vi.fn(),
  fetchProfileCatalog: vi.fn(),
}));

import {
  createLibraryAsset,
  fetchProfileCatalog,
  listConversionTemplates,
  listLibraryAssets,
  updateConversionTemplate,
  updateLibraryAsset,
} from '../../utils/conversionProfilesApi';
import { ConversionCatalogPicker } from './ConversionCatalogPicker';
import { ConversionTemplatesPanel } from './ConversionTemplatesPanel';
import { DecodingLibraryPanel } from './DecodingLibraryPanel';
import { DisseminationLibraryPanel } from './DisseminationLibraryPanel';
import { IwxxmValidationRulesPanel } from './IwxxmValidationRulesPanel';
import { LibraryWorkbenchShell } from './LibraryWorkbenchShell';
import { ProfileOverviewPanel } from './ProfileOverviewPanel';
import { TacValidationRulesPanel } from './TacValidationRulesPanel';

const listAssets = vi.mocked(listLibraryAssets);
const listTemplates = vi.mocked(listConversionTemplates);
const createAsset = vi.mocked(createLibraryAsset);
const updateAsset = vi.mocked(updateLibraryAsset);
const updateTemplate = vi.mocked(updateConversionTemplate);
const catalog = vi.mocked(fetchProfileCatalog);

describe('EVWB P1–P4 coverage fills', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('toggles LibraryWorkbenchShell preview panels', () => {
    render(
      <LibraryWorkbenchShell
        kind="conversion"
        catalog={<div>cat</div>}
        editor={<div>ed</div>}
      />,
    );
    fireEvent.click(screen.getByTestId('library-workbench-preview-iwxxm-conversion'));
    expect(
      screen.getByTestId('library-workbench-preview-iwxxm-panel-conversion'),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByTestId('library-workbench-preview-issues-conversion'));
    expect(
      screen.getByTestId('library-workbench-preview-issues-panel-conversion'),
    ).toBeInTheDocument();
  });

  it('merges duplicate catalog blocks, selects cards, and handles load errors', async () => {
    listAssets.mockResolvedValueOnce({
      items: [
        {
          id: 'a',
          kind: 'conversion',
          name: 'A',
          access: 'first_party',
          engineProfileId: 'x',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [
              {
                id: 'g1',
                label: 'G1',
                cards: [
                  { id: 'c1', label: 'One' },
                  { id: 'c2', label: 'Two' },
                  null,
                  { label: 'noid' },
                  {},
                ],
              },
              { id: '', label: 'skip' },
              'bad',
              {
                id: 'g1',
                label: 'G1-again',
                cards: [
                  { id: 'c1', label: 'One-dup' },
                  { id: 'c3', label: 'Three' },
                ],
              },
            ],
          },
        },
        {
          id: 'b',
          kind: 'conversion',
          name: 'B',
          access: 'custom',
          engineProfileId: 'x',
          attachedNationalLine: 'ICAO_2025',
          body: { schema_blocks: 'nope' },
        },
      ],
    } as never);
    const onSelect = vi.fn();
    const { unmount } = render(
      <ConversionCatalogPicker accessToken="tok" onSelectCard={onSelect} />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('conversion-catalog-card-c3')).toBeInTheDocument();
    });
    const picker = screen.getByTestId('conversion-catalog-picker');
    fireEvent.click(within(picker).getByTestId('conversion-catalog-card-c1'));
    expect(onSelect).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'c1', label: 'One' }),
    );
    fireEvent.change(screen.getByTestId('conversion-catalog-search'), {
      target: { value: 'zzzz' },
    });
    expect(screen.getByTestId('conversion-catalog-empty')).toBeInTheDocument();
    unmount();

    listAssets.mockRejectedValueOnce('string-fail');
    render(<ConversionCatalogPicker accessToken="tok" onSelectCard={onSelect} />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-catalog-error')).toHaveTextContent(
        'Catalog unavailable',
      );
    });
  });

  it('covers catalog Error rejects, group search hits, and label fallbacks', async () => {
    listAssets.mockResolvedValueOnce({
      items: [
        {
          id: 'a',
          kind: 'conversion',
          name: 'A',
          access: 'first_party',
          engineProfileId: 'x',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [
              {
                id: 'metar-group',
                // label omitted → falls back to id
                cards: [{ id: 'c-only' }, { id: 'c-empty', label: '' }],
              },
              {
                id: 'empty-cards',
                label: 'Empty',
                cards: [],
              },
              {
                id: 'bad-cards',
                label: 'Bad',
                cards: 'nope',
              },
            ],
          },
        },
      ],
    } as never);
    const onSelect = vi.fn();
    const { unmount } = render(
      <ConversionCatalogPicker accessToken="tok" onSelectCard={onSelect} />,
    );
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-catalog-group-metar-group'),
      ).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-catalog-search'), {
      target: { value: 'metar-group' },
    });
    expect(screen.getByTestId('conversion-catalog-card-c-only')).toBeInTheDocument();
    unmount();

    listAssets.mockRejectedValueOnce(new Error('hard fail'));
    render(<ConversionCatalogPicker accessToken="tok" onSelectCard={onSelect} />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-catalog-error')).toHaveTextContent(
        'hard fail',
      );
    });
  });

  it('selects catalog cards into ConversionTemplatesPanel and covers save failure', async () => {
    listTemplates.mockResolvedValue({
      items: [
        {
          id: 'CV.WIND',
          slug: 'CV.WIND',
          name: 'Wind group',
          access: 'first_party',
          iwxxmBlock: 'iwxxm:WindObservation',
          slots: [{ id: 'ddd', label: 'direction', type: 'digits', digits: 3 }],
          sample: '18012KT',
        },
        {
          id: 'custom-1',
          slug: 'my-wind',
          name: 'My wind',
          access: 'custom',
          iwxxmBlock: 'iwxxm:WindObservation',
          slots: [{ id: 'ddd', label: 'direction', type: 'digits', digits: 3 }],
          sample: '18012KT',
        },
      ],
    } as never);
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'LIB.CONVERSION.ICAO_2025',
          kind: 'conversion',
          name: 'ICAO',
          access: 'first_party',
          engineProfileId: 'annex3',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [
              {
                id: 'g',
                label: 'g',
                cards: [
                  { id: 'iwxxm:WindObservation', label: 'Wind Observation' },
                  { id: 'iwxxm:CloudLayer', label: 'Cloud Layer' },
                ],
              },
            ],
          },
        },
      ],
    } as never);
    updateTemplate.mockRejectedValueOnce(new Error('save boom'));
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-catalog-card-iwxxm:WindObservation'),
      ).toBeInTheDocument();
    });
    fireEvent.click(
      screen.getByTestId('conversion-catalog-card-iwxxm:WindObservation'),
    );
    expect(screen.getByTestId('conversion-templates-search')).toHaveValue(
      'Wind Observation',
    );
    fireEvent.change(screen.getByTestId('conversion-templates-search'), {
      target: { value: 'zzzz-no-match' },
    });
    // selected stays pinned in filtered list
    expect(screen.getByTestId('conversion-templates-select')).toHaveValue('CV.WIND');
    fireEvent.change(screen.getByTestId('conversion-templates-search'), {
      target: { value: '' },
    });
    fireEvent.change(screen.getByTestId('conversion-templates-select'), {
      target: { value: 'custom-1' },
    });
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-save')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-templates-save'));
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-error')).toHaveTextContent(
        'save boom',
      );
    });
  });

  it('covers TAC in-values YAML, sample edits, and save/fork failures', async () => {
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'custom',
          kind: 'tac_validation',
          name: 'Custom',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            rules: [
              {
                id: 'CUSTOM.A',
                label: 'A',
                severity: 'info',
                pattern: '\\d+',
                sample: '1',
                enabled: true,
                check: { op: 'in', values: [1, 2], unit: 'KT', field: 'value' },
              },
              {
                id: 'CUSTOM.B',
                code: 'B',
                label: 'B',
                severity: 'warning',
                regex: 'x+',
                enabled: false,
                check: { op: 'weird' },
              },
              null,
              { id: '' },
              'bad',
            ],
          },
        },
      ],
    } as never);
    updateAsset.mockRejectedValueOnce(new Error('save boom'));
    createAsset.mockRejectedValueOnce('fork-string');
    render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rule-check-values')).toHaveValue(
        '1, 2',
      );
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-sample'), {
      target: { value: '99' },
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-check-values'), {
      target: { value: '1, 2, 3' },
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-check-unit'), {
      target: { value: 'MPS' },
    });
    fireEvent.click(screen.getByTestId('tac-validation-rule-enabled'));
    fireEvent.change(screen.getByTestId('tac-validation-rule-label'), {
      target: { value: 'Renamed' },
    });
    fireEvent.click(screen.getByTestId('tac-validation-rules-save'));
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-error')).toHaveTextContent(
        'save boom',
      );
    });
    fireEvent.click(screen.getByTestId('tac-validation-rules-fork'));
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-error')).toHaveTextContent(
        'Fork failed',
      );
    });
  });

  it('covers IWXXM custom overlay edits and save/fork failures', async () => {
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'custom-iw',
          kind: 'iwxxm_validation',
          name: 'Custom',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            rules: [
              {
                id: 'A.1',
                label: 'Assert',
                enabled: true,
                context: '//x',
                test: 'true()',
              },
            ],
            custom_rules: [
              {
                id: 'CUSTOM.X',
                label: 'X',
                regex: 'iwxxm:X',
                enabled: true,
                check: { op: 'max', value: 9 },
              },
            ],
          },
        },
      ],
    } as never);
    updateAsset.mockRejectedValueOnce(new Error('iw-save'));
    createAsset.mockRejectedValueOnce(new Error('iw-fork'));
    render(<IwxxmValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rule-select')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('iwxxm-validation-rule-select'), {
      target: { value: 'CUSTOM.X' },
    });
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rule-pattern')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('iwxxm-validation-rule-pattern'), {
      target: { value: 'iwxxm:Y' },
    });
    fireEvent.change(screen.getByTestId('iwxxm-validation-rule-check-op'), {
      target: { value: 'min' },
    });
    fireEvent.change(screen.getByTestId('iwxxm-validation-rule-check-value'), {
      target: { value: '1' },
    });
    fireEvent.click(screen.getByTestId('iwxxm-validation-rules-save'));
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rules-error')).toHaveTextContent(
        'iw-save',
      );
    });
    fireEvent.click(screen.getByTestId('iwxxm-validation-rules-fork'));
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rules-error')).toHaveTextContent(
        'iw-fork',
      );
    });
  });

  it('covers decoding entry select/rename and save/fork failures', async () => {
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'dec',
          kind: 'decoding',
          name: 'Dec',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            entries: [
              {
                token: 'FEW',
                explanation: 'few',
                unit: 'oktas',
                structured_type: 'text',
              },
              { token: 'SCT', explanation: '' },
            ],
          },
        },
      ],
    } as never);
    createAsset.mockRejectedValueOnce('dec-fork');
    render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('decoding-entry-FEW')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('decoding-entry-SCT'));
    await waitFor(() => {
      expect(screen.getByTestId('decoding-entry-token')).toHaveValue('SCT');
    });
    fireEvent.change(screen.getByTestId('decoding-entry-token'), {
      target: { value: 'sct2' },
    });
    expect(screen.getByTestId('decoding-entry-token')).toHaveValue('SCT2');
    fireEvent.click(screen.getByTestId('decoding-rules-fork'));
    await waitFor(() => {
      expect(screen.getByTestId('decoding-panel-error')).toHaveTextContent(
        'Fork failed',
      );
    });
  });

  it('covers decoding save failure path', async () => {
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'dec',
          kind: 'decoding',
          name: 'Dec',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            entries: [{ token: 'FEW', explanation: 'few' }],
          },
        },
      ],
    } as never);
    updateAsset.mockRejectedValueOnce(new Error('dec-save'));
    render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('decoding-rules-save')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('decoding-rules-save'));
    await waitFor(() => {
      expect(screen.getByTestId('decoding-panel-error')).toHaveTextContent('dec-save');
    });
  });

  it('covers dissemination transform select/type/note and save/fork failures', async () => {
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'dis',
          kind: 'dissemination',
          name: 'Dis',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            transforms: [
              {
                id: 'envelope',
                type: 'envelope',
                label: 'Envelope',
                enabled: true,
                note: 'n',
              },
              {
                id: 'compress',
                type: 'compress',
                label: 'Compress',
                enabled: false,
                note: '',
              },
            ],
          },
        },
      ],
    } as never);
    createAsset.mockRejectedValueOnce(new Error('dis-fork'));
    render(<DisseminationLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('dissemination-transform-compress'),
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('dissemination-transform-compress'));
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-transform-enabled')).not.toBeChecked();
    });
    fireEvent.change(screen.getByTestId('dissemination-transform-type'), {
      target: { value: 'sign-xml' },
    });
    fireEvent.change(screen.getByTestId('dissemination-transform-note'), {
      target: { value: 'updated' },
    });
    fireEvent.click(screen.getByTestId('dissemination-rules-fork'));
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-panel-error')).toHaveTextContent(
        'dis-fork',
      );
    });
  });

  it('covers dissemination save failure path', async () => {
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'dis',
          kind: 'dissemination',
          name: 'Dis',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            transforms: [
              {
                id: 'envelope',
                type: 'envelope',
                label: 'Envelope',
                enabled: true,
                note: 'n',
              },
            ],
          },
        },
      ],
    } as never);
    updateAsset.mockRejectedValueOnce('dis-string');
    render(<DisseminationLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-rules-save')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('dissemination-rules-save'));
    await waitFor(() => {
      expect(screen.getByTestId('dissemination-panel-error')).toHaveTextContent(
        'Save failed',
      );
    });
  });

  it('covers Overview catalog error, left/right select, and identical compare', async () => {
    catalog.mockRejectedValueOnce(new Error('cat boom'));
    const { unmount } = render(<ProfileOverviewPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-error')).toHaveTextContent(
        'cat boom',
      );
    });
    unmount();

    catalog.mockResolvedValue({
      profiles: [
        {
          id: 'A',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: '2025-2',
          rule_pack_count: 1,
          overlay_count: 0,
          deltas_vs_icao: ['x'],
        },
        {
          id: 'B',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: '2025-2',
          rule_pack_count: 1,
          overlay_count: 0,
          deltas_vs_icao: ['x'],
        },
      ],
    } as never);
    render(<ProfileOverviewPanel accessToken="tok" preferredProfileId="A" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-left-select')).toHaveValue('A');
    });
    // A vs B with identical catalog fields
    expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
      'No catalog differences',
    );
    fireEvent.change(screen.getByTestId('profile-overview-left-select'), {
      target: { value: 'B' },
    });
    fireEvent.change(screen.getByTestId('profile-overview-right-select'), {
      target: { value: 'A' },
    });
    expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
      'No catalog differences',
    );
  });

  it('covers multi-group template sort and empty iwxxmBlock grouping', async () => {
    listTemplates.mockResolvedValue({
      items: [
        {
          id: 'CV.A',
          slug: 'a',
          name: 'A',
          access: 'first_party',
          iwxxmBlock: 'iwxxm:Zebra',
          slots: [],
          sample: 'x',
        },
        {
          id: 'CV.B',
          slug: 'b',
          name: 'B',
          access: 'custom',
          iwxxmBlock: '',
          slots: [],
          sample: 'y',
        },
        {
          id: 'CV.C',
          slug: 'c',
          name: 'C',
          access: 'custom',
          iwxxmBlock: 'iwxxm:Alpha',
          slots: [],
          sample: 'z',
        },
      ],
    } as never);
    listAssets.mockResolvedValue({ items: [] } as never);
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-select')).toBeInTheDocument();
    });
    const select = screen.getByTestId('conversion-templates-select');
    expect(select).toHaveTextContent('A');
    expect(select).toHaveTextContent('B');
    expect(select).toHaveTextContent('C');
  });

  it('covers catalog label match, TAC id rename, IWXXM parse edges, Overview preferred miss', async () => {
    listTemplates.mockResolvedValue({
      items: [
        {
          id: 'custom-1',
          slug: 'my-wind',
          name: 'Something Else',
          access: 'custom',
          iwxxmBlock: 'iwxxm:WindObservation',
          slots: [{ id: 'ddd', label: 'direction', type: 'digits', digits: 3 }],
          sample: '18012KT',
        },
      ],
    } as never);
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'LIB.CONVERSION.ICAO_2025',
          kind: 'conversion',
          name: 'ICAO',
          access: 'first_party',
          engineProfileId: 'annex3',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [
              {
                id: 'g',
                label: 'g',
                cards: [{ id: 'pick-wind', label: 'Wind' }],
              },
            ],
          },
        },
      ],
    } as never);
    const { unmount: unmountConv } = render(
      <ConversionTemplatesPanel accessToken="tok" />,
    );
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-catalog-card-pick-wind'),
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-catalog-card-pick-wind'));
    expect(screen.getByTestId('conversion-templates-select')).toHaveValue('custom-1');
    unmountConv();

    listAssets.mockResolvedValue({
      items: [
        {
          id: 'custom',
          kind: 'tac_validation',
          name: 'Custom',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            rules: [
              {
                id: 'CUSTOM.OLD',
                label: 'Old',
                severity: 'info',
                enabled: true,
              },
              {
                id: 'CUSTOM.OTHER',
                label: 'Other',
                severity: 'warning',
                enabled: true,
              },
            ],
          },
        },
      ],
    } as never);
    const { unmount: unmountTac } = render(
      <TacValidationRulesPanel accessToken="tok" />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rule-id')).toHaveValue('CUSTOM.OLD');
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-select'), {
      target: { value: 'CUSTOM.OTHER' },
    });
    expect(screen.getByTestId('tac-validation-rule-id')).toHaveValue('CUSTOM.OTHER');
    fireEvent.change(screen.getByTestId('tac-validation-rule-id'), {
      target: { value: 'CUSTOM.RENAMED' },
    });
    expect(screen.getByTestId('tac-validation-rule-id')).toHaveValue('CUSTOM.RENAMED');
    unmountTac();

    listAssets.mockRejectedValueOnce('iw-load-string');
    const { unmount: unmountIw } = render(
      <IwxxmValidationRulesPanel accessToken="tok" />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rules-error')).toHaveTextContent(
        'Failed to load asserts',
      );
    });
    unmountIw();

    listAssets.mockResolvedValue({
      items: [
        {
          id: 'custom-iw',
          kind: 'iwxxm_validation',
          name: 'Custom',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            rules: [
              null,
              { id: '' },
              { pattern_id: 'PAT.1', label: 'From pattern id' },
              {
                id: 'WITH.CHECK',
                label: 'Checked',
                check: { op: 'min', value: 0 },
                enabled: false,
              },
            ],
            custom_rules: [
              null,
              { id: '' },
              {
                id: 'CUSTOM.NOCHECK',
                label: 'No check',
                enabled: true,
              },
            ],
          },
        },
      ],
    } as never);
    updateAsset.mockResolvedValue({
      id: 'custom-iw',
      kind: 'iwxxm_validation',
      name: 'Custom',
      access: 'custom',
      engineProfileId: 'a',
      attachedNationalLine: 'ICAO_2025',
      body: { rules: [], custom_rules: [] },
    } as never);
    const { unmount: unmountIw2 } = render(
      <IwxxmValidationRulesPanel accessToken="tok" />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rule-select')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('iwxxm-validation-rule-select'), {
      target: { value: 'CUSTOM.NOCHECK' },
    });
    fireEvent.click(screen.getByTestId('iwxxm-validation-rules-save'));
    await waitFor(() => {
      expect(screen.getByTestId('iwxxm-validation-rules-saved')).toBeInTheDocument();
    });
    unmountIw2();

    listAssets.mockResolvedValue({
      items: [
        {
          id: 'dec',
          kind: 'decoding',
          name: 'Dec',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            entries: [
              {
                token: 'CAMEL',
                explanation: 'c',
                structuredType: 'polygon',
              },
            ],
          },
        },
      ],
    } as never);
    const { unmount: unmountDec } = render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('decoding-entry-structured-type')).toHaveValue(
        'polygon',
      );
    });
    unmountDec();

    catalog.mockResolvedValue({
      profiles: [
        {
          id: 'ONLY',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR', 'TAF'],
          iwxxm_line: '2025-2',
          rule_pack_count: 1,
          overlay_count: 1,
          deltas_vs_icao: [],
        },
        {
          id: 'OTHER',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR', 'TAF'],
          iwxxm_line: '2023-1',
          rule_pack_count: 2,
          overlay_count: 0,
          deltas_vs_icao: ['note'],
        },
      ],
    } as never);
    const { rerender } = render(
      <ProfileOverviewPanel accessToken="tok" preferredProfileId="MISSING" />,
    );
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-left-select')).toHaveValue('ONLY');
    });
    expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
      'IWXXM line:',
    );
    rerender(<ProfileOverviewPanel accessToken="tok" preferredProfileId="OTHER" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-left-select')).toHaveValue('OTHER');
    });
  });

  it('covers remaining TAC load errors, save non-Error, name-match catalog, Overview empty fields', async () => {
    listAssets.mockRejectedValueOnce(new Error('tac-load'));
    const { unmount: u1 } = render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-error')).toHaveTextContent(
        'tac-load',
      );
    });
    u1();

    listAssets.mockRejectedValueOnce('tac-string');
    const { unmount: u2 } = render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-error')).toHaveTextContent(
        'Failed to load rules',
      );
    });
    u2();

    listAssets.mockResolvedValueOnce({ items: [] });
    const { unmount: u3 } = render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/No TAC validation rules|No rules/i)).toBeInTheDocument();
    });
    u3();

    listTemplates.mockResolvedValue({
      items: [
        {
          id: 'custom-1',
          slug: 'my-wind',
          name: 'Exact Name',
          access: 'custom',
          iwxxmBlock: 'iwxxm:Other',
          slots: [{ id: 'ddd', label: 'direction', type: 'digits', digits: 3 }],
          sample: '18012KT',
        },
      ],
    } as never);
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'LIB.CONVERSION.ICAO_2025',
          kind: 'conversion',
          name: 'ICAO',
          access: 'first_party',
          engineProfileId: 'annex3',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [
              {
                id: 'g',
                label: 'g',
                cards: [{ id: 'no-match-id', label: 'Exact Name' }],
              },
            ],
          },
        },
      ],
    } as never);
    updateTemplate.mockRejectedValueOnce('save-string');
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-catalog-card-no-match-id'),
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-catalog-card-no-match-id'));
    expect(screen.getByTestId('conversion-templates-select')).toHaveValue('custom-1');
    fireEvent.click(screen.getByTestId('conversion-templates-save'));
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-error')).toHaveTextContent(
        'Save failed',
      );
    });

    catalog.mockResolvedValue({
      profiles: [
        {
          id: 'FULL',
          kind: 'semantic',
          status: 'implemented',
          products: ['METAR'],
          iwxxm_line: '2025-2',
          rule_pack_count: 1,
          overlay_count: 1,
          deltas_vs_icao: ['d'],
        },
        {
          id: 'EMPTY',
          kind: 'semantic',
          status: 'implemented',
          products: [],
          iwxxm_line: '',
          rule_pack_count: null,
          overlay_count: null,
          deltas_vs_icao: [],
        },
      ],
    } as never);
    render(<ProfileOverviewPanel accessToken="tok" preferredProfileId="FULL" />);
    await waitFor(() => {
      expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent(
        'Products:',
      );
    });
    expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent('—');
    fireEvent.change(screen.getByTestId('profile-overview-left-select'), {
      target: { value: 'EMPTY' },
    });
    fireEvent.change(screen.getByTestId('profile-overview-right-select'), {
      target: { value: 'FULL' },
    });
    expect(screen.getByTestId('profile-overview-compare-diffs')).toHaveTextContent('—');
  });

  it('covers non-string schema block ids in catalog', async () => {
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'a',
          kind: 'conversion',
          name: 'A',
          access: 'first_party',
          engineProfileId: 'x',
          attachedNationalLine: 'ICAO_2025',
          body: {
            schema_blocks: [
              { id: 42, label: 'num', cards: [{ id: 'c1', label: 'One' }] },
              { id: 'ok', label: 99, cards: [{ id: 'c2', label: 'Two' }] },
            ],
          },
        },
      ],
    } as never);
    render(<ConversionCatalogPicker accessToken="tok" onSelectCard={vi.fn()} />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-catalog-card-c2')).toBeInTheDocument();
    });
    expect(screen.getByTestId('conversion-catalog-group-ok')).toHaveTextContent('ok');
  });

  it('covers empty-unit decode save, Error forks, and TAC yaml without optional fields', async () => {
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'dec',
          kind: 'decoding',
          name: 'Dec',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            entries: [{ token: 'BLANK', explanation: '', structured_type: '' }],
          },
        },
      ],
    } as never);
    updateAsset.mockResolvedValue({
      id: 'dec',
      kind: 'decoding',
      name: 'Dec',
      access: 'custom',
      engineProfileId: 'a',
      attachedNationalLine: 'ICAO_2025',
      body: { entries: [{ token: 'BLANK', explanation: '' }] },
    } as never);
    createAsset.mockRejectedValueOnce(new Error('dec-fork-err'));
    const { unmount: u1 } = render(<DecodingLibraryPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('decoding-rules-save')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('decoding-rules-save'));
    await waitFor(() => {
      expect(screen.getByTestId('decoding-rules-saved')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('decoding-rules-fork'));
    await waitFor(() => {
      expect(screen.getByTestId('decoding-panel-error')).toHaveTextContent(
        'dec-fork-err',
      );
    });
    u1();

    listAssets.mockResolvedValue({
      items: [
        {
          id: 'custom',
          kind: 'tac_validation',
          name: 'Custom',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            rules: [
              {
                id: 'CUSTOM.BARE',
                label: 'Bare',
                severity: 'info',
                enabled: true,
                check: { op: 'eq' },
              },
            ],
          },
        },
      ],
    } as never);
    updateAsset.mockResolvedValue({
      id: 'custom',
      kind: 'tac_validation',
      name: 'Custom',
      access: 'custom',
      engineProfileId: 'a',
      attachedNationalLine: 'ICAO_2025',
      body: { rules: [] },
    } as never);
    const { unmount: uTac } = render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rule-check-op')).toHaveValue('eq');
    });
    fireEvent.change(screen.getByTestId('tac-validation-rule-check-value'), {
      target: { value: '' },
    });
    fireEvent.click(screen.getByTestId('tac-validation-rules-save'));
    await waitFor(() => {
      expect(updateAsset).toHaveBeenCalled();
    });
    uTac();

    // code-only search hit
    listAssets.mockResolvedValue({
      items: [
        {
          id: 'custom',
          kind: 'tac_validation',
          name: 'Custom',
          access: 'custom',
          engineProfileId: 'a',
          attachedNationalLine: 'ICAO_2025',
          body: {
            rules: [
              {
                id: 'CUSTOM.Z',
                code: 'ZZONLY',
                label: 'Something',
                severity: 'info',
                enabled: true,
              },
            ],
          },
        },
      ],
    } as never);
    render(<TacValidationRulesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('tac-validation-rules-search')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('tac-validation-rules-search'), {
      target: { value: 'zzonly' },
    });
    expect(screen.getByTestId('tac-validation-rule-id')).toHaveValue('CUSTOM.Z');
  });
});
