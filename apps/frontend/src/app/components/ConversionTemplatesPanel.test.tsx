/**
 * Tests for ConversionTemplatesPanel (UJ-072e / TC-EV080 FE).
 */

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, expect, it, vi, beforeEach } from 'vitest';

import { ConversionTemplatesPanel } from './ConversionTemplatesPanel';

vi.mock('../../utils/conversionProfilesApi', () => ({
  listConversionTemplates: vi.fn(),
  previewConversionTemplate: vi.fn(),
  createConversionTemplate: vi.fn(),
}));

import {
  createConversionTemplate,
  listConversionTemplates,
  previewConversionTemplate,
} from '../../utils/conversionProfilesApi';

const listMock = vi.mocked(listConversionTemplates);
const previewMock = vi.mocked(previewConversionTemplate);
const createMock = vi.mocked(createConversionTemplate);

describe('ConversionTemplatesPanel', () => {
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
          slots: [
            { id: 'ddd', label: 'direction', type: 'digits', digits: 3 },
            { id: 'ff', label: 'speed', type: 'digits', digits: 2 },
          ],
          sample: '18012G20KT',
        },
      ],
    });
  });

  it('loads templates and previews mapping', async () => {
    previewMock.mockResolvedValue({
      templateId: 'CV.WIND',
      focusGroup: '18012G20KT',
      matched: true,
      captures: [],
      xmlBlock: '<iwxxm:WindObservation/>',
      compiledPattern: '{ddd}',
    });
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-select')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-templates-preview'));
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-templates-preview-result'),
      ).toHaveTextContent('WindObservation');
    });
  });

  it('forks a first-party template', async () => {
    createMock.mockResolvedValue({
      id: 'new',
      slug: 'fork-x',
      name: 'Wind group (custom)',
      access: 'custom',
      iwxxmBlock: 'iwxxm:WindObservation',
      slots: [],
    });
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-fork')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-templates-fork'));
    await waitFor(() => {
      expect(createMock).toHaveBeenCalled();
    });
  });

  it('reorders with keyboard buttons', async () => {
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-move-down')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-templates-move-down'));
    fireEvent.click(screen.getByTestId('conversion-templates-move-up'));
    expect(screen.getByTestId('conversion-template-slot-ddd')).toBeInTheDocument();
  });
});
