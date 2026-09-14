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

const windItem = {
  id: 'CV.WIND',
  slug: 'CV.WIND',
  name: 'Wind group',
  access: 'first_party' as const,
  iwxxmBlock: 'iwxxm:WindObservation',
  slots: [
    {
      id: 'ddd',
      label: 'direction',
      type: 'digits',
      digits: 3,
      iwxxmField: 'direction',
    },
    { id: 'ff', label: 'speed', type: 'digits', digits: 2 },
  ],
  sample: '18012G20KT',
};

const customItem = {
  id: 'custom-1',
  slug: 'my-wind',
  name: 'My wind',
  access: 'custom' as const,
  iwxxmBlock: 'iwxxm:WindObservation',
  slots: [{ id: 'ddd', label: 'direction', type: 'digits', digits: 3 }],
  sample: '18012KT',
  forkOf: 'CV.WIND',
};

describe('ConversionTemplatesPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    listMock.mockResolvedValue({ items: [windItem] });
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

  it('reorders with keyboard buttons and drag-drop', async () => {
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-move-down')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-templates-move-down'));
    fireEvent.click(screen.getByTestId('conversion-templates-move-up'));
    const first = screen.getByTestId('conversion-template-slot-ddd');
    const second = screen.getByTestId('conversion-template-slot-ff');
    fireEvent.dragStart(first);
    fireEvent.dragOver(second);
    fireEvent.drop(second);
    expect(first).toBeInTheDocument();
  });

  it('updates focus and comments fields', async () => {
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-focus')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-templates-focus'), {
      target: { value: '27015KT' },
    });
    fireEvent.change(screen.getByTestId('conversion-templates-comments'), {
      target: { value: 'operator note' },
    });
    expect(screen.getByTestId('conversion-templates-focus')).toHaveValue('27015KT');
    expect(screen.getByTestId('conversion-templates-comments')).toHaveValue(
      'operator note',
    );
  });

  it('shows empty state and load errors', async () => {
    listMock.mockResolvedValueOnce({ items: [] });
    const { unmount } = render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByText(/No conversion tokens/i)).toBeInTheDocument();
    });
    unmount();

    listMock.mockRejectedValueOnce(new Error('boom'));
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-error')).toHaveTextContent(
        'boom',
      );
    });
  });

  it('sets token mode to Skip and shows skip chip without machine ids in select', async () => {
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-select')).toBeInTheDocument();
    });
    const select = screen.getByTestId('conversion-templates-select');
    expect(select).toHaveTextContent(/Wind group/);
    expect(select).not.toHaveTextContent('CV.WIND');
    fireEvent.change(screen.getByTestId('conversion-template-slot-mode-ddd'), {
      target: { value: 'skip' },
    });
    fireEvent.change(screen.getByTestId('conversion-template-slot-gloss-ddd'), {
      target: { value: 'etc.' },
    });
    expect(screen.getByTestId('conversion-templates-skip-chips')).toHaveTextContent(
      'Skipped',
    );
    const advanced = screen.getByTestId('conversion-templates-advanced');
    expect(advanced).toBeInTheDocument();
    fireEvent(advanced, new Event('toggle', { bubbles: true }));
  });

  it('shows API skipped chips and compiled pattern after preview', async () => {
    previewMock.mockResolvedValue({
      templateId: 'CV.WIND',
      focusGroup: '18012G20KT',
      matched: true,
      captures: [],
      xmlBlock: '<iwxxm:WindObservation/>',
      compiledPattern: '{ddd}{ff}',
      skipped: [
        { slot: 'noise', label: 'residual', gloss: 'etc.' },
        { slot: 'only-id', label: '', gloss: '' },
        { slot: '', label: 'label-only', gloss: '' },
        { slot: '', label: '', gloss: '' },
      ],
    });
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-preview')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-templates-preview'));
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-skip-chips')).toHaveTextContent(
        'residual',
      );
    });
    expect(screen.getByTestId('conversion-templates-skip-chips')).toHaveTextContent(
      'only-id',
    );
    expect(
      screen.getByTestId('conversion-templates-advanced-pattern'),
    ).toHaveTextContent('{ddd}{ff}');
  });

  it('falls back when slot mode and gloss are unset', async () => {
    listMock.mockResolvedValue({
      items: [
        {
          ...windItem,
          slots: [{ id: 'bare', label: 'bare', type: 'digits', digits: 2 }],
        },
      ],
    });
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-template-slot-mode-bare')).toHaveValue(
        'convert',
      );
    });
    fireEvent.change(screen.getByTestId('conversion-template-slot-mode-bare'), {
      target: { value: 'skip' },
    });
    expect(screen.getByTestId('conversion-templates-skip-chips')).toHaveTextContent(
      'bare',
    );
  });

  it('handles preview and fork failures and custom forkOf', async () => {
    listMock.mockResolvedValue({ items: [customItem, windItem] });
    previewMock.mockRejectedValueOnce(new Error('preview broke'));
    createMock.mockRejectedValueOnce(new Error('fork broke'));
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-select')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-templates-select'), {
      target: { value: 'custom-1' },
    });
    fireEvent.click(screen.getByTestId('conversion-templates-preview'));
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-error')).toHaveTextContent(
        'preview broke',
      );
    });
    fireEvent.click(screen.getByTestId('conversion-templates-fork'));
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-error')).toHaveTextContent(
        'fork broke',
      );
    });
  });

  it('covers non-Error failures, empty select, and null drag drop', async () => {
    listMock.mockRejectedValueOnce('string-fail');
    const { unmount } = render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-error')).toHaveTextContent(
        'Failed to load templates',
      );
    });
    unmount();

    listMock.mockResolvedValue({ items: [windItem, customItem] });
    previewMock.mockRejectedValueOnce('preview-string');
    createMock.mockRejectedValueOnce('fork-string');
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-select')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-templates-select'), {
      target: { value: 'missing' },
    });
    fireEvent.drop(screen.getByTestId('conversion-template-slot-ddd'));
    fireEvent.click(screen.getByTestId('conversion-templates-preview'));
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-error')).toHaveTextContent(
        'Preview failed',
      );
    });
    fireEvent.click(screen.getByTestId('conversion-templates-fork'));
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-error')).toHaveTextContent(
        'Fork failed',
      );
    });
  });

  it('forks custom with comments and forkOf fallback', async () => {
    listMock.mockResolvedValue({
      items: [{ ...customItem, forkOf: undefined }],
    });
    createMock.mockResolvedValue({
      id: 'new',
      slug: 'fork-x',
      name: 'My wind (custom)',
      access: 'custom',
      iwxxmBlock: 'iwxxm:WindObservation',
      slots: [],
    });
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-comments')).toBeInTheDocument();
    });
    fireEvent.change(screen.getByTestId('conversion-templates-comments'), {
      target: { value: 'keep' },
    });
    fireEvent.click(screen.getByTestId('conversion-templates-fork'));
    await waitFor(() => {
      expect(createMock).toHaveBeenCalledWith(
        'tok',
        expect.objectContaining({
          comments: 'keep',
          forkOf: 'custom-1',
        }),
      );
    });
  });

  it('renders unmatched preview branch', async () => {
    previewMock.mockResolvedValue({
      templateId: 'CV.WIND',
      focusGroup: 'x',
      matched: false,
      captures: [],
      xmlBlock: '<!-- none -->',
      compiledPattern: '',
    });
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-preview')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-templates-preview'));
    await waitFor(() => {
      expect(
        screen.getByTestId('conversion-templates-preview-result'),
      ).toHaveTextContent('Matched: no');
    });
  });

  it('no-ops move when slots are empty', async () => {
    listMock.mockResolvedValue({
      items: [{ ...windItem, slots: [] }],
    });
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-move-down')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByTestId('conversion-templates-move-down'));
    fireEvent.click(screen.getByTestId('conversion-templates-move-up'));
    expect(screen.getByTestId('conversion-templates-slots')).toBeInTheDocument();
  });

  it('applies defaults when slots/sample are missing', async () => {
    listMock.mockResolvedValue({
      items: [
        {
          id: 'bare',
          slug: 'bare',
          name: 'Bare',
          access: 'first_party',
          iwxxmBlock: 'iwxxm:WindObservation',
          slots: undefined as unknown as [],
          sample: '',
        },
      ],
    });
    render(<ConversionTemplatesPanel accessToken="tok" />);
    await waitFor(() => {
      expect(screen.getByTestId('conversion-templates-focus')).toHaveValue(
        '18012G20KT',
      );
    });
  });
});
