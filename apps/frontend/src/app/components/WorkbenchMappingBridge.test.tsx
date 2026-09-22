/**
 * WorkbenchMappingBridge tests (Convert dual surface).
 */

import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../../utils/conversionProfilesApi', () => ({
  listConversionTemplates: vi.fn(),
  previewConversionTemplate: vi.fn(),
}));

import {
  listConversionTemplates,
  previewConversionTemplate,
} from '../../utils/conversionProfilesApi';
import { WorkbenchMappingBridge } from './WorkbenchMappingBridge';

const listMock = vi.mocked(listConversionTemplates);
const previewMock = vi.mocked(previewConversionTemplate);

const windItem = {
  id: 'CV.WIND',
  slug: 'CV.WIND',
  name: 'Wind group',
  access: 'first_party' as const,
  iwxxmBlock: 'iwxxm:WindObservation',
  slots: [],
  sample: '18012G20KT',
};

const otherItem = {
  id: 'CV.VIS',
  slug: 'CV.VIS',
  name: 'Visibility',
  access: 'first_party' as const,
  iwxxmBlock: 'iwxxm:HorizontalVisibility',
  slots: [],
  sample: '9999',
};

describe('WorkbenchMappingBridge', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({ items: [windItem, otherItem] });
  });

  it('loads templates and previews mapping on Convert', async () => {
    previewMock.mockResolvedValue({
      templateId: 'CV.WIND',
      focusGroup: '18012G20KT',
      matched: true,
      captures: [],
      xmlBlock: '<iwxxm:WindObservation/>',
      compiledPattern: '',
    });
    render(
      <WorkbenchMappingBridge accessToken="tok" tacText="METAR KJFK 18012G20KT=" />,
    );
    await waitFor(() => {
      expect(
        screen.getByTestId('workbench-mapping-bridge-template'),
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('workbench-mapping-bridge-preview'));
    await waitFor(() => {
      expect(screen.getByTestId('mapping-bridge-iwxxm-block')).toHaveTextContent(
        'WindObservation',
      );
    });
    expect(previewMock).toHaveBeenCalled();
  });

  it('seeds focus from last non-METAR token when wind group is absent', async () => {
    render(<WorkbenchMappingBridge accessToken="tok" tacText="SPECI KJFK FEW020 =" />);
    await waitFor(() => {
      expect(screen.getByTestId('workbench-mapping-bridge-focus')).toHaveValue(
        'FEW020',
      );
    });
  });

  it('falls back to default focus when TAC has only product markers', async () => {
    render(<WorkbenchMappingBridge accessToken="tok" tacText="METAR =" />);
    await waitFor(() => {
      expect(screen.getByTestId('workbench-mapping-bridge-focus')).toHaveValue(
        '18012G20KT',
      );
    });
  });

  it('seeds focus from MPS wind token when present', async () => {
    render(<WorkbenchMappingBridge accessToken="tok" tacText="METAR CYUL 24010MPS" />);
    await waitFor(() => {
      expect(screen.getByTestId('workbench-mapping-bridge-focus')).toHaveValue(
        '24010MPS',
      );
    });
  });

  it('uses default focus when tacText is blank', async () => {
    render(<WorkbenchMappingBridge accessToken="tok" tacText="   " />);
    await waitFor(() => {
      expect(screen.getByTestId('workbench-mapping-bridge-focus')).toHaveValue(
        '18012G20KT',
      );
    });
  });

  it('changes template and focus, surfaces preview errors and skip chips', async () => {
    previewMock.mockResolvedValueOnce({
      templateId: 'CV.VIS',
      focusGroup: '9999',
      matched: false,
      captures: [],
      xmlBlock: '',
      compiledPattern: '',
      skipped: [
        { slot: '', label: '', gloss: '' },
        { slot: 'x', label: 'labeled', gloss: '' },
      ],
    });
    render(<WorkbenchMappingBridge accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('workbench-mapping-bridge-template'),
      ).toBeInTheDocument();
    });

    fireEvent.change(screen.getByTestId('workbench-mapping-bridge-template'), {
      target: { value: otherItem.id },
    });
    fireEvent.change(screen.getByTestId('workbench-mapping-bridge-focus'), {
      target: { value: '9999' },
    });
    expect(screen.getByTestId('workbench-mapping-bridge-focus')).toHaveValue('9999');

    fireEvent.click(screen.getByTestId('workbench-mapping-bridge-preview'));
    await waitFor(() => {
      expect(screen.getByTestId('mapping-bridge-skip-chips')).toHaveTextContent('skip');
    });
    expect(screen.getByTestId('mapping-bridge-skip-chips')).toHaveTextContent(
      'labeled',
    );

    previewMock.mockRejectedValueOnce(new Error('preview-boom'));
    fireEvent.click(screen.getByTestId('workbench-mapping-bridge-preview'));
    await waitFor(() => {
      expect(screen.getByText('preview-boom')).toBeInTheDocument();
    });

    previewMock.mockRejectedValueOnce('raw');
    fireEvent.click(screen.getByTestId('workbench-mapping-bridge-preview'));
    await waitFor(() => {
      expect(screen.getByText('Unknown error')).toBeInTheDocument();
    });
  });

  it('shows list load errors and skips preview when empty', async () => {
    listMock.mockResolvedValueOnce({ items: [] });
    const { unmount } = render(<WorkbenchMappingBridge accessToken="tok" />);
    await waitFor(() => {
      expect(
        screen.getByTestId('workbench-mapping-bridge-preview'),
      ).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('workbench-mapping-bridge-preview'));
    expect(previewMock).not.toHaveBeenCalled();
    unmount();

    listMock.mockRejectedValueOnce(new Error('list-fail'));
    render(<WorkbenchMappingBridge accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText('list-fail')).toBeInTheDocument();
    });
  });

  it('shows Unknown error when template list rejects a non-Error', async () => {
    listMock.mockRejectedValueOnce('nope');
    render(<WorkbenchMappingBridge accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText('Unknown error')).toBeInTheDocument();
    });
  });
});
