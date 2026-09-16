/**
 * Vitest for LibraryDraftShell (EVPYL Phase A / C).
 */

import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';

import { LibraryDraftShell } from './LibraryDraftShell';

const createLibraryAsset = vi.fn();
const updateLibraryAsset = vi.fn();

vi.mock('../../utils/conversionProfilesApi', async (importOriginal) => {
  const actual =
    await importOriginal<typeof import('../../utils/conversionProfilesApi')>();
  return {
    ...actual,
    createLibraryAsset: (...args: unknown[]) => createLibraryAsset(...args),
    updateLibraryAsset: (...args: unknown[]) => updateLibraryAsset(...args),
  };
});

describe('LibraryDraftShell', () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('renders draft shell with block skeleton for conversion kind', () => {
    render(<LibraryDraftShell kind="conversion" />);

    expect(screen.getByTestId('library-draft-shell-conversion')).toBeInTheDocument();
    expect(screen.getByTestId('library-draft-blocks-conversion')).toBeInTheDocument();
    expect(
      screen.getByTestId('library-draft-block-observation-conversion'),
    ).toBeInTheDocument();
    expect(
      screen.getByTestId('library-draft-block-cloud-conversion'),
    ).toBeInTheDocument();
    expect(
      screen.getByTestId('library-draft-block-rvr-conversion'),
    ).toBeInTheDocument();
    expect(screen.getByTestId('library-draft-status-conversion')).toHaveTextContent(
      /Not saved/i,
    );
  });

  it('renders mined schema blocks when provided', () => {
    render(
      <LibraryDraftShell
        kind="conversion"
        schemaBlocks={[
          {
            id: 'obs',
            label: 'Observation block',
            cards: [{ id: 'wind', label: 'Wind card' }],
          },
        ]}
      />,
    );
    expect(
      screen.getByTestId('library-draft-block-obs-conversion'),
    ).toBeInTheDocument();
    expect(screen.getByText('Wind card')).toBeInTheDocument();
  });

  it('loads template yaml and saves draft locally', async () => {
    const user = userEvent.setup();
    render(<LibraryDraftShell kind="tac_validation" />);

    await user.click(screen.getByTestId('library-draft-new-template-tac_validation'));
    expect(screen.getByTestId('library-draft-yaml-tac_validation')).toHaveValue(
      `# TAC validation draft
kind: tac_validation
name: New TAC validation draft
rules:
  - pattern: "(?P<wind>\\\\d{5})KT"
    sample: "18004KT"
`,
    );
    expect(screen.getByTestId('library-draft-status-tac_validation')).toHaveTextContent(
      /Draft/i,
    );

    await user.click(screen.getByTestId('library-draft-save-tac_validation'));
    expect(screen.getByTestId('library-draft-status-tac_validation')).toHaveTextContent(
      /Draft saved/i,
    );

    expect(
      screen.getByTestId('library-draft-activate-tac_validation'),
    ).not.toBeDisabled();
    await user.click(screen.getByTestId('library-draft-activate-tac_validation'));
    expect(screen.getByTestId('library-draft-status-tac_validation')).toHaveTextContent(
      /Activated/i,
    );
  });

  it('duplicates built-in yaml into the editor', async () => {
    const user = userEvent.setup();
    render(<LibraryDraftShell kind="decoding" sourceAssetName="ICAO decode set" />);

    await user.click(screen.getByTestId('library-draft-duplicate-decoding'));
    const yaml = screen.getByTestId(
      'library-draft-yaml-decoding',
    ) as HTMLTextAreaElement;
    expect(yaml.value).toContain('ICAO decode set');
    expect(yaml.value).toContain('kind: decoding');
  });

  it('locks activate on invalid YAML and shows diagnostics for fail patterns', async () => {
    const user = userEvent.setup();
    render(<LibraryDraftShell kind="tac_validation" />);
    const editor = screen.getByTestId('library-draft-yaml-tac_validation');
    await user.clear(editor);
    await user.paste('name: only');
    expect(screen.getByTestId('library-draft-activate-tac_validation')).toBeDisabled();
    expect(
      screen.getByTestId('library-draft-yaml-lock-tac_validation'),
    ).toBeInTheDocument();
  });

  it('updates the sample drawer and uses a fallback name when saving nameless YAML', async () => {
    const user = userEvent.setup();
    const onDraftStatusChange = vi.fn();
    render(
      <LibraryDraftShell
        kind="conversion"
        accessToken="tok"
        onDraftStatusChange={onDraftStatusChange}
      />,
    );

    const sample = screen.getByTestId('library-draft-sample-input-conversion');
    await user.type(sample, '18004KT');
    expect(sample).toHaveValue('18004KT');

    const editor = screen.getByTestId('library-draft-yaml-conversion');
    // No name line → yamlName falls back to "New conversion draft".
    fireEvent.change(editor, {
      target: { value: 'kind: conversion\nrules: []\n' },
    });

    createLibraryAsset.mockResolvedValueOnce({
      id: 'asset-1',
      kind: 'conversion',
      name: 'New conversion draft',
      access: 'custom',
      engineProfileId: 'ICAO_2025',
      attachedNationalLine: 'ICAO_2025',
      status: 'draft',
    });

    await user.click(screen.getByTestId('library-draft-save-conversion'));
    await waitFor(() => {
      expect(createLibraryAsset).toHaveBeenCalledWith(
        'tok',
        expect.objectContaining({
          name: 'New conversion draft',
          kind: 'conversion',
          status: 'draft',
        }),
      );
    });
    expect(screen.getByTestId('library-draft-status-conversion')).toHaveTextContent(
      /Draft saved/i,
    );
    expect(onDraftStatusChange).toHaveBeenCalledWith('saved');
  });

  it('strips quotes from the YAML name when persisting', async () => {
    const user = userEvent.setup();
    createLibraryAsset.mockResolvedValueOnce({
      id: 'asset-quoted',
      kind: 'conversion',
      name: 'Quoted Wind',
      access: 'custom',
      engineProfileId: 'ICAO_2025',
      attachedNationalLine: 'ICAO_2025',
      status: 'draft',
    });
    render(<LibraryDraftShell kind="conversion" accessToken="tok" />);
    fireEvent.change(screen.getByTestId('library-draft-yaml-conversion'), {
      target: { value: 'kind: conversion\nname: "Quoted Wind"\nrules: []\n' },
    });
    await user.click(screen.getByTestId('library-draft-save-conversion'));
    await waitFor(() => {
      expect(createLibraryAsset).toHaveBeenCalledWith(
        'tok',
        expect.objectContaining({ name: 'Quoted Wind' }),
      );
    });
  });

  it('creates then updates a library asset when accessToken is present', async () => {
    const user = userEvent.setup();
    createLibraryAsset.mockResolvedValueOnce({
      id: 'asset-1',
      kind: 'tac_validation',
      name: 'New TAC validation draft',
      access: 'custom',
      engineProfileId: 'ICAO_2025',
      attachedNationalLine: 'ICAO_2025',
      status: 'draft',
    });
    updateLibraryAsset.mockResolvedValueOnce({
      id: 'asset-1',
      kind: 'tac_validation',
      name: 'New TAC validation draft',
      access: 'custom',
      engineProfileId: 'ICAO_2025',
      attachedNationalLine: 'ICAO_2025',
      status: 'activated',
    });

    render(<LibraryDraftShell kind="tac_validation" accessToken="tok" />);
    await user.click(screen.getByTestId('library-draft-new-template-tac_validation'));
    await user.click(screen.getByTestId('library-draft-save-tac_validation'));

    await waitFor(() => {
      expect(createLibraryAsset).toHaveBeenCalledTimes(1);
    });

    await user.click(screen.getByTestId('library-draft-activate-tac_validation'));
    await waitFor(() => {
      expect(updateLibraryAsset).toHaveBeenCalledWith(
        'tok',
        'asset-1',
        expect.objectContaining({ status: 'activated' }),
      );
    });
    expect(screen.getByTestId('library-draft-status-tac_validation')).toHaveTextContent(
      /Activated/i,
    );
  });

  it('surfaces persist errors from the API', async () => {
    const user = userEvent.setup();
    createLibraryAsset.mockRejectedValueOnce(new Error('server down'));
    render(<LibraryDraftShell kind="decoding" accessToken="tok" />);
    await user.click(screen.getByTestId('library-draft-new-template-decoding'));
    await user.click(screen.getByTestId('library-draft-save-decoding'));
    await waitFor(() => {
      expect(screen.getByText('server down')).toBeInTheDocument();
    });
  });

  it('surfaces a generic persist error for non-Error rejections', async () => {
    const user = userEvent.setup();
    createLibraryAsset.mockRejectedValueOnce('nope');
    render(<LibraryDraftShell kind="dissemination" accessToken="tok" />);
    await user.click(screen.getByTestId('library-draft-new-template-dissemination'));
    await user.click(screen.getByTestId('library-draft-save-dissemination'));
    await waitFor(() => {
      expect(screen.getByText('Save failed')).toBeInTheDocument();
    });
  });

  it('ignores save/activate when yaml is empty or activation is locked', async () => {
    const user = userEvent.setup();
    render(<LibraryDraftShell kind="conversion" />);

    // Empty editor: Save stays disabled (primary gate).
    expect(screen.getByTestId('library-draft-save-conversion')).toBeDisabled();

    await user.click(screen.getByTestId('library-draft-duplicate-conversion'));
    const editor = screen.getByTestId('library-draft-yaml-conversion');
    await user.clear(editor);
    await user.paste(`kind: tac_validation
name: Bad
rules:
  - pattern: "(unclosed"
`);
    expect(
      screen.getByTestId('library-draft-activate-blocked-conversion'),
    ).toBeInTheDocument();
    expect(screen.getByTestId('library-draft-activate-conversion')).toBeDisabled();
  });

  it('shows capture names for matching sample diagnostics', async () => {
    const user = userEvent.setup();
    render(<LibraryDraftShell kind="tac_validation" />);
    await user.click(screen.getByTestId('library-draft-new-template-tac_validation'));
    await user.type(
      screen.getByTestId('library-draft-sample-input-tac_validation'),
      '18004KT',
    );
    await waitFor(() => {
      expect(
        screen.getByTestId('library-draft-diagnostics-tac_validation'),
      ).toHaveTextContent(/Captures|wind/i);
    });
  });
});
