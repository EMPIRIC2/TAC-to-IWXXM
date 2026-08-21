/**
 * T2.7 smoke — TacEditor mounts a CodeMirror host.
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { useState } from 'react';

vi.mock('codemirror', () => {
  class FakeEditorView {
    static lineWrapping = {};
    static updateListener = { of: () => ({}) };
    static editable = { of: () => ({}) };
    static contentAttributes = { of: () => ({}) };
    static theme = () => ({});
    state = { doc: { toString: () => '', length: 0 } };
    contentDOM: HTMLElement;
    constructor(config?: { parent?: HTMLElement | null }) {
      this.contentDOM = document.createElement('div');
      this.contentDOM.contentEditable = 'true';
      this.contentDOM.setAttribute('aria-label', 'Enter TAC data manually');
      this.contentDOM.id = 'manual-input';
      config?.parent?.appendChild(this.contentDOM);
    }
    dispatch() {
      /* no-op */
    }
    destroy() {
      /* no-op */
    }
  }
  return { EditorView: FakeEditorView, basicSetup: [] };
});

vi.mock('@codemirror/state', () => ({
  EditorState: {
    create: () => ({}),
    readOnly: { of: () => ({}) },
  },
  StateEffect: { define: () => ({ of: (v: unknown) => v }) },
  StateField: {
    define: () => ({}),
  },
}));

vi.mock('/utils/tacEditorSpans', () => ({
  setTacSpansEffect: { of: (v: unknown) => v },
  tacSpanExtensions: () => [],
}));

import { TacEditor } from './TacEditor';

describe('TacEditor', () => {
  it('renders the CodeMirror host container', () => {
    render(
      <TacEditor
        value="METAR KJFK="
        onChange={() => undefined}
        aria-label="TAC editor"
      />,
    );
    expect(screen.getByTestId('tac-editor')).toBeInTheDocument();
  });

  it('exposes issue span count for live workbench highlights', () => {
    render(
      <TacEditor
        value="METAR KJFK="
        onChange={() => undefined}
        issueSpans={[{ start: 0, end: 5, message: 'type' }]}
      />,
    );
    expect(screen.getByTestId('tac-editor')).toHaveAttribute(
      'data-issue-span-count',
      '1',
    );
  });

  it('syncs contentDOM aria-label when the prop changes (UJ-058 / EV-057)', () => {
    function Harness() {
      const [label, setLabel] = useState('Enter METAR data manually');
      return (
        <div>
          <button type="button" onClick={() => setLabel('Enter IWXXM XML manually')}>
            switch-validate
          </button>
          <TacEditor value="<root/>" onChange={() => undefined} aria-label={label} />
        </div>
      );
    }

    render(<Harness />);
    expect(screen.getByLabelText('Enter METAR data manually')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'switch-validate' }));
    expect(screen.getByLabelText('Enter IWXXM XML manually')).toBeInTheDocument();
  });
});
