/**
 * Vitest for LibraryDraftShell (EVPYL Phase A).
 */

import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it } from 'vitest';
import { LibraryDraftShell } from './LibraryDraftShell';

describe('LibraryDraftShell', () => {
  afterEach(() => {
    cleanup();
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

  it('loads template yaml and saves draft locally', async () => {
    const user = userEvent.setup();
    render(<LibraryDraftShell kind="tac_validation" />);

    await user.click(screen.getByTestId('library-draft-new-template-tac_validation'));
    expect(screen.getByTestId('library-draft-yaml-tac_validation')).toHaveValue(
      `# TAC validation draft
kind: tac_validation
name: New TAC validation draft
rules: []
`,
    );
    expect(screen.getByTestId('library-draft-status-tac_validation')).toHaveTextContent(
      /Draft/i,
    );

    await user.click(screen.getByTestId('library-draft-save-tac_validation'));
    expect(screen.getByTestId('library-draft-status-tac_validation')).toHaveTextContent(
      /Draft saved locally/i,
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
});
