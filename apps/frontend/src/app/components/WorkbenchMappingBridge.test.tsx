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

describe('WorkbenchMappingBridge', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({
      items: [
        {
          id: 'CV.WIND',
          slug: 'CV.WIND',
          name: 'Wind group',
          access: 'first_party',
          iwxxmBlock: 'iwxxm:WindObservation',
          slots: [],
          sample: '18012G20KT',
        },
      ],
    });
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
});
